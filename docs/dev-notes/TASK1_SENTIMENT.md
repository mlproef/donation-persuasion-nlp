# Задача 1: Анализ позитивной ноты общения (Sentiment анализ)

## Цель задачи

Определить общую тональность общения в диалоге - позитивная ли нота общения.

Используя sentiment анализ через предобученную модель RoBERTa.

---

## Реализация

### Скрипт: `bsp2.py` (строки 7-41)

**Что делали:**
- Загрузили базовые диалоги (`full_dialog.csv`)
- Применили **sentiment модель** для анализа тональности сообщений target (B4=1)
- Использовали модель: `cardiffnlp/twitter-roberta-base-sentiment`

**Код:**
```python
# --- SENTIMENT MODEL ---
sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment"
sent_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sent_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name).to(device)
sent_model.eval()

def roberta_sentiment(text):
    if not isinstance(text, str) or text.strip() == "":
        return None

    inputs = sent_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128
    ).to(device)

    with torch.no_grad():
        outputs = sent_model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1)
    labels = ["negative", "neutral", "positive"]
    return labels[int(torch.argmax(probs))]
```

**Результат:** `full_dialog_with_reactions.csv`

**Структура результата:**
- `sentiment_reaction` - метка тональности: **negative**, **neutral**, или **positive**

**Применение:**
- Анализируются только сообщения target (B4=1)
- Для каждого сообщения определяется общая тональность

---

## Текущее состояние

### ✅ Что работает:

1. **Sentiment анализ:**
   - Модель: `cardiffnlp/twitter-roberta-base-sentiment`
   - Три класса: negative, neutral, positive
   - Применено ко всем сообщениям target

2. **Результаты:**
   - `full_dialog_with_reactions.csv` - все диалоги с sentiment метками
   - Работает стабильно и дает хорошие результаты

### Почему остановились на этом:

- ✅ Модель работает хорошо и стабильно
- ✅ Результаты удовлетворяют требованиям задачи
- ✅ Не требует дополнительной настройки или обучения
- ✅ Быстро работает на всех данных

---

## Файлы задачи

### Скрипт:
- `bsp2.py` (строки 7-41) - sentiment анализ

### Данные:
- `full_dialog_with_reactions.csv` - диалоги с sentiment метками

---

## Использование результата

Sentiment метки используются для:
- Общей оценки тональности диалога
- Понимания эмоционального фона общения
- Дополнительного контекста для других задач

---

*Задача 1: Анализ позитивной ноты общения*
