"""
Task 3: label every persuader message with one persuasion strategy.

Hierarchical prompting via Ollama: the LLM first picks one of 12 categories,
then a specific strategy inside it (taxonomy in strategies_hierarchical.py).

Usage:
    python src/classification/llama_strategies.py

Input:  data/raw/full_dialog.csv
Output: data/interim/test_batch_results_single.csv  (column strategy_ollama_single)

Settings (environment variables):
    OLLAMA_URL    Ollama chat endpoint (default: http://localhost:11434/api/chat)
    OLLAMA_MODEL  model name (default: qwen3:30b)

Progress is saved periodically, so an interrupted run resumes where it stopped.
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import FULL_DIALOG, STRATEGY_RESULTS  # noqa: E402

import pandas as pd
import requests
import json
import os
import re
import time
import signal
import sys
from tqdm import tqdm

# Import strategies and categories directly
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from strategies_hierarchical import STRATEGIES_INFO, STRATEGY_CATEGORIES         

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:30b")
REQUEST_TIMEOUT = 600  # Increased timeout for batch requests (10 minutes)

# Load data
print("Loading data...")
# Try to load existing results if they exist
if os.path.exists(str(STRATEGY_RESULTS)):
    print("   Found results file, loading it...")
    df = pd.read_csv(str(STRATEGY_RESULTS))
    # Restore empty strings to NaN for proper checking
    df["strategy_ollama_single"] = df["strategy_ollama_single"].replace("", pd.NA)
else:
    print("   Results file not found, loading source data...")
    df = pd.read_csv(str(FULL_DIALOG))
    # Create column for strategies if it doesn't exist
    if "strategy_ollama_single" not in df.columns:
        df["strategy_ollama_single"] = None

df = df.sort_values(["B2", "Turn"]).reset_index(drop=True)

# Group by dialogs
groups = df.groupby("B2", sort=False)

print(f"Total dialogs: {len(groups)}")
print(f"Starting processing one message at a time with context...\n")

# Prepare data for prompt (same for all messages)

# Build hierarchical structure: categories with strategies inside
hierarchical_structure = []
for cat_id, cat_info in STRATEGY_CATEGORIES.items():
    # Find all strategies in this category
    strategies_in_category = [s for s in STRATEGIES_INFO if s.get('parent_id') == cat_id]
    strategy_names = [s['name'] for s in strategies_in_category]
    
    hierarchical_structure.append({
        'category_id': cat_id,
        'category_name': cat_info['name'],
        'category_definition': cat_info['definition'],
        'strategies': strategy_names
    })

# Build text representation of hierarchy for prompt
hierarchical_text = ""
for cat_data in hierarchical_structure:
    hierarchical_text += f"\n{cat_data['category_name']}:\n"
    hierarchical_text += f"  Definition: {cat_data['category_definition']}\n"
    hierarchical_text += f"  Strategies ({len(cat_data['strategies'])}):\n"
    for strategy in cat_data['strategies']:
        hierarchical_text += f"    - {strategy}\n"

num_strategies = len(STRATEGIES_INFO)
num_categories = len(STRATEGY_CATEGORIES)

# Create list of valid strategy names for validation
valid_strategy_names = [s['name'] for s in STRATEGIES_INFO if 'name' in s]

# Collect all persuader messages for processing
all_persuader_messages = []
skipped_empty = 0
skipped_already_processed = 0

for dialog_id, dialog_group in groups:
    # Save original indices before sorting
    dialog_group_with_idx = dialog_group.copy()
    dialog_group_with_idx['original_index'] = dialog_group_with_idx.index
    
    dialog_group_sorted = dialog_group_with_idx.sort_values("Turn").reset_index(drop=True)
    
    for idx, row in dialog_group_sorted.iterrows():
        b4_value = row["B4"]
        if b4_value == 0 or str(b4_value) == "0":
            # Get original index from source dataframe
            original_idx = int(row['original_index'])
            
            # Check if already processed
            if pd.notna(df.at[original_idx, "strategy_ollama_single"]) and str(df.at[original_idx, "strategy_ollama_single"]).strip() != "":
                skipped_already_processed += 1
                continue
            
            # Check if message is empty (filter immediately so progress bar is accurate)
            current_message = str(row["Unit"]) if isinstance(row["Unit"], str) else ""
            if not current_message.strip():
                skipped_empty += 1
                continue
            
            all_persuader_messages.append({
                'dialog_id': dialog_id,
                'dialog_group': dialog_group_sorted,
                'index_in_dialog': idx,
                'original_idx': original_idx,
                'row': row
            })

print(f"Total persuader messages to process: {len(all_persuader_messages)}")
print(f"Skipped (already processed): {skipped_already_processed}")
print(f"Skipped (empty messages): {skipped_empty}\n")

# Function to save progress
def save_progress():
    """Saves current progress to file"""
    global df
    output_file = str(STRATEGY_RESULTS)
    df_save = df.copy()
    df_save["strategy_ollama_single"] = df_save["strategy_ollama_single"].fillna("")
    df_save.to_csv(output_file, index=False)
    return output_file

# Signal handler for saving on interruption
def signal_handler(sig, frame):
    """Saves progress on interruption (Ctrl+C)"""
    print("\n\n⚠️  Interrupt signal received. Saving progress...")
    output_file = save_progress()
    print(f"✅ Progress saved to {output_file}")
    print("You can safely interrupt execution.")
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Process each message separately
processed_count = 0
total_processed = 0
skipped_invalid_strategy = 0

for msg_data in tqdm(all_persuader_messages, desc="Processing messages"):
    dialog_id = msg_data['dialog_id']
    dialog_group = msg_data['dialog_group']
    idx = msg_data['index_in_dialog']
    original_idx = msg_data['original_idx']
    row = msg_data['row']
    
    # Get current message (already checked for emptiness when added to list)
    current_message = str(row["Unit"]) if isinstance(row["Unit"], str) else ""
    
    # Build context from 5 previous messages in dialog
    context_messages = []
    context_start = max(0, idx - 5)
    
    for context_idx in range(context_start, idx):
        context_row = dialog_group.iloc[context_idx]
        speaker = "Persuader" if (context_row["B4"] == 0 or str(context_row["B4"]) == "0") else "User"
        text = str(context_row["Unit"]) if isinstance(context_row["Unit"], str) else ""
        turn = context_row.get("Turn", context_idx)
        if text.strip():
            context_messages.append(f"Turn {turn} - {speaker}: {text}")
    
    # Build context text from last 5 messages
    context_text = "\n".join(context_messages) if context_messages else "No previous messages in this dialog."
    
    # Build prompt
    prompt = f"""You are a hierarchical persuasion strategy classification system.

Your task is to classify ONE persuader message using a TWO-STEP HIERARCHICAL APPROACH.

MESSAGE TO ANALYZE:
Turn {row.get('Turn', idx)} - Persuader: {current_message}

CONTEXT (up to 5 previous messages in the same dialogue, if any):
{context_text}

HIERARCHICAL STRUCTURE (CATEGORIES → STRATEGIES):
{hierarchical_text}

TASK (MANDATORY STEPS):
1. FIRST: Determine which CATEGORY best fits the message.
2. THEN: Choose the SINGLE most appropriate STRATEGY within that category.

CLASSIFICATION RULES (STRICT):
- You MUST assign EXACTLY ONE strategy to this message.
- You MUST use an EXACT strategy name from the list above.
- If the message does NOT attempt to persuade, you MUST choose a strategy from:
  "Conversation Management".
- DO NOT output "None" for non-empty messages.
- Use context ONLY to understand flow or verify dialogue-dependent strategies.
- Do NOT guess dialogue-dependent strategies unless there is CLEAR evidence in the provided context.

DIALOGUE-DEPENDENT STRATEGIES (IMPORTANT):
The following strategies REQUIRE clear evidence across multiple messages:
- Activation of Personal Commitment
- Commitment and Consistency
- Foot-in-the-door
- Door-in-the-face

You MUST use these strategies ONLY IF:
- A relevant earlier message is clearly visible in the provided context, AND
- The current message logically depends on that earlier message.

If this condition is NOT met, DO NOT use dialogue-dependent strategies.

OUTPUT FORMAT (STRICT — NO EXTRA TEXT):
Return ONLY the following format:

BEGIN_JSON
{{"strategy":"<exact_strategy_name>"}}
END_JSON

Do NOT include explanations, reasoning, or any other text outside BEGIN_JSON / END_JSON."""

    messages = [
        {
            "role": "system",
            "content": "You are a hierarchical persuasion strategy classification system. Your task is to classify persuader messages using a two-step hierarchical approach: first determine the category, then choose the specific strategy within that category. You must output ONLY valid JSON between BEGIN_JSON and END_JSON markers. Do not include any explanations or reasoning outside these markers."
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
            "num_predict": 4000,
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
        strategy_name = None
        
        # First try to find JSON between markers
        begin_marker = "BEGIN_JSON"
        end_marker = "END_JSON"
        begin_idx = full_content.find(begin_marker)
        end_idx = full_content.find(end_marker)
        
        if begin_idx != -1 and end_idx != -1 and end_idx > begin_idx:
            # Extract JSON between markers
            json_str = full_content[begin_idx + len(begin_marker):end_idx].strip()
            try:
                parsed_json = json.loads(json_str)
                if "strategy" in parsed_json:
                    strategy_name = parsed_json["strategy"]
            except json.JSONDecodeError:
                pass
        
        # Fallback: if markers not found, try regular JSON search
        if not strategy_name:
            json_start = full_content.find('{')
            json_end = full_content.rfind('}')
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                for attempt_end in range(json_end, json_start, -1):
                    try:
                        json_str = full_content[json_start:attempt_end+1]
                        parsed_json = json.loads(json_str)
                        
                        if "strategy" in parsed_json:
                            strategy_name = parsed_json["strategy"]
                        break
                    except json.JSONDecodeError:
                        continue
        
        # Save result (don't save "None", as Conversation Management is now used for non-persuasive messages)
        if strategy_name and strategy_name.strip() and strategy_name.lower() != "none":
            # Validation: check that strategy_name exists in list of valid strategies
            if strategy_name not in valid_strategy_names:
                # Skip invalid strategies
                skipped_invalid_strategy += 1
                continue
            
            if original_idx < len(df):
                df.at[original_idx, "strategy_ollama_single"] = strategy_name
                total_processed += 1
                
                processed_count += 1
                
                # Save every 25 messages (reduced interval for safety)
                if processed_count % 25 == 0:
                    output_file = save_progress()
                    print(f"\n✅ Processed messages: {processed_count} (saved to {output_file})")
                    if skipped_invalid_strategy > 0:
                        print(f"   Skipped (invalid strategies): {skipped_invalid_strategy}")
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Timeout for message in dialog {dialog_id}")
        # Save progress on error
        if processed_count > 0 and processed_count % 25 != 0:
            output_file = save_progress()
            print(f"   💾 Progress saved after error: {output_file}")
        continue
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error for message in dialog {dialog_id}: {e}")
        # Save progress on error
        if processed_count > 0 and processed_count % 25 != 0:
            output_file = save_progress()
            print(f"   💾 Progress saved after error: {output_file}")
        continue
    except Exception as e:
        print(f"\n❌ Error for message in dialog {dialog_id}: {e}")
        # Save progress on error
        if processed_count > 0 and processed_count % 25 != 0:
            output_file = save_progress()
            print(f"   💾 Progress saved after error: {output_file}")
        continue

# Final save
output_file = save_progress()

print(f"\n{'='*70}")
print(f"✅ PROCESSING COMPLETED")
print(f"{'='*70}")
print(f"Processed and saved messages: {processed_count}")
if skipped_invalid_strategy > 0:
    print(f"Skipped (invalid strategies): {skipped_invalid_strategy}")
print(f"Results saved to: {output_file}")
print(f"{'='*70}")

