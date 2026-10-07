"""
Task 1: classify the sentiment (negative / neutral / positive) of every persuadee message.
Sends one LLM request per dialog via Ollama, same batching approach as llama_interest.py.

Usage:
    python src/classification/llama_sentiment.py

What it does:
    1. Loads data/raw/full_dialog.csv
    2. Groups by dialogs (B2)
    3. For each dialog, finds all target messages (B4=1)
    4. Sends batch request to Ollama to analyze all target messages in the dialog
    5. Determines sentiment: negative, neutral, or positive
    6. Saves results to data/interim/test_batch_sentiment_results.csv

Results:
    - sentiment_ollama: category name ("negative", "neutral", or "positive")

Settings:
    - OLLAMA_URL: Ollama server URL (default: http://localhost:11434/api/chat, override with the OLLAMA_URL environment variable)
    - OLLAMA_MODEL: Ollama model (default: gpt-oss:20b, override with the OLLAMA_MODEL environment variable)
    - REQUEST_TIMEOUT: request timeout in seconds (default: 600)
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import FULL_DIALOG, SENTIMENT_RESULTS  # noqa: E402

import pandas as pd
import requests
import json
import os
import re
import time
from tqdm import tqdm
import sys

# Sentiment category structure (embedded in file)
SENTIMENT_CATEGORIES = {
    "negative": {
        "name": "negative",
        "definition": "The person expresses negative emotions, frustration, anger, or dissatisfaction."
    },
    "neutral": {
        "name": "neutral",
        "definition": "The person expresses neutral tone, neither positive nor negative."
    },
    "positive": {
        "name": "positive",
        "definition": "The person expresses positive emotions, enthusiasm, agreement, or satisfaction."
    }
}

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
REQUEST_TIMEOUT = 600  # Increased timeout for batch requests (10 minutes)

# Load data
print("Loading data...")
# Try to load existing results if they exist
if os.path.exists(str(SENTIMENT_RESULTS)):
    print("   Found results file, loading it...")
    df = pd.read_csv(str(SENTIMENT_RESULTS))
    # Restore empty strings to NaN for proper checking
    if "sentiment_ollama" in df.columns:
        df["sentiment_ollama"] = df["sentiment_ollama"].replace("", pd.NA)
    # Create column for new v2 results if it doesn't exist
    if "sentiment_ollama_v2" not in df.columns:
        df["sentiment_ollama_v2"] = None
    else:
        # Restore empty strings to NaN for proper checking
        df["sentiment_ollama_v2"] = df["sentiment_ollama_v2"].replace("", pd.NA)
else:
    print("   Results file not found, loading source data...")
    df = pd.read_csv(str(FULL_DIALOG))
    # Create columns for sentiment if they don't exist
    if "sentiment_ollama" not in df.columns:
        df["sentiment_ollama"] = None
    if "sentiment_ollama_v2" not in df.columns:
        df["sentiment_ollama_v2"] = None

# Determine which column to use for new analysis
# Use _v2 if it exists, otherwise create new one
SENTIMENT_COLUMN = "sentiment_ollama_v2"

df = df.sort_values(["B2", "Turn"]).reset_index(drop=True)

# Group by dialogs
groups = df.groupby("B2", sort=False)

print(f"Total dialogs: {len(groups)}")
print(f"Starting processing...\n")

# Prepare data for prompt (same for all dialogs)

# List of all sentiment categories (only 3 categories)
categories_list = "\n".join([
    f"- {cat_info['name']}: {cat_info['definition']}"
    for cat_id, cat_info in SENTIMENT_CATEGORIES.items()
])

# List of all categories for JSON response
all_category_names = [cat_info['name'] for cat_info in SENTIMENT_CATEGORIES.values()]
category_names_list = ", ".join(all_category_names)

# List of names for quick access
name_mapping = {cat_info['name'].lower(): cat_info['name'] for cat_info in SENTIMENT_CATEGORIES.values()}

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
            # Skip already processed messages (check column for new analysis)
            if SENTIMENT_COLUMN in df.columns:
                sentiment_value = df.at[original_idx, SENTIMENT_COLUMN]
                if pd.notna(sentiment_value) and str(sentiment_value).strip() != "":
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
    prompt = f"""Analyze {num_valid_messages} target user messages and determine their sentiment (emotional tone).

SENTIMENT CATEGORIES (only 3 options):
- negative: The person expresses negative emotions, frustration, anger, or dissatisfaction
- neutral: The person expresses neutral tone, neither positive nor negative
- positive: The person expresses positive emotions, enthusiasm, agreement, or satisfaction

MESSAGES TO ANALYZE (each with context from last 2 previous messages):
{target_messages_text}

TASK:
For each target message above, determine the sentiment. Return ONLY the category name: "negative", "neutral", or "positive".

You may think about it, but you MUST end your response with a valid JSON object.

OUTPUT FORMAT (STRICT — NO EXTRA TEXT):
Return ONLY the following format:

BEGIN_JSON
{{"Message #1": "negative", "Message #2": "neutral", "Message #3": "positive"}}
END_JSON

IMPORTANT:
- Return ONLY category names: "negative", "neutral", or "positive"
- negative = negative emotions, frustration, anger
- neutral = neutral tone, neither positive nor negative
- positive = positive emotions, enthusiasm, agreement
- Do NOT include explanations, reasoning, or any other text outside BEGIN_JSON / END_JSON
- JSON must be between BEGIN_JSON and END_JSON markers

EXAMPLE OUTPUT:
BEGIN_JSON
{{"Message #1": "negative", "Message #2": "neutral", "Message #3": "positive"}}
END_JSON"""

    messages = [
        {
            "role": "system",
            "content": "You are a sentiment classification system. You must output ONLY valid JSON between BEGIN_JSON and END_JSON markers. Do not include any explanations or reasoning outside these markers. The JSON must contain only sentiment categories (\"negative\", \"neutral\", or \"positive\") for each message."
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
                            if isinstance(value, str):
                                # This is category name
                                sentiment_name = value.strip().lower()
                                # Normalize name
                                if sentiment_name in name_mapping:
                                    sentiment = name_mapping[sentiment_name]
                                elif sentiment_name in ["neg", "negative"]:
                                    sentiment = "negative"
                                elif sentiment_name in ["neu", "neutral"]:
                                    sentiment = "neutral"
                                elif sentiment_name in ["pos", "positive"]:
                                    sentiment = "positive"
                                else:
                                    sentiment = "neutral"  # Default to neutral
                                
                                result[original_idx] = sentiment
                            elif isinstance(value, dict):
                                # Old format with dict - extract sentiment
                                sentiment = value.get("sentiment") or value.get("category")
                                if sentiment:
                                    sentiment_name = str(sentiment).strip().lower()
                                    if sentiment_name in name_mapping:
                                        sentiment = name_mapping[sentiment_name]
                                    elif sentiment_name in ["neg", "negative"]:
                                        sentiment = "negative"
                                    elif sentiment_name in ["neu", "neutral"]:
                                        sentiment = "neutral"
                                    elif sentiment_name in ["pos", "positive"]:
                                        sentiment = "positive"
                                    else:
                                        sentiment = "neutral"
                                else:
                                    sentiment = "neutral"
                                
                                result[original_idx] = sentiment
                            else:
                                # Unknown format - default to neutral
                                result[original_idx] = "neutral"
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
                                    if isinstance(value, str):
                                        sentiment_name = value.strip().lower()
                                        if sentiment_name in name_mapping:
                                            sentiment = name_mapping[sentiment_name]
                                        elif sentiment_name in ["neg", "negative"]:
                                            sentiment = "negative"
                                        elif sentiment_name in ["neu", "neutral"]:
                                            sentiment = "neutral"
                                        elif sentiment_name in ["pos", "positive"]:
                                            sentiment = "positive"
                                        else:
                                            sentiment = "neutral"
                                        result[original_idx] = sentiment
                        break
                    except json.JSONDecodeError:
                        continue
        
        # Save results
        if result:
            for original_idx, sentiment_name in result.items():
                if original_idx < len(df):
                    # Save sentiment name to column for new analysis
                    df.at[original_idx, SENTIMENT_COLUMN] = sentiment_name
            
            processed_dialogs += 1
            total_processed += len(result)
            
            # Save every 20 dialogs
            if processed_dialogs % 20 == 0:
                output_file = str(SENTIMENT_RESULTS)
                df_save = df.copy()
                
                # For target (B4=1) leave as is - don't fill empty values with fillna
                # Convert only None to empty string for correct saving (for both columns)
                if "sentiment_ollama" in df_save.columns:
                    df_save.loc[(df_save["B4"] == 1) & (df_save["sentiment_ollama"].isna()), "sentiment_ollama"] = ""
                    df_save["sentiment_ollama"] = df_save["sentiment_ollama"].astype(str).replace("nan", "").replace("None", "")
                
                if SENTIMENT_COLUMN in df_save.columns:
                    df_save.loc[(df_save["B4"] == 1) & (df_save[SENTIMENT_COLUMN].isna()), SENTIMENT_COLUMN] = ""
                    df_save[SENTIMENT_COLUMN] = df_save[SENTIMENT_COLUMN].astype(str).replace("nan", "").replace("None", "")
                
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
output_file = str(SENTIMENT_RESULTS)
df_save = df.copy()

# Clear values for persuader (B4=0) - sentiment only for target (for both columns)
if "sentiment_ollama" in df_save.columns:
    df_save.loc[df_save["B4"] == 0, "sentiment_ollama"] = ""
    # For target (B4=1) leave as is - don't fill empty values with fillna
    # Convert only None to empty string for correct saving
    df_save.loc[(df_save["B4"] == 1) & (df_save["sentiment_ollama"].isna()), "sentiment_ollama"] = ""
    # Convert to strings for correct saving (only for non-None values)
    df_save["sentiment_ollama"] = df_save["sentiment_ollama"].astype(str).replace("nan", "").replace("None", "")

if SENTIMENT_COLUMN in df_save.columns:
    # IMPORTANT: First save non-empty values, then process empty ones
    # Clear only persuader (B4=0)
    df_save.loc[df_save["B4"] == 0, SENTIMENT_COLUMN] = ""
    # For target (B4=1): convert only NaN/None to empty string, DON'T touch filled values
    mask_na = (df_save["B4"] == 1) & (df_save[SENTIMENT_COLUMN].isna())
    df_save.loc[mask_na, SENTIMENT_COLUMN] = ""
    # Convert to strings ONLY for saving, but preserve all non-empty values
    # Save filled values BEFORE conversion
    filled_mask = (df_save["B4"] == 1) & (df_save[SENTIMENT_COLUMN].notna())
    filled_values = df_save.loc[filled_mask, SENTIMENT_COLUMN].copy()
    # Convert to strings
    df_save[SENTIMENT_COLUMN] = df_save[SENTIMENT_COLUMN].astype(str)
    # Restore filled values
    df_save.loc[filled_mask, SENTIMENT_COLUMN] = filled_values.astype(str)
    # Clear only "nan" and "None" strings
    df_save.loc[df_save[SENTIMENT_COLUMN] == "nan", SENTIMENT_COLUMN] = ""
    df_save.loc[df_save[SENTIMENT_COLUMN] == "None", SENTIMENT_COLUMN] = ""

df_save.to_csv(output_file, index=False)

print(f"\n{'='*70}")
print(f"✅ PROCESSING COMPLETED")
print(f"{'='*70}")
print(f"Processed dialogs: {processed_dialogs}")
print(f"Processed messages: {total_processed}")
print(f"Results saved to: {output_file}")
print(f"{'='*70}")

# Statistics
if total_processed > 0:
    print(f"\nDistribution by sentiment (new analysis - {SENTIMENT_COLUMN}):")
    if SENTIMENT_COLUMN in df_save.columns:
        sentiment_counts = df_save[SENTIMENT_COLUMN].value_counts()
        for sentiment, count in sentiment_counts.items():
            if sentiment and sentiment.strip():
                print(f"  {sentiment}: {count}")

