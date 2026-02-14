# Эволюция структуры стратегий убеждения

## Обзор

Этот документ описывает эволюцию структуры стратегий убеждения от начального плоского списка из 45 стратегий до иерархической структуры с 11 категориями и 43 стратегиями, организованными по подклассам.

---

## Начальное состояние: Плоский список (45 стратегий)

### Этап 1: Первая версия

**Источник:** `bsp2_first_roberta_for_strategies.py`

**Характеристики:**
- **45 стратегий** в плоском списке
- Нет категоризации
- Нет иерархии
- Просто список названий стратегий

**Пример структуры:**
```python
strategies = [
    "Rewarding Activity",
    "Punishing Activity",
    "Expertise",
    "Activation of Personal Commitment",
    "Activation of Impersonal Commitment",
    "Liking",
    "Pre-giving",
    "Moral Appeal",
    # ... и еще 37 стратегий
]
```

**Проблемы:**
- ❌ Слишком много стратегий для выбора
- ❌ Нет группировки похожих стратегий
- ❌ Сложно различать похожие стратегии
- ❌ Нет метаданных (описания, маркеры, правила)

---

## Сокращение до 40 стратегий

### Этап 2: Оптимизация списка

**Источник:** `bsp2_my_roberta_for_strategies.py`

**Что изменили:**
- Убрали дубликаты и очень похожие стратегии
- Сократили с **45 до 40 стратегий**
- Добавили описания (descriptions) для каждой стратегии
- Добавили гипотезы (hypotheses) для NLI классификации

**Структура:**
```python
strategies_info = [
    {
        "name": "Rewarding Activity",
        "hypothesis": "In this dialogue, the persuader uses rewarding activity: ..."
    },
    # ... еще 39 стратегий
]
```

**Улучшения:**
- ✅ Меньше стратегий = быстрее классификация
- ✅ Убраны дубликаты
- ✅ Добавлены гипотезы для NLI

**Остающиеся проблемы:**
- ❌ Все еще плоский список
- ❌ Нет группировки по типам
- ❌ Нет иерархии для улучшения точности

---

## Создание иерархической структуры

### Этап 3: Иерархическая организация

**Источник:** `bsp2/strategies_hierarchical.py`

**Что сделали:**

1. **Создали 11 родительских категорий:**
   - Группировка стратегий по семантической близости
   - Каждая категория имеет определение и маркеры

2. **Организовали 43 стратегии по категориям:**
   - Каждая стратегия привязана к родительской категории
   - Добавлены подклассы внутри категорий

3. **Добавили метаданные:**
   - `parent_category` - название родительской категории
   - `parent_id` - ID категории
   - `subclass_id` - ID подкласса
   - `subclass_name` - название подкласса
   - `markers` - ключевые слова для быстрого определения
   - `decision_rules` - правила использования/избегания

---

## Итоговая структура

### 11 родительских категорий:

1. **Exchange / Incentives** (5 стратегий)
   - Rewarding Activity
   - Pre-giving
   - Reciprocity
   - Debt
   - Promise

2. **Authority / Expertise** (4 стратегии)
   - Expertise
   - Authority
   - Credibility Appeal
   - Authority Pressure

3. **Norms / Morality / Values** (5 стратегий)
   - Moral Appeal
   - Appeal to Values
   - Activation of Impersonal Commitment
   - Guilt Induction
   - Self-feeling Appeal

4. **Commitment / Consistency** (4 стратегии)
   - Activation of Personal Commitment
   - Commitment and Consistency
   - Foot-in-the-door
   - Door-in-the-face

5. **Social Influence** (3 стратегии)
   - Social Proof
   - Unity
   - Social Positioning

6. **Rational / Impact Appeal** (2 стратегии)
   - Rational Appeal
   - Logical Appeal

7. **Emotional Influence** (6 стратегий)
   - Emotional Appeal
   - Storytelling
   - Empathy Appeal
   - Sympathy Appeal
   - Fear Appeal
   - Emotional Manipulation

8. **Urgency / Scarcity** (3 стратегии)
   - Urgency
   - Scarcity
   - Scarcity Manipulation

9. **Threat / Pressure** (5 стратегий)
   - Threat
   - Aversive Stimulation
   - Punishing Activity
   - Overloading
   - Confusion Induction

10. **Call to Action** (2 стратегии)
    - Call to Action
    - Liking

11. **Framing & Presentation** (4 стратегии)
    - Framing
    - Loss Aversion Appeal
    - Bait-and-switch
    - Pretexting

**Всего: 43 стратегии**

### Полный список всех 43 стратегий:

1. Rewarding Activity
2. Pre-giving
3. Reciprocity
4. Debt
5. Promise
6. Expertise
7. Authority
8. Credibility Appeal
9. Authority Pressure
10. Moral Appeal
11. Appeal to Values
12. Activation of Impersonal Commitment
13. Guilt Induction
14. Self-feeling Appeal
15. Activation of Personal Commitment
16. Commitment and Consistency
17. Foot-in-the-door
18. Door-in-the-face
19. Social Proof
20. Unity
21. Social Positioning
22. Rational Appeal
23. Logical Appeal
24. Emotional Appeal
25. Storytelling
26. Empathy Appeal
27. Sympathy Appeal
28. Fear Appeal
29. Emotional Manipulation
30. Urgency
31. Scarcity
32. Scarcity Manipulation
33. Threat
34. Aversive Stimulation
35. Punishing Activity
36. Overloading
37. Confusion Induction
38. Call to Action
39. Liking
40. Framing
41. Loss Aversion Appeal
42. Bait-and-switch
43. Pretexting

---

## Структура данных стратегии

Каждая стратегия теперь содержит:

```python
{
    "name": "Rewarding Activity",                    # Название стратегии
    "description": "persuader promises...",          # Описание
    "parent_category": "Exchange / Incentives",      # Родительская категория
    "parent_id": "exchange",                         # ID категории
    "subclass_id": "reward_benefit",                 # ID подкласса
    "subclass_name": "Reward / Benefit (Conditional Reward)",  # Название подкласса
    "markers": ["if you donate", "you'll get", ...], # Ключевые слова
    "decision_rules": {                              # Правила использования
        "use_if": [...],                            # Когда использовать
        "avoid_if": [...]                           # Когда избегать
    }
}
```

---

## Структура категорий

Каждая категория содержит:

```python
{
    "name": "Exchange / Incentives",                # Название категории
    "definition": "Donation request framed as...", # Определение
    "parent_markers": ["in exchange", "you'll get", ...],  # Маркеры категории
    "strategies": ["Rewarding Activity", ...]       # Список стратегий в категории
}
```

---

## Преимущества иерархической структуры

### 1. **Двухэтапная классификация:**
   - Сначала определяется категория (11 вариантов)
   - Затем стратегия внутри категории (3-6 вариантов)
   - Это сужает выбор и повышает точность

### 2. **Метаданные для улучшения классификации:**
   - **Markers** - помогают быстро определить стратегию по ключевым словам
   - **Decision rules** - четкие правила, когда использовать/избегать стратегию
   - **Subclasses** - группировка похожих стратегий

### 3. **Организация и понимание:**
   - Легче понять структуру стратегий
   - Видно семантические связи между стратегиями
   - Упрощает анализ результатов

### 4. **Гибкость использования:**
   - Можно использовать только категории (11 классов)
   - Можно использовать полную иерархию (43 стратегии)
   - Можно использовать подклассы для детализации

---

## Эволюция количества стратегий

| Этап | Количество | Структура | Метаданные |
|------|------------|-----------|------------|
| Начало | 45 | Плоский список | ❌ |
| Оптимизация | 40 | Плоский список | ✅ Описания, гипотезы |
| Иерархия | 43 | 11 категорий, подклассы | ✅ Полные метаданные |

**Примечание:** Количество увеличилось с 40 до 43, потому что:
- Добавлены некоторые стратегии, которые были упущены
- Некоторые стратегии разделены на варианты (например, Promise как вариант Rewarding Activity)

---

## Использование иерархической структуры

### В LLM классификации (`llama_task3.py`):

1. **Формируется иерархическая структура для промпта:**
   ```python
   hierarchical_structure = []
   for cat_id, cat_info in STRATEGY_CATEGORIES.items():
       strategies_in_category = [s for s in STRATEGIES_INFO if s.get('parent_id') == cat_id]
       hierarchical_structure.append({
           'category_name': cat_info['name'],
           'category_definition': cat_info['definition'],
           'strategies': [s['name'] for s in strategies_in_category]
       })
   ```

2. **Промпт явно требует двухэтапную классификацию:**
   - Сначала выбрать категорию
   - Затем выбрать стратегию внутри категории

3. **Это улучшает точность:**
   - LLM видит структуру и понимает связи
   - Сужение выбора снижает ошибки
   - Метаданные помогают в принятии решений

---

## Примеры организации

### Пример 1: Exchange / Incentives

**Категория:** Exchange / Incentives
- **Определение:** Donation request framed as an exchange: reward, gift, return favor, or owed obligation.
- **Маркеры:** "in exchange", "for donation", "you'll get", "discount", "gift", "owe"

**Стратегии в категории:**
1. **Rewarding Activity** (subclass: reward_benefit)
   - Маркеры: "if you donate", "you'll get", "access", "prize"
   - Использовать: когда есть условные выгоды
   - Избегать: если нет элемента обмена

2. **Pre-giving** (subclass: pre_giving)
   - Маркеры: "I already did", "I helped you", "here you go"
   - Использовать: когда подарок уже дан
   - Избегать: если только обещана награда

3. **Reciprocity** (subclass: reciprocity)
   - Маркеры: "remember I", "helped you out", "mutually"
   - Использовать: когда напоминают о взаимности
   - Избегать: если прямое "ты должен"

4. **Debt** (subclass: debt_owed)
   - Маркеры: "you owe", "you must", "in debt", "pay back"
   - Использовать: когда есть элемент долга
   - Избегать: если только моральный долг

5. **Promise** (subclass: reward_benefit - вариант)
   - Маркеры: "I promise", "I guarantee", "you'll get"
   - Использовать: когда есть явное обещание выгоды
   - Избегать: если нет элемента обмена

### Пример 2: Emotional Influence

**Категория:** Emotional Influence
- **Определение:** Uses emotions: empathy, pity, stories, emotional pressure.
- **Маркеры:** "pity", "suffering", "heart", "imagine", "crying", "story", "pain"

**Стратегии в категории:**
1. **Emotional Appeal** (subclass: empathy)
2. **Storytelling** (subclass: story)
3. **Empathy Appeal** (subclass: empathy)
4. **Sympathy Appeal** (subclass: sympathy)
5. **Fear Appeal** (subclass: sympathy - эмоциональный вариант)
6. **Emotional Manipulation** (subclass: sympathy)

---

## Ключевые изменения

### 1. От плоского к иерархическому:
- **Было:** 45 стратегий в одном списке
- **Стало:** 11 категорий → 43 стратегии → подклассы

### 2. Добавление метаданных:
- **Было:** Только название
- **Стало:** Описание, маркеры, правила, подклассы

### 3. Организация по семантике:
- **Было:** Алфавитный/случайный порядок
- **Стало:** Группировка по типам влияния

### 4. Двухэтапная классификация:
- **Было:** Выбор из 40-45 стратегий сразу
- **Стало:** Сначала категория (11 вариантов), потом стратегия (3-6 вариантов)

---

## Статистика структуры

- **Всего категорий:** 11
- **Всего стратегий:** 43
- **Среднее стратегий на категорию:** ~3.9
- **Минимум стратегий в категории:** 2 (Rational / Impact Appeal, Call to Action)
- **Максимум стратегий в категории:** 6 (Emotional Influence)

**Распределение по категориям:**
- Exchange / Incentives: 5 стратегий
- Authority / Expertise: 4 стратегии
- Norms / Morality / Values: 5 стратегий
- Commitment / Consistency: 4 стратегии
- Social Influence: 3 стратегии
- Rational / Impact Appeal: 2 стратегии
- Emotional Influence: 6 стратегий
- Urgency / Scarcity: 3 стратегии
- Threat / Pressure: 5 стратегий
- Call to Action: 2 стратегии
- Framing & Presentation: 4 стратегии

---

## Использование в коде

### Импорт структуры:

```python
from bsp2.strategies_hierarchical import STRATEGIES_INFO, STRATEGY_CATEGORIES
```

### Доступ к стратегиям:

```python
# Все стратегии
for strategy in STRATEGIES_INFO:
    print(strategy["name"])
    print(strategy["parent_category"])
    print(strategy["subclass_name"])

# Стратегии в категории
strategies_in_category = [
    s for s in STRATEGIES_INFO 
    if s.get('parent_id') == 'exchange'
]

# Категории
for cat_id, cat_info in STRATEGY_CATEGORIES.items():
    print(cat_info["name"])
    print(cat_info["definition"])
```

---

## Преимущества для классификации

1. **Повышение точности:**
   - Двухэтапный подход сужает выбор
   - Метаданные помогают LLM принимать решения
   - Четкие правила уменьшают путаницу

2. **Улучшение понимания:**
   - Видна семантическая структура
   - Легче анализировать результаты
   - Понятна связь между стратегиями

3. **Гибкость:**
   - Можно использовать только категории
   - Можно использовать полную иерархию
   - Можно добавлять новые стратегии в существующие категории

---

## Файлы

- **`bsp2/strategies_hierarchical.py`** - полная иерархическая структура
  - `STRATEGIES_INFO` - список всех 43 стратегий с метаданными
  - `STRATEGY_CATEGORIES` - структура 11 категорий

---

*Документ создан: декабрь 2024*

