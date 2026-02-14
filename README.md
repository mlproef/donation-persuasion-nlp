# BSP2: Анализ диалогов убеждения

Проект для анализа диалогов убеждения (persuasion dialogues), где один участник (persuader) пытается убедить другого (target) сделать пожертвование.

## 📋 Описание проекта

Проект решает три основные задачи:

1. **Задача 1: Анализ тональности (Sentiment Analysis)**
   - Определение общей тональности общения в диалоге
   - Классификация: negative, neutral, positive
   - Используется модель `cardiffnlp/twitter-roberta-base-sentiment`

2. **Задача 2: Определение заинтересованности в донате (Interest Classification)**
   - Классификация реакций убеждаемого: отказ/нейтрально/заинтересован
   - Используется LLM (Ollama) для классификации с учетом контекста диалога
   - Три категории: Not Interested (0), Neutral (1), Interested (2)

3. **Задача 3: Определение стратегий убеждения (Strategy Classification)**
   - Определение стратегий убеждения, используемых persuader'ом
   - 42 стратегии, организованные в 11 иерархических категорий
   - Используется иерархическая классификация через LLM (Ollama)

## 🎯 Основные результаты

### Финальные данные
- `full_dialog_with_all_analysis.csv` - полный диалог со всеми анализами (sentiment, interest, strategies)

### Анализ тональности
- `sentiment_v2_summary.csv` - сводная статистика по тональности
- `sentiment_v2_dialog_stats.csv` - статистика по диалогам
- `sentiment_v2_details.csv` - детальная информация
- `sentiment_v2_analysis.png` - визуализация анализа
- `sentiment_donation_correlation.png` - корреляция тональности и донатов

### Анализ заинтересованности
- `interest_v2_summary.csv` - сводная статистика по заинтересованности
- `interest_v2_dialog_stats.csv` - статистика по диалогам
- `interest_v2_details.csv` - детальная информация
- `interest_v2_analysis.png` - визуализация анализа
- `interest_donation_correlation.png` - корреляция заинтересованности и донатов
- `interest_donation_summary.csv` - сводка по корреляции с донатами

### Анализ стратегий
- `task3_single_summary.csv` - сводная статистика по стратегиям
- `task3_single_dialog_stats.csv` - статистика по диалогам
- `task3_single_category_details.csv` - детали по категориям
- `task3_single_strategy_details.csv` - детали по стратегиям
- `task3_single_analysis.png` - визуализация анализа
- `strategy_donation_stats.csv` - корреляция стратегий и донатов
- `strategy_interest_stats.csv` - корреляция стратегий и заинтересованности
- `strategy_sentiment_stats.csv` - корреляция стратегий и тональности

### Анализ донатов
- `donation_dataset_stats.csv` - статистика по донатам
- `donation_analysis.png` - визуализация анализа донатов
- `donation_by_role.png` - донаты по ролям
- `donation_amount_distribution.png` - распределение сумм донатов

### Совместный анализ
- `joint_strategies_stats.csv` - статистика совместного эффекта стратегий
- `joint_strategies_effect.png` - визуализация совместного эффекта

## 📁 Структура проекта

```
bsp2/
├── README.md                          # Этот файл
├── PROJECT_DOCUMENTATION.md            # Подробная документация проекта
├── TASK1_SENTIMENT.md                  # Документация задачи 1
├── TASK2_INTEREST_IN_DONATION.md      # Документация задачи 2
├── TASK3_STRATEGIES.md                 # Документация задачи 3
├── strategies_sources.md               # Источники стратегий
├── STRATEGIES_IMPROVEMENTS.md          # Улучшения стратегий
│
├── bsp2/                              # Основные скрипты
│   ├── llama_sentiment.py             # LLM классификация тональности
│   ├── llama_interest.py              # LLM классификация заинтересованности
│   ├── llama_strategies.py            # LLM классификация стратегий
│   ├── llama_task3.py                 # Иерархическая классификация стратегий
│   └── strategies_hierarchical.py     # Иерархическая структура стратегий
│
├── analyze_*.py                        # Скрипты анализа результатов
├── merge_all_analysis_results.py      # Объединение всех анализов
│
├── roberta_reaction_classifier/       # Обученная модель RoBERTa
│   └── best_model/                    # Лучшая модель
│
├── reaction_calibrator.joblib         # Калибратор реакций
│
├── 14feb/                             # Web интерфейс для визуализации
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── start_server.py
│
└── *.csv, *.png                       # Результаты анализа
```

## 🚀 Быстрый старт

### Установка зависимостей

```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Использование

1. **Запуск анализа:**
   - Используйте скрипты в директории `bsp2/` для классификации
   - Используйте скрипты `analyze_*.py` для анализа результатов

2. **Объединение результатов:**
   ```bash
   python merge_all_analysis_results.py
   ```

3. **Запуск web интерфейса:**
   ```bash
   cd 14feb
   python start_server.py
   ```

## 📊 Методы и модели

### Sentiment Analysis
- **Модель:** `cardiffnlp/twitter-roberta-base-sentiment`
- **Метод:** Предобученная модель для анализа тональности

### Interest Classification
- **Модель:** LLM через Ollama API (qwen3:30b)
- **Метод:** Batch-обработка диалогов с полным контекстом
- **Альтернатива:** Fine-tuned RoBERTa модель (в `roberta_reaction_classifier/`)

### Strategy Classification
- **Модель:** LLM через Ollama API (qwen3:30b)
- **Метод:** Иерархическая классификация (сначала категория, потом стратегия)
- **Структура:** 11 категорий, 42 стратегии

## 📈 Результаты

Все результаты анализа сохранены в CSV файлах и визуализированы в PNG файлах. Основные метрики:

- **Sentiment:** Распределение тональности по диалогам
- **Interest:** Корреляция заинтересованности с донатами
- **Strategies:** Эффективность различных стратегий убеждения
- **Donations:** Статистика и распределение донатов

## 📚 Документация

Подробная документация доступна в файлах:
- `PROJECT_DOCUMENTATION.md` - полная документация проекта
- `TASK1_SENTIMENT.md` - детали задачи 1
- `TASK2_INTEREST_IN_DONATION.md` - детали задачи 2
- `TASK3_STRATEGIES.md` - детали задачи 3

## 🔧 Требования

- Python 3.9+
- PyTorch
- Transformers
- Pandas, NumPy
- Matplotlib, Seaborn
- Ollama (для LLM классификации)

## 📝 Лицензия

Проект создан в образовательных целях.

## 👤 Автор

Проект BSP2 - анализ диалогов убеждения
