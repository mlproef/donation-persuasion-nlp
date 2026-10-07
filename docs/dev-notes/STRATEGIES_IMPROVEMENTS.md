# Рекомендации по улучшению стратегий для лучшей дифференциации

## 🔍 Обнаруженные проблемы

### 1. КРИТИЧЕСКИЕ: Одинаковые маркеры в разных стратегиях

#### Проблема A: Sympathy Appeal vs Emotional Manipulation
**Текущие маркеры одинаковые:**
- Sympathy Appeal: `["poor thing", "unfortunate", "pity", "no strength", "terrible to see"]`
- Emotional Manipulation: `["poor thing", "unfortunate", "pity", "no strength", "terrible to see"]`
- Fear Appeal: `["poor thing", "unfortunate", "pity", "no strength", "terrible to see", "danger", "threat"]`

**Решение:**
- **Sympathy Appeal**: Добавить маркеры, связанные с сочувствием к другим: `["feel sorry for", "my suffering", "their hardship", "helpless", "in need", "struggling"]`
- **Emotional Manipulation**: Добавить маркеры манипуляции: `["you don't care", "heartless", "cruel", "selfish", "if you had a heart", "manipulative language"]`
- **Fear Appeal**: Сфокусировать на страхе/опасности: `["danger", "threat", "will happen", "could happen", "risks", "consequences", "terrible outcome"]`

#### Проблема B: Scarcity vs Scarcity Manipulation
**Текущие маркеры одинаковые:**
- Scarcity: `["limited", "limit", "spots", "only N", "matching", "quota"]`
- Scarcity Manipulation: `["limited", "limit", "spots", "only N", "matching", "quota"]`

**Решение:**
- **Scarcity**: Добавить конкретные индикаторы реальной нехватки: `["limited spots", "only 5 left", "last 10", "few remaining", "running out", "almost gone"]`
- **Scarcity Manipulation**: Добавить индикаторы искусственности: `["hurry up", "act now", "limited time offer", "exclusive", "special offer", "artificial urgency"]`

### 2. Слишком общие маркеры

#### Проблема: Pretexting
**Текущие маркеры:** `["I", "we", "situation"]` - слишком общие

**Решение:**
Добавить более специфичные маркеры:
- `["I'm calling from", "we are contacting", "I represent", "we're reaching out", "on behalf of", "supposedly", "claims to be", "pretends to be"]`

#### Проблема: Rational Appeal
**Текущие маркеры:** `["%", "€", "$", "rub", "according to data"]` - только символы валют

**Решение:**
Расширить маркеры:
- `["statistics", "data shows", "research indicates", "studies show", "numbers prove", "percentage", "according to studies", "scientific evidence"]`

### 3. Пустые или слабые avoid_if правила

#### Проблема: Reciprocity
**Текущий avoid_if:** `[]` (пусто)

**Решение:**
Добавить четкие правила:
```python
"avoid_if": [
    "Gift/favor was just given now (use Pre-giving)", 
    "Explicit 'you owe me' language (use Debt)",
    "Only social obligation without personal favor (use Social Proof)"
]
```

### 4. Одинаковые use_if правила в группах

#### Проблема: Все стратегии Exchange имеют одинаковый use_if
**Текущий:** `"Text contains conditional benefits, gifts, return-favor reminders, or 'you owe' framing."`

**Решение:** Уточнить для каждой стратегии:

- **Rewarding Activity**: `"Text promises future benefit/reward IF person donates (conditional on donation)."`
- **Pre-giving**: `"Text mentions gift/favor that was ALREADY given (past tense), then asks for donation."`
- **Reciprocity**: `"Text reminds of past mutual help/favor without explicit gift, suggests return favor."`
- **Debt**: `"Text explicitly states person OWES something or uses debt/obligation language."`
- **Promise**: `"Text makes explicit promise of benefit IF donation happens (future conditional)."`

### 5. Слабая дифференциация похожих стратегий

#### Проблема A: Authority vs Expertise vs Credibility Appeal
Все три используют одинаковый `use_if`: `"Text emphasizes credentials, official role, institutional backing, proofs/reports."`

**Решение:**
- **Expertise**: `"Text emphasizes personal knowledge, experience, or professional expertise (first-person: 'I know', 'I've seen', 'in my experience')."`
- **Authority**: `"Text emphasizes official position, institutional role, or organizational status ('I represent', 'official collection', 'we are')."`
- **Credibility Appeal**: `"Text emphasizes transparency, verifiability, or trustworthiness ('you can check', 'transparent', 'can verify', 'receipts available')."`

#### Проблема B: Emotional Appeal vs Empathy Appeal vs Sympathy Appeal
**Решение:**
- **Emotional Appeal** (общий): `"Text uses emotional language to create feeling without specific technique (general emotional appeal)."`
- **Empathy Appeal**: `"Text explicitly asks person to IMAGINE being in another's situation ('imagine if', 'what if it were you', 'put yourself in their shoes')."`
- **Sympathy Appeal**: `"Text describes suffering/hardship to make person FEEL SORRY without imagination prompt (descriptive pity)."`

### 6. Неточные описания (descriptions)

#### Проблема: Некоторые descriptions недостаточно специфичны

**Улучшения:**
- **Promise** (строка 59): Добавить различие с Rewarding Activity - Promise более формальное и явное
- **Fear Appeal** (строка 370): Уточнить, что это про опасность для других, не для самого донатора
- **Pretexting** (строка 573): Уточнить, что это ложная роль/сценарий, не просто рассказ

## 📋 Рекомендуемые изменения

### Приоритет 1 (Критичные - мешают классификации):

1. **Разделить маркеры** между Sympathy Appeal, Emotional Manipulation и Fear Appeal
2. **Разделить маркеры** между Scarcity и Scarcity Manipulation
3. **Добавить avoid_if** для Reciprocity
4. **Уточнить use_if** правила для стратегий Exchange категории
5. **Разделить use_if** правила для Authority/Expertise/Credibility Appeal

### Приоритет 2 (Важные - улучшат точность):

6. **Расширить маркеры** для Pretexting (добавить более специфичные)
7. **Расширить маркеры** для Rational Appeal (добавить слова, не только символы)
8. **Уточнить use_if** для Emotional стратегий (Empathy vs Sympathy vs General)
9. **Улучшить descriptions** для лучшего понимания различий

### Приоритет 3 (Желательные - дополнительные улучшения):

10. Добавить **примеры сообщений** для каждой стратегии (в комментариях)
11. Добавить **частые путаницы** (common confusions) для каждой стратегии
12. Улучшить **decision_rules** для всех стратегий с более конкретными критериями

## 🎯 Примеры улучшенных стратегий

### Пример 1: Sympathy Appeal (улучшенная версия)
```python
{
    "name": "Sympathy Appeal",
    "description": "persuader highlights their own suffering or the hardship of others to make the listener feel sorry and want to donate.",
    "markers": ["feel sorry for", "their suffering", "my hardship", "helpless", "in need", "struggling", "poor thing", "unfortunate situation", "terrible to see"],
    "decision_rules": {
        "use_if": ["Text describes suffering/hardship to elicit pity/sympathy without asking person to imagine themselves in that situation."],
        "avoid_if": [
            "Text asks person to IMAGINE being in another's situation (use Empathy Appeal).",
            "Text uses guilt/shame language directly (use Guilt Induction).",
            "Text manipulates emotions with coercion (use Emotional Manipulation).",
            "Text describes danger/threat rather than suffering (use Fear Appeal)."
        ]
    }
}
```

### Пример 2: Emotional Manipulation (улучшенная версия)
```python
{
    "name": "Emotional Manipulation",
    "description": "persuader strategically shifts moods, exaggerates emotions, or exploits the other person's feelings to push them toward donating.",
    "markers": ["you don't care", "heartless", "cruel", "selfish", "if you had a heart", "how can you not", "you're being", "manipulative pressure"],
    "decision_rules": {
        "use_if": ["Text manipulates emotions with coercion, attacks person's character, or uses emotional blackmail to force donation."],
        "avoid_if": [
            "Text just describes suffering without attacking (use Sympathy Appeal).",
            "Text asks to imagine situation (use Empathy Appeal).",
            "Text uses shame/guilt about actions, not character attack (use Guilt Induction)."
        ]
    }
}
```

## 📝 Дополнительные рекомендации

1. **Добавить negative examples** (что НЕ является этой стратегией) в descriptions
2. **Использовать более конкретные маркеры** вместо общих слов
3. **Добавить контекстные маркеры** (например, не только слова, но и структура предложения)
4. **Улучшить иерархию** - некоторые стратегии могут быть подтипами других

