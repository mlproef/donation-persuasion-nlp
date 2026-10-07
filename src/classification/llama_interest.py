"""
Task 2: classify how interested the persuadee is in donating (Not Interested / Neutral / Interested).
Sends one LLM request per dialog via Ollama, so the model sees the full conversation context.

Usage:
    python src/classification/llama_interest.py

What it does:
    1. Loads data/raw/full_dialog.csv
    2. Groups by dialogs (B2)
    3. For each dialog, finds all target messages (B4=1)
    4. Sends batch request to Ollama to analyze all target messages in the dialog
    5. Determines interest: 0 (refusal), 1 (neutral), 2 (interested)
    6. Saves results to data/interim/test_batch_interest_results.csv

Results:
    - interest_ollama: category name ("Not Interested", "Neutral", or "Interested")
    - interest_label_ollama: numeric label (0, 1, or 2)

Settings:
    - OLLAMA_URL: Ollama server URL (default: http://localhost:11434/api/chat, override with the OLLAMA_URL environment variable)
    - OLLAMA_MODEL: Ollama model (default: gpt-oss:20b, override with the OLLAMA_MODEL environment variable)
    - REQUEST_TIMEOUT: request timeout in seconds (default: 600)
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import FULL_DIALOG, INTEREST_RESULTS  # noqa: E402

import pandas as pd
import requests
import json
import os
import re
import time
from tqdm import tqdm
import sys

# Interest category structure (embedded in file)
INTEREST_CATEGORIES = {
    "refusal": {
        "name": "Not Interested",
        "label": 0,
        "definition": "The person refuses to donate money or is not interested in donating.",
        "hypothesis": "The person refuses to donate any money or is not interested in donating.",
        "markers": ["no", "don't", "won't", "refuse", "not going to", "can't", "sorry", "unfortunately", "can't afford", "not interested"]
    },
    "neutral": {
        "name": "Neutral",
        "label": 1,
        "definition": "The person neither agrees nor refuses, showing neutral response.",
        "hypothesis": "The person responds neutrally to the donation request, neither expressing clear interest nor refusal.",
        "markers": ["what", "who", "how", "ok", "I see", "understand", "maybe"]
    },
    "interested": {
        "name": "Interested",
        "label": 2,
        "definition": "The person expresses interest in donating or agrees to donate.",
        "hypothesis": "The person expresses interest in donating money or agrees to donate.",
        "markers": ["yes", "I will", "I'll donate", "sure", "how do I", "where do I", "that's great", "sounds good", "I'd like to", "I want to"]
    }
}

# For backward compatibility
INTEREST_INFO = [
    {
        "name": "Not Interested",
        "label": 0,
        "parent_id": "refusal",
        "hypothesis": INTEREST_CATEGORIES["refusal"]["hypothesis"]
    },
    {
        "name": "Neutral",
        "label": 1,
        "parent_id": "neutral",
        "hypothesis": INTEREST_CATEGORIES["neutral"]["hypothesis"]
    },
    {
        "name": "Interested",
        "label": 2,
        "parent_id": "interested",
        "hypothesis": INTEREST_CATEGORIES["interested"]["hypothesis"]
    }
]

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
REQUEST_TIMEOUT = 600  # Increased timeout for batch requests (10 minutes)

# Load data
print("Loading data...")
# Try to load existing results if they exist
if os.path.exists(str(INTEREST_RESULTS)):
    print("   Found results file, loading it...")
    df = pd.read_csv(str(INTEREST_RESULTS))
    # Create columns for interest (new columns with _v2 suffix) if they don't exist
    if "interest_ollama_v2" not in df.columns:
        df["interest_ollama_v2"] = None
    if "interest_label_ollama_v2" not in df.columns:
        df["interest_label_ollama_v2"] = None
    # Restore empty strings to NaN for proper checking (new _v2 columns)
    df["interest_ollama_v2"] = df["interest_ollama_v2"].replace("", pd.NA)
    df["interest_label_ollama_v2"] = df["interest_label_ollama_v2"].replace("", pd.NA)
else:
    print("   Results file not found, loading source data...")
    df = pd.read_csv(str(FULL_DIALOG))
    # Create columns for interest (new columns with _v2 suffix)
    if "interest_ollama_v2" not in df.columns:
        df["interest_ollama_v2"] = None
    if "interest_label_ollama_v2" not in df.columns:
        df["interest_label_ollama_v2"] = None

df = df.sort_values(["B2", "Turn"]).reset_index(drop=True)

# Group by dialogs
groups = df.groupby("B2", sort=False)

print(f"Total dialogs: {len(groups)}")
print(f"Starting processing...\n")

# Prepare data for prompt (same for all dialogs)

# List of all interest categories (only 3 categories)
categories_list = "\n".join([
    f"- {cat_info['label']}: {cat_info['name']} - {cat_info['definition']}"
    for cat_id, cat_info in sorted(INTEREST_CATEGORIES.items(), key=lambda x: x[1]['label'])
])

# List of all categories for JSON response
all_category_names = [cat_info['name'] for cat_info in INTEREST_CATEGORIES.values()]
category_names_list = ", ".join(all_category_names)

# List of labels for quick access
label_mapping = {cat_info['name']: cat_info['label'] for cat_info in INTEREST_CATEGORIES.values()}

# Process each dialog

processed_dialogs = 0
total_processed = 0

for dialog_id, dialog_group in tqdm(groups, desc="Processing dialogs"):
    # Save original_index
    dialog_group = dialog_group.copy()
    dialog_group["original_index"] = dialog_group.index
    dialog_group = dialog_group.sort_values("Turn").reset_index(drop=True)
    
    # Find all target messages (B4=1) in dialog
    target_rows = []
    for idx, row in dialog_group.iterrows():
        b4_value = row["B4"]
        if b4_value == 1 or str(b4_value) == "1":
            original_idx = row.get("original_index", idx)
            # Skip already processed messages (check new _v2 columns)
            # Check column existence and value
            if "interest_ollama_v2" in df.columns:
                interest_value = df.at[original_idx, "interest_ollama_v2"]
                if pd.notna(interest_value) and str(interest_value).strip() != "":
                    continue
            target_rows.append((original_idx, row))
    
    # If no messages to process, skip dialog
    if not target_rows:
        continue
    
    # Build list of target messages for analysis with context from 2 previous messages
    # IMPORTANT: create mapping message_number -> original_idx only for non-empty messages
    target_messages_list = []
    message_number_to_original_idx = {}  # Mapping: message number in prompt -> original_idx
    
    # Create dictionary for quick access: Turn -> index in dialog_group
    turn_to_index = {}
    for idx, row in dialog_group.iterrows():
        turn = row.get("Turn")
        if turn is not None:
            turn_to_index[turn] = idx
    
    # Counter only for non-empty messages
    message_num = 0
    
    for local_idx, (original_idx, row) in enumerate(target_rows):
        message = str(row["Unit"]) if isinstance(row["Unit"], str) else ""
        if not message.strip():
            # Skip empty messages, but don't increment counter
            continue
        
        # Increment counter only for non-empty messages
        message_num += 1
        
        # Save mapping: message_number -> original_idx
        message_number_to_original_idx[message_num] = original_idx
        
        # Find position of this message in sorted dialog by Turn
        target_turn = row.get("Turn")
        target_idx_in_dialog = turn_to_index.get(target_turn)
        
        # Build context from 2 previous messages
        context_messages = []
        if target_idx_in_dialog is not None and target_idx_in_dialog > 0:
            context_start = max(0, target_idx_in_dialog - 2)
            for ctx_idx in range(context_start, target_idx_in_dialog):
                ctx_row = dialog_group.iloc[ctx_idx]
                speaker = "Persuader" if (ctx_row["B4"] == 0 or str(ctx_row["B4"]) == "0") else "Target"
                text = str(ctx_row["Unit"]) if isinstance(ctx_row["Unit"], str) else ""
                turn = ctx_row.get("Turn", ctx_idx)
                if text.strip():
                    context_messages.append(f"Turn {turn} - {speaker}: {text}")
        
        context_text = "\n".join(context_messages) if context_messages else "No previous messages."
        
        # Use message_num (starts at 1) for numbering in prompt
        target_messages_list.append(f"Message #{message_num}:\n  Context (last 2 messages):\n{context_text}\n  Message: {message}")
    
    target_messages_text = "\n".join(target_messages_list)
    
    # Build prompt (use count of non-empty messages)
    num_valid_messages = len(message_number_to_original_idx)
    prompt = f"""Analyze {num_valid_messages} target user messages and determine their interest in donating.

INTEREST LEVELS (only 3 options):
- 0: Not Interested - The person refuses to donate or is not interested
- 1: Neutral - The person neither agrees nor refuses, shows neutral response
- 2: Interested - The person expresses interest in donating or agrees to donate

MESSAGES TO ANALYZE (each with context from last 2 previous messages):
{target_messages_text}

TASK:
For each target message above, determine the interest level. Return ONLY a number: 0, 1, or 2.

You may think about it, but you MUST end your response with a valid JSON object.

OUTPUT FORMAT (STRICT — NO EXTRA TEXT):
Return ONLY the following format:

BEGIN_JSON
{{"Message #1": 0, "Message #2": 1, "Message #3": 2}}
END_JSON

IMPORTANT:
- Return ONLY numbers: 0, 1, or 2
- 0 = Not Interested (refuses or not interested)
- 1 = Neutral (neither agrees nor refuses)
- 2 = Interested (expresses interest or agrees)
- Do NOT include explanations, reasoning, or any other text outside BEGIN_JSON / END_JSON
- JSON must be between BEGIN_JSON and END_JSON markers

EXAMPLE OUTPUT:
BEGIN_JSON
{{"Message #1": 0, "Message #2": 1, "Message #3": 2}}
END_JSON

Now analyze the messages and return the JSON:"""

    messages = [
        {
            "role": "system",
            "content": "You are an interest classification system for donation requests. You may think about the analysis, but you MUST complete your response with a valid JSON object containing only numbers (0=Not Interested, 1=Neutral, 2=Interested) for each message. The JSON must be complete and valid. Do not stop generating until the JSON object is finished."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    # Send request
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 8000,
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT, stream=True)
        response.raise_for_status()
        
        # Collect all response parts
        full_content = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        full_content += chunk["message"]["content"]
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
        
        # Parse JSON - search between BEGIN_JSON and END_JSON
        result = {}
        
        # First try to find JSON between markers
        begin_marker = "BEGIN_JSON"
        end_marker = "END_JSON"
        begin_idx = full_content.find(begin_marker)
        end_idx = full_content.find(end_marker)
        
        parsed_successfully = False
        
        if begin_idx != -1 and end_idx != -1 and end_idx > begin_idx:
            # Extract JSON between markers
            json_str = full_content[begin_idx + len(begin_marker):end_idx].strip()
            try:
                parsed_json = json.loads(json_str)
                parsed_successfully = True
                
                # Process all keys from JSON
                for key, value in parsed_json.items():
                    match = re.match(r'Message\s*#(\d+)', key, re.IGNORECASE)
                    if match:
                        msg_num = int(match.group(1))
                        # Use mapping message_number -> original_idx
                        if msg_num in message_number_to_original_idx:
                            original_idx = message_number_to_original_idx[msg_num]
                            
                            # Process different response formats
                            if isinstance(value, int):
                                # Simple format - number only
                                label = value
                                # Check that label is in valid range
                                if label not in [0, 1, 2]:
                                    label = 1  # Default to neutral
                                
                                # Determine category by label
                                category = None
                                for cat_id, cat_info in INTEREST_CATEGORIES.items():
                                    if cat_info["label"] == label:
                                        category = cat_info["name"]
                                        break
                                
                                result[original_idx] = {
                                    "label": label,
                                    "category": category
                                }
                            elif isinstance(value, dict):
                                # Old format with dict - extract label
                                label = value.get("label")
                                if label is None:
                                    label = 1  # Default to neutral
                                if label not in [0, 1, 2]:
                                    label = 1
                                
                                category = value.get("category")
                                if not category:
                                    # Determine category by label
                                    for cat_id, cat_info in INTEREST_CATEGORIES.items():
                                        if cat_info["label"] == label:
                                            category = cat_info["name"]
                                            break
                                
                                result[original_idx] = {
                                    "label": label,
                                    "category": category
                                }
                            elif isinstance(value, str):
                                # This could be category name or number as string
                                try:
                                    label = int(value)
                                    if label not in [0, 1, 2]:
                                        label = 1
                                except ValueError:
                                    # This is category name
                                    label = label_mapping.get(value, 1)
                                
                                # Determine category
                                category = value if value in label_mapping else None
                                if not category:
                                    for cat_id, cat_info in INTEREST_CATEGORIES.items():
                                        if cat_info["label"] == label:
                                            category = cat_info["name"]
                                            break
                                
                                result[original_idx] = {
                                    "label": label,
                                    "category": category
                                }
            except json.JSONDecodeError:
                pass
        
        # Fallback: if markers not found, try regular JSON search
        if not parsed_successfully and not result:
            json_start = full_content.find('{')
            json_end = full_content.rfind('}')
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                for attempt_end in range(json_end, json_start, -1):
                    try:
                        json_str = full_content[json_start:attempt_end+1]
                        parsed_json = json.loads(json_str)
                        parsed_successfully = True
                        
                        # Process all keys from JSON
                        for key, value in parsed_json.items():
                            match = re.match(r'Message\s*#(\d+)', key, re.IGNORECASE)
                            if match:
                                msg_num = int(match.group(1))
                                # Use mapping message_number -> original_idx
                                if msg_num in message_number_to_original_idx:
                                    original_idx = message_number_to_original_idx[msg_num]
                                    
                                    # Process different response formats
                                    if isinstance(value, int):
                                        # Simple format - number only
                                        label = value
                                        # Check that label is in valid range
                                        if label not in [0, 1, 2]:
                                            label = 1  # Default to neutral
                                        
                                        # Determine category by label
                                        category = None
                                        for cat_id, cat_info in INTEREST_CATEGORIES.items():
                                            if cat_info["label"] == label:
                                                category = cat_info["name"]
                                                break
                                        
                                        result[original_idx] = {
                                            "label": label,
                                            "category": category
                                        }
                        break
                    except json.JSONDecodeError:
                        continue
        
        # Save results (to new _v2 columns)
        if result:
            for original_idx, interest_data in result.items():
                if original_idx < len(df):
                    # Save category name to new column
                    df.at[original_idx, "interest_ollama_v2"] = interest_data.get("category", "")
                    # Save label to new column
                    df.at[original_idx, "interest_label_ollama_v2"] = interest_data.get("label", 1)
            
            processed_dialogs += 1
            total_processed += len(result)
            
            # Save every 20 dialogs
            if processed_dialogs % 20 == 0:
                output_file = str(INTEREST_RESULTS)
                df_save = df.copy()
                
                # Clear values for persuader (B4=0) - interest only for target (new _v2 columns)
                df_save.loc[df_save["B4"] == 0, "interest_ollama_v2"] = ""
                df_save.loc[df_save["B4"] == 0, "interest_label_ollama_v2"] = ""
                
                # For target (B4=1) leave as is - don't fill empty values with fillna
                # Convert only None to empty string for correct saving
                df_save.loc[(df_save["B4"] == 1) & (df_save["interest_ollama_v2"].isna()), "interest_ollama_v2"] = ""
                df_save.loc[(df_save["B4"] == 1) & (df_save["interest_label_ollama_v2"].isna()), "interest_label_ollama_v2"] = ""
                
                # Convert to strings for correct saving (only for non-None values)
                df_save["interest_ollama_v2"] = df_save["interest_ollama_v2"].astype(str).replace("nan", "").replace("None", "")
                df_save["interest_label_ollama_v2"] = df_save["interest_label_ollama_v2"].astype(str).replace("nan", "").replace("None", "")
                
                df_save.to_csv(output_file, index=False)
                print(f"\n✅ Processed dialogs: {processed_dialogs}, messages: {total_processed} (saved to {output_file})")
            elif processed_dialogs % 10 == 0:
                print(f"\nProcessed dialogs: {processed_dialogs}, messages: {total_processed}")
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Timeout for dialog {dialog_id}")
        continue
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error for dialog {dialog_id}: {e}")
        continue
    except Exception as e:
        print(f"\n❌ Error for dialog {dialog_id}: {e}")
        import traceback
        traceback.print_exc()
        continue

# Final save
output_file = str(INTEREST_RESULTS)
df_save = df.copy()

# Clear values for persuader (B4=0) - interest only for target (new _v2 columns)
df_save.loc[df_save["B4"] == 0, "interest_ollama_v2"] = ""
df_save.loc[df_save["B4"] == 0, "interest_label_ollama_v2"] = ""

# For target (B4=1) leave as is - don't fill empty values with fillna
# Convert only None to empty string for correct saving
df_save.loc[(df_save["B4"] == 1) & (df_save["interest_ollama_v2"].isna()), "interest_ollama_v2"] = ""
df_save.loc[(df_save["B4"] == 1) & (df_save["interest_label_ollama_v2"].isna()), "interest_label_ollama_v2"] = ""

# Convert to strings for correct saving (only for non-None values)
df_save["interest_ollama_v2"] = df_save["interest_ollama_v2"].astype(str).replace("nan", "").replace("None", "")
df_save["interest_label_ollama_v2"] = df_save["interest_label_ollama_v2"].astype(str).replace("nan", "").replace("None", "")

df_save.to_csv(output_file, index=False)

print(f"\n{'='*70}")
print(f"✅ PROCESSING COMPLETED")
print(f"{'='*70}")
print(f"Processed dialogs: {processed_dialogs}")
print(f"Processed messages: {total_processed}")
print(f"Results saved to: {output_file}")
print(f"{'='*70}")

# Statistics (for new _v2 columns)
if total_processed > 0:
    print(f"\nDistribution by labels (v2):")
    label_counts = df_save["interest_label_ollama_v2"].value_counts().sort_index()
    for label, count in label_counts.items():
        if str(label).strip() and str(label) != "nan":
            try:
                label_int = int(float(label))
                label_name = {0: "Not Interested", 1: "Neutral", 2: "Interested"}.get(label_int, "unknown")
                print(f"  {label_int} ({label_name}): {count}")
            except:
                pass
    
    print(f"\nDistribution by categories (v2):")
    category_counts = df_save["interest_ollama_v2"].value_counts()
    for category, count in category_counts.items():
        if category and str(category).strip() and str(category) != "nan":
            print(f"  {category}: {count}")

