# Задача 3: Определение стратегий убеждения

## Цель задачи

Определить, какие стратегии убеждения использует persuader (B4=0) в каждом сообщении:
- **40 различных стратегий** (Rewarding Activity, Emotional Appeal, Social Proof, Urgency, и т.д.)
- Для каждого сообщения persuader определяем **одну лучшую стратегию**

Используя Natural Language Inference (NLI) через RoBERTa-large-MNLI.

---

## Эволюция подхода

### Этап 1: Первая попытка - Zero-shot классификация (9 декабря 2024)

#### Скрипт: `bsp2_first_roberta_for_strategies.py`

**Что делали:**
- Загрузили `full_dialog.csv`
- Оставили только сообщения persuader (B4=0)
- Использовали **zero-shot классификатор** `facebook/bart-large-mnli`
- Проверяли **45 стратегий** для каждого сообщения
- Возвращали до **4 лучших стратегий** (если score >= 0.30)

**Список стратегий (45):**
1. Rewarding Activity
2. Punishing Activity
3. Expertise
4. Activation of Personal Commitment
5. Activation of Impersonal Commitment
6. Liking
7. Pre-giving
8. Moral Appeal
9. Aversive Stimulation
10. Debt
... и еще 35 стратегий

**Метод:**
```python
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
result = classifier(text, strategies, multi_label=True)
# Возвращает до 4 стратегий с score >= 0.30
```

**Результат:** `strategies_B4_0.csv`

**Структура:**
- Все колонки из `full_dialog.csv` (только B4=0)
- `strategies` - список стратегий через запятую (до 4)

**Проблемы:**
- ❌ Анализировали только **текущее сообщение** (без контекста диалога)
- ❌ Слишком много стратегий (45) - некоторые похожи друг на друга
- ❌ Zero-shot классификация не всегда точна
- ❌ Возвращали несколько стратегий - неясно, какая главная
- ❌ BART-large-MNLI менее точная, чем RoBERTa-large-MNLI

**Что получили:**
- ✅ Первые автоматические метки стратегий
- ✅ Понимание, какие стратегии встречаются в данных
- ✅ Базовый pipeline для определения стратегий

---

### Этап 2: Улучшение - RoBERTa-large-MNLI с контекстом (11 декабря 2024)

#### Скрипт: `bsp2_my_roberta_for_strategies.py`

**Проблемы предыдущего подхода:**
- Нет контекста - стратегия может быть понятна только в контексте диалога
- Слишком много стратегий - нужно сократить и убрать дубликаты
- Zero-shot менее точный - нужно использовать NLI напрямую
- Несколько стратегий - нужна одна лучшая

**Что изменили:**

1. **Добавили контекст диалога:**
   - Анализируем не только текущее сообщение, но и **последние 4 сообщения** диалога
   - Формат: "Persuader: ... User: ... Persuader: ..."
   - Это помогает понять стратегию в контексте разговора

2. **Сократили до 40 стратегий:**
   - Убрали дубликаты и похожие стратегии
   - Оставили наиболее различимые

3. **Использовали roberta-large-mnli напрямую:**
   - Вместо zero-shot pipeline используем NLI модель напрямую
   - Более точная модель для entailment проверки

4. **Возвращаем только лучшую стратегию:**
   - Для каждого сообщения выбираем одну стратегию с максимальным score
   - Если score < 0.30, то стратегия не определяется

**Метод:**
```python
def build_premise_from_group(group_df, idx_in_group, window_size=4):
    """Строим контекст из последних 4 сообщений"""
    start = max(0, idx_in_group - window_size + 1)
    ctx = group_df.iloc[start : idx_in_group + 1]
    
    parts = []
    for _, r in ctx.iterrows():
        speaker = "Persuader" if r["B4"] == 0 else "User"
        text = str(r["Unit"])
        if text.strip():
            parts.append(f"{speaker}: {text}")
    
    return "\n".join(parts)

def best_strategy(premise_text, min_score=0.30):
    """Находим лучшую стратегию"""
    hypotheses = [s["hypothesis"] for s in strategies_info]
    
    # Проверяем все гипотезы через MNLI
    enc = tokenizer(
        [premise_text] * len(hypotheses),
        hypotheses,
        return_tensors="pt",
        padding=True,
        truncation="only_first",
        max_length=512,
    ).to(device)
    
    with torch.no_grad():
        logits = model(**enc).logits
    
    probs = F.softmax(logits, dim=1)
    entail_scores = probs[:, 2].cpu().numpy()  # класс entailment
    
    best_idx = entail_scores.argmax()
    best_score = float(entail_scores[best_idx])
    
    if best_score < min_score:
        return ""  # стратегия не определена
    
    return strategies_info[best_idx]["name"]
```

**40 стратегий:**
1. Rewarding Activity
2. Punishing Activity
3. Expertise
4. Activation of Personal Commitment
5. Activation of Impersonal Commitment
6. Liking
7. Pre-giving
8. Moral Appeal
9. Aversive Stimulation
10. Debt
11. Reciprocity
12. Commitment and Consistency
13. Social Proof
14. Authority
15. Scarcity
16. Unity
17. Rational Appeal
18. Emotional Appeal
19. Threat
20. Promise
21. Appeal to Values
22. Self-feeling Appeal
23. Logical Appeal
24. Credibility Appeal
25. Storytelling
26. Fear Appeal
27. Empathy Appeal
28. Call to Action
29. Social Positioning
30. Urgency
31. Authority Pressure
32. Pretexting
33. Emotional Manipulation
34. Scarcity Manipulation
35. Guilt Induction
36. Foot-in-the-door
37. Door-in-the-face
38. Framing
39. Loss Aversion Appeal
40. Overloading
41. Confusion Induction
42. Sympathy Appeal
43. Bait-and-switch

**Результат:** `full_dialog_with_nli_strategies.csv`

**Структура:**
- Все колонки из `full_dialog.csv`
- `strategy` - одна лучшая стратегия для сообщений persuader (B4=0)

**Прогресс:**
- ✅ Учет контекста диалога (последние 4 сообщения)
- ✅ Более точная классификация через RoBERTa-large-MNLI
- ✅ Упрощенный вывод (одна стратегия вместо нескольких)
- ✅ Сокращение до 40 наиболее различимых стратегий

---

### Этап 3: Объединение с полным диалогом (11 декабря 2024)

#### Скрипт: `bsp_adding_b0_b4.py`

**Цель:** Объединить стратегии с полным диалогом

**Что делали:**
1. Загрузили `full_dialog.csv` и `strategies_B4_0.csv`
2. Взяли только первую (лучшую) стратегию из списка
3. Объединили с полным диалогом по ключам (B2, Turn, B4, Unit)

**Результат:** `full_dialog_with_strategies_top1.csv`

**Структура:**
- Все колонки из `full_dialog.csv`
- `strategy` - одна лучшая стратегия для сообщений persuader

**Использование:**
- Полный диалог с реакциями и стратегиями
- Анализ связи между стратегиями и реакциями

---

### Этап 4: Тестирование и проверка (11 декабря 2024)

#### Скрипт: `check_before_run.py`

**Цель:** Убедиться, что все готово перед долгим запуском

**Что проверяли:**
- ✅ Наличие файла `full_dialog.csv`
- ✅ Структуру данных (колонки B2, B4, Turn, Unit)
- ✅ Загрузку модели RoBERTa-large-MNLI
- ✅ Работу функций на примере
- ⏱️ Оценку времени выполнения

**Результат:** Подтверждение готовности к запуску

---

#### Скрипт: `test_small_batch.py`

**Цель:** Финальная проверка логики на реальных данных

**Что делали:**
- Запускали на **первых 3 диалогах**
- Использовали только **5 стратегий** (для скорости)
- Проверяли логику работы функций

**Результат:** `test_batch_results.csv`

**Использование:**
- Проверка перед полным запуском
- Убедиться, что все работает корректно

**Внимание:** В реальном запуске будет проверяться 40 стратегий, поэтому тест быстрее.

---

### Этап 5: Иерархическая классификация через LLM (Ollama) (декабрь 2024)

#### Скрипт: `bsp2/llama_task3.py`

**Проблемы предыдущих подходов:**
- RoBERTa-MNLI требует много времени для обработки всех стратегий
- Плоская классификация из 42 стратегий может быть неточной
- Нет использования иерархической структуры категорий

**Что изменили:**

1. **Использование LLM (Ollama) вместо NLI:**
   - Используется модель `qwen3:30b` через Ollama API
   - Более гибкий подход к классификации
   - Может использовать reasoning для лучшего понимания контекста

2. **Иерархическая классификация:**
   - Используется двухэтапный подход:
     1. **Сначала** определяется родительская категория (из 11 категорий)
     2. **Затем** выбирается конкретная стратегия внутри категории
   - Это сужает выбор и повышает точность

3. **Batch-обработка диалогов:**
   - Все сообщения persuader'а в диалоге анализируются одним запросом
   - Более эффективно, чем обработка каждого сообщения отдельно
   - Полный контекст диалога передается в промпт

4. **Пропуск уже обработанных сообщений:**
   - Проверяется, обработано ли сообщение (есть значение в `strategy_ollama`)
   - Если все сообщения в диалоге обработаны, диалог пропускается
   - Позволяет продолжать обработку с места остановки

**Иерархическая структура:**

Используется структура из `strategies_hierarchical.py`:
- **11 родительских категорий:**
  1. Exchange / Incentives
  2. Authority / Expertise
  3. Norms / Morality / Values
  4. Commitment / Consistency
  5. Social Influence
  6. Rational / Impact Appeal
  7. Emotional Influence
  8. Urgency / Scarcity
  9. Threat / Pressure
  10. Call to Action
  11. Framing & Presentation

- **42 стратегии** распределены по категориям

**Метод:**

```python
# Формируется иерархическая структура для промпта
hierarchical_structure = []
for cat_id, cat_info in STRATEGY_CATEGORIES.items():
    strategies_in_category = [s for s in STRATEGIES_INFO if s.get('parent_id') == cat_id]
    hierarchical_structure.append({
        'category_name': cat_info['name'],
        'category_definition': cat_info['definition'],
        'strategies': [s['name'] for s in strategies_in_category]
    })

# Промпт явно требует двухэтапную классификацию:
# 1. FIRST: Determine which CATEGORY best fits the message
# 2. THEN: Choose the specific STRATEGY within that category
```

**Промпт:**
- Показывает полную иерархическую структуру (категории со стратегиями)
- Явно требует сначала выбрать категорию, потом стратегию
- Использует полный контекст диалога для анализа

**Результат:** `test_batch_results.csv`

**Структура:**
- Все колонки из `full_dialog.csv`
- `strategy_ollama` - название стратегии для сообщений persuader (B4=0)

**Преимущества:**
- ✅ Использование иерархической структуры повышает точность
- ✅ Batch-обработка более эффективна
- ✅ Возможность продолжения с места остановки
- ✅ LLM может использовать reasoning для лучшего понимания

**Ограничения:**
- ⏱️ Зависит от доступности Ollama сервера
- ⏱️ Время обработки зависит от размера модели и количества сообщений в диалоге
- ⚠️ Требует настройки Ollama сервера и модели

---

## Текущее состояние

### ✅ Что работает:

1. **Определение стратегий:**
   - 42 стратегии через иерархическую классификацию (LLM/Ollama)
   - 40 стратегий через RoBERTa-large-MNLI (альтернативный метод)
   - Учет контекста диалога (полный диалог для LLM, последние 4 сообщения для NLI)
   - Одна лучшая стратегия для каждого сообщения persuader

2. **Иерархическая классификация (LLM):**
   - Двухэтапный подход: сначала категория, потом стратегия
   - Batch-обработка диалогов
   - Пропуск уже обработанных сообщений
   - Использование полного контекста диалога

3. **Результаты:**
   - `test_batch_results.csv` - стратегии через LLM (иерархическая классификация)
   - `strategies_B4_0.csv` - стратегии для persuader (первая версия)
   - `full_dialog_with_nli_strategies.csv` - полный диалог со стратегиями (NLI)
   - `full_dialog_with_strategies_top1.csv` - объединенный результат

### Ограничения:

1. **Время выполнения:**
   - ~10,600 сообщений от persuader
   - × 40 стратегий
   - = ~424,000 вызовов модели
   - Примерно 12-60 часов (зависит от устройства)

2. **Точность:**
   - Зависит от качества гипотез стратегий
   - Порог 0.30 может пропускать некоторые стратегии
   - Контекст из 4 сообщений может быть недостаточным для длинных диалогов

3. **Одна стратегия:**
   - Иногда может использоваться несколько стратегий одновременно
   - Текущий подход возвращает только лучшую

---

## Метрики прогресса

| Этап | Метод | Стратегии | Контекст | Модель | Иерархия |
|------|-------|-----------|----------|--------|----------|
| 1 | Zero-shot (BART) | 45 | ❌ | BART-large-MNLI | ❌ |
| 2 | NLI с контекстом | 40 | ✅ (4 сообщения) | RoBERTa-large-MNLI | ❌ |
| 3 | Объединение | 40 | ✅ | RoBERTa-large-MNLI | ❌ |
| 5 | LLM (Ollama) | 42 | ✅ (полный диалог) | qwen3:30b | ✅ |

**Улучшения:**
- ✅ От zero-shot к прямому использованию NLI
- ✅ От одного сообщения к контексту диалога
- ✅ От множественных к одной стратегии
- ✅ Более точная модель (RoBERTa вместо BART)
- ✅ **Иерархическая классификация** (сначала категория, потом стратегия)
- ✅ **Batch-обработка** диалогов для эффективности
- ✅ **LLM reasoning** для лучшего понимания контекста

---

## Примеры стратегий

### Emotional Appeal
**Гипотеза:** "In this dialogue, the persuader uses an emotional appeal: they try to move the other person emotionally, for example by appealing to compassion, sadness, hope, or pride to get a donation."

### Social Proof
**Гипотеза:** "In this dialogue, the persuader uses social proof: they emphasize that many other people donate or support this cause, and therefore the listener should also donate."

### Urgency
**Гипотеза:** "In this dialogue, the persuader uses urgency: they stress that time is running out and that the donation must happen immediately."

### Moral Appeal
**Гипотеза:** "In this dialogue, the persuader uses a moral appeal: they argue that donating is morally right, good, or the ethically correct thing to do."

---

## Следующие шаги

1. **Оптимизация времени выполнения:**
   - Батчинг запросов к модели
   - Кэширование результатов
   - Параллельная обработка

2. **Улучшение точности:**
   - Настройка порога (0.30)
   - Эксперименты с размером контекста
   - Улучшение формулировок гипотез

3. **Множественные стратегии:**
   - Возвращать топ-3 стратегии вместо одной
   - Учитывать комбинации стратегий

---

## Файлы задачи

### Скрипты:
- `bsp2_first_roberta_for_strategies.py` - первая версия (zero-shot)
- `bsp2_my_roberta_for_strategies.py` - версия с NLI (RoBERTa-large-MNLI)
- `bsp2/llama_task3.py` - **иерархическая классификация через LLM (Ollama)** ⭐
- `bsp_adding_b0_b4.py` - объединение с диалогом
- `check_before_run.py` - проверка перед запуском
- `test_small_batch.py` - тестовый запуск

### Данные:
- `test_batch_results.csv` - **стратегии через LLM (иерархическая классификация)** ⭐
- `strategies_B4_0.csv` - стратегии для persuader (первая версия)
- `strategies_B4_0_top1.csv` - только лучшая стратегия
- `full_dialog_with_nli_strategies.csv` - полный диалог со стратегиями (NLI)
- `full_dialog_with_strategies_top1.csv` - объединенный результат

### Структура иерархии:
- `bsp2/strategies_hierarchical.py` - полная иерархическая структура (10 категорий, 42 стратегии)

---

*Задача 3: Определение стратегий убеждения - В РАЗРАБОТКЕ*
