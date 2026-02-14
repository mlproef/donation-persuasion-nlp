
import pandas as pd
import requests
import json
import os
import re
import time
from tqdm import tqdm

# Импортируем стратегии и категории из основного файла
import sys
sys.path.insert(0, 'bsp2')
from llama_analizator import STRATEGIES_INFO, STRATEGY_CATEGORIES

# Конфигурация Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:30b")
REQUEST_TIMEOUT = 600  # Увеличиваем таймаут для batch-запросов (10 минут)

# Загружаем данные
print("Загрузка данных...")
df = pd.read_csv("full_dialog.csv")
df = df.sort_values(["B2", "Turn"]).reset_index(drop=True)

# Создаем колонку для стратегий, если её нет
if "strategy_ollama" not in df.columns:
    df["strategy_ollama"] = None

# Группируем по диалогам
groups = df.groupby("B2", sort=False)

print(f"Всего диалогов: {len(groups)}")
print(f"Начинаем обработку...\n")

# Подготовка данных для промпта (одинаковая для всех диалогов)

# Формируем иерархическую структуру: категории со стратегиями внутри
hierarchical_structure = []
for cat_id, cat_info in STRATEGY_CATEGORIES.items():
    # Находим все стратегии в этой категории
    strategies_in_category = [s for s in STRATEGIES_INFO if s.get('parent_id') == cat_id]
    strategy_names = [s['name'] for s in strategies_in_category]
    
    hierarchical_structure.append({
        'category_id': cat_id,
        'category_name': cat_info['name'],
        'category_definition': cat_info['definition'],
        'strategies': strategy_names
    })

# Формируем текстовое представление иерархии для промпта
hierarchical_text = ""
for cat_data in hierarchical_structure:
    hierarchical_text += f"\n{cat_data['category_name']}:\n"
    hierarchical_text += f"  Definition: {cat_data['category_definition']}\n"
    hierarchical_text += f"  Strategies ({len(cat_data['strategies'])}):\n"
    for strategy in cat_data['strategies']:
        hierarchical_text += f"    - {strategy}\n"

# Список всех точных названий стратегий (для валидации)
all_strategy_names = [s['name'] for s in STRATEGIES_INFO]
strategy_names_list = ", ".join(all_strategy_names)

num_strategies = len(STRATEGIES_INFO)
num_categories = len(STRATEGY_CATEGORIES)

# Обрабатываем каждый диалог

processed_dialogs = 0
total_processed = 0

for dialog_id, dialog_group in tqdm(groups, desc="Обработка диалогов"):
    # Сохраняем original_index
    dialog_group = dialog_group.copy()
    dialog_group["original_index"] = dialog_group.index
    dialog_group = dialog_group.sort_values("Turn").reset_index(drop=True)
    
    # Находим все сообщения persuader'а в диалоге
    persuader_rows = []
    for idx, row in dialog_group.iterrows():
        b4_value = row["B4"]
        if b4_value == 0 or str(b4_value) == "0":
            original_idx = row.get("original_index", idx)
            # Пропускаем уже обработанные сообщения
            if pd.notna(df.at[original_idx, "strategy_ollama"]) and str(df.at[original_idx, "strategy_ollama"]).strip() != "":
                continue
            persuader_rows.append((original_idx, row))
    
    # Если нет сообщений для обработки, пропускаем диалог
    if not persuader_rows:
        continue
    
    # Формируем полный диалог для контекста
    dialog_text = []
    for _, row in dialog_group.iterrows():
        speaker = "Persuader" if (row["B4"] == 0 or str(row["B4"]) == "0") else "User"
        text = str(row["Unit"]) if isinstance(row["Unit"], str) else ""
        if text.strip():
            dialog_text.append(f"{speaker}: {text}")
    
    full_dialog = "\n".join(dialog_text)
    
    # Формируем список сообщений persuader'а для анализа
    persuader_messages_list = []
    for local_idx, (original_idx, row) in enumerate(persuader_rows):
        message = str(row["Unit"]) if isinstance(row["Unit"], str) else ""
        if message.strip():
            persuader_messages_list.append(f"Message #{local_idx + 1}: {message}")
    
    persuader_messages_text = "\n".join(persuader_messages_list)
    
    # Формируем промпт с иерархической структурой
    prompt = f"""Analyze {len(persuader_rows)} persuader messages and return strategy for each using HIERARCHICAL CLASSIFICATION.

MESSAGES TO ANALYZE:
{persuader_messages_text}

FULL DIALOGUE CONTEXT:
{full_dialog}

HIERARCHICAL STRUCTURE ({num_categories} categories, {num_strategies} strategies total):
{hierarchical_text}

TASK - TWO-STEP HIERARCHICAL CLASSIFICATION:
For each message above, you MUST:
1. FIRST: Determine which CATEGORY best fits the message
2. THEN: Choose the specific STRATEGY within that category

This hierarchical approach improves accuracy by narrowing down choices.

RESPONSE STRUCTURE:
1. You can think/analyze first (optional)
2. Then output JSON in this exact format:

{{
  "Message #1": "<exact_strategy_name>",
  "Message #2": "<exact_strategy_name>",
  "Message #3": "<exact_strategy_name>"
}}

IMPORTANT:
- Use HIERARCHICAL approach: first choose category, then strategy within that category
- Use EXACT strategy names from the hierarchical structure above
- If no strategy fits, use "None"
- Your response MUST end with valid JSON
- JSON must start with {{ and end with }}
- Do not stop before completing the JSON object

EXAMPLE OUTPUT:
{{
  "Message #1": "Call to Action",
  "Message #2": "Social Proof",
  "Message #3": "Urgency"
}}

Now analyze the messages using hierarchical classification and return the JSON:"""

    messages = [
        {
            "role": "system",
            "content": "You are a hierarchical strategy classification system. For each message, you MUST first determine the category, then choose the specific strategy within that category. You may think about the analysis, but you MUST complete your response with a valid JSON object containing strategy names. The JSON must be complete and valid. Do not stop generating until the JSON object is finished."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    # Отправляем запрос
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 8000,
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT, stream=True)
        response.raise_for_status()
        
        # Собираем все части ответа БЕЗ ВЫВОДА
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
        
        # Парсим JSON
        result = {}
        json_start = full_content.find('{')
        json_end = full_content.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            for attempt_end in range(json_end, json_start, -1):
                try:
                    json_str = full_content[json_start:attempt_end+1]
                    parsed_json = json.loads(json_str)
                    
                    for key, strategy_name in parsed_json.items():
                        match = re.match(r'Message\s*#(\d+)', key, re.IGNORECASE)
                        if match:
                            msg_num = int(match.group(1))
                            if msg_num <= len(persuader_rows):
                                original_idx = persuader_rows[msg_num - 1][0]
                                result[original_idx] = strategy_name
                    break
                except json.JSONDecodeError:
                    continue
        
        # Сохраняем результаты
        if result:
            for original_idx, strategy_name in result.items():
                if original_idx < len(df):
                    df.at[original_idx, "strategy_ollama"] = strategy_name if strategy_name != "None" else None
            
            # Сохраняем после каждого диалога
            output_file = "test_batch_results.csv"
            df_save = df.copy()
            df_save["strategy_ollama"] = df_save["strategy_ollama"].fillna("")
            df_save.to_csv(output_file, index=False)
            
            processed_dialogs += 1
            total_processed += len(result)
            
            if processed_dialogs % 10 == 0:
                print(f"\nОбработано диалогов: {processed_dialogs}, сообщений: {total_processed}")
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Таймаут для диалога {dialog_id}")
        continue
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка запроса для диалога {dialog_id}: {e}")
        continue
    except Exception as e:
        print(f"\n❌ Ошибка для диалога {dialog_id}: {e}")
        continue

# Финальное сохранение
output_file = "test_batch_results.csv"
df_save = df.copy()
df_save["strategy_ollama"] = df_save["strategy_ollama"].fillna("")
df_save.to_csv(output_file, index=False)

print(f"\n{'='*70}")
print(f"✅ ОБРАБОТКА ЗАВЕРШЕНА")
print(f"{'='*70}")
print(f"Обработано диалогов: {processed_dialogs}")
print(f"Обработано сообщений: {total_processed}")
print(f"Результаты сохранены в: {output_file}")
print(f"{'='*70}")
