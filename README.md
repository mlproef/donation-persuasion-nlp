# BSP2: Persuasion Dialogue Analysis

Project for analyzing persuasion dialogues where one participant (persuader) attempts to convince another (target) to make a donation.

## 📋 Project Description

The project solves three main tasks:

1. **Task 1: Sentiment Analysis**
   - Determining the overall emotional tone of communication in the dialogue
   - Classification: negative, neutral, positive
   - Uses `cardiffnlp/twitter-roberta-base-sentiment` model

2. **Task 2: Interest in Donation Classification**
   - Classifying target reactions: refusal/neutral/interested
   - Uses LLM (Ollama) for classification with full dialog context
   - Three categories: Not Interested (0), Neutral (1), Interested (2)

3. **Task 3: Persuasion Strategy Classification**
   - Identifying persuasion strategies used by the persuader
   - 42 strategies organized into 11 hierarchical categories
   - Uses hierarchical classification via LLM (Ollama)

## 🎯 Main Results

### Final Data
- `full_dialog_with_all_analysis.csv` - complete dialog with all analyses (sentiment, interest, strategies)

### Sentiment Analysis
- `sentiment_v2_summary.csv` - sentiment summary statistics
- `sentiment_v2_dialog_stats.csv` - dialog statistics
- `sentiment_v2_details.csv` - detailed information
- `sentiment_v2_analysis.png` - analysis visualization
- `sentiment_donation_correlation.png` - correlation between sentiment and donations

### Interest Analysis
- `interest_v2_summary.csv` - interest summary statistics
- `interest_v2_dialog_stats.csv` - dialog statistics
- `interest_v2_details.csv` - detailed information
- `interest_v2_analysis.png` - analysis visualization
- `interest_donation_correlation.png` - correlation between interest and donations
- `interest_donation_summary.csv` - donation correlation summary

### Strategy Analysis
- `task3_single_summary.csv` - strategy summary statistics
- `task3_single_dialog_stats.csv` - dialog statistics
- `task3_single_category_details.csv` - category details
- `task3_single_strategy_details.csv` - strategy details
- `task3_single_analysis.png` - analysis visualization
- `strategy_donation_stats.csv` - correlation between strategies and donations
- `strategy_interest_stats.csv` - correlation between strategies and interest
- `strategy_sentiment_stats.csv` - correlation between strategies and sentiment

### Donation Analysis
- `donation_dataset_stats.csv` - donation statistics
- `donation_analysis.png` - donation analysis visualization
- `donation_by_role.png` - donations by role
- `donation_amount_distribution.png` - donation amount distribution

### Joint Analysis
- `joint_strategies_stats.csv` - joint strategy effect statistics
- `joint_strategies_effect.png` - joint effect visualization

## 📁 Project Structure

```
bsp2/
├── README.md                          # This file
├── PROJECT_DOCUMENTATION.md            # Detailed project documentation
├── TASK1_SENTIMENT.md                  # Task 1 documentation
├── TASK2_INTEREST_IN_DONATION.md      # Task 2 documentation
├── TASK3_STRATEGIES.md                 # Task 3 documentation
├── strategies_sources.md               # Strategy sources
├── STRATEGIES_IMPROVEMENTS.md          # Strategy improvements
│
├── bsp2/                              # Main scripts
│   ├── llama_sentiment.py             # LLM sentiment classification
│   ├── llama_interest.py              # LLM interest classification
│   ├── llama_strategies.py            # LLM strategy classification
│   └── strategies_hierarchical.py     # Hierarchical strategy structure
│
├── analyze_*.py                        # Result analysis scripts
├── merge_all_analysis_results.py      # Merge all analyses
│
└── *.csv, *.png                       # Analysis results
```

## 🚀 Quick Start

### Installing Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Usage

1. **Running Analysis:**
   - Use scripts in `bsp2/` directory for classification
   - Use `analyze_*.py` scripts for result analysis

2. **Merging Results:**
   ```bash
   python merge_all_analysis_results.py
   ```

## 📊 Methods and Models

### Sentiment Analysis
- **Model:** `cardiffnlp/twitter-roberta-base-sentiment`
- **Method:** Pre-trained model for sentiment analysis

### Interest Classification
- **Model:** LLM via Ollama API (qwen3:30b)
- **Method:** Batch processing of dialogs with full context

### Strategy Classification
- **Model:** LLM via Ollama API (qwen3:30b)
- **Method:** Hierarchical classification (category first, then strategy)
- **Structure:** 11 categories, 42 strategies

## 📈 Results

All analysis results are saved in CSV files and visualized in PNG files. Main metrics:

- **Sentiment:** Sentiment distribution across dialogs
- **Interest:** Correlation between interest and donations
- **Strategies:** Effectiveness of various persuasion strategies
- **Donations:** Statistics and distribution of donations

## 📚 Documentation

Detailed documentation is available in:
- `PROJECT_DOCUMENTATION.md` - full project documentation
- `TASK1_SENTIMENT.md` - Task 1 details
- `TASK2_INTEREST_IN_DONATION.md` - Task 2 details
- `TASK3_STRATEGIES.md` - Task 3 details

## 🔧 Requirements

- Python 3.9+
- PyTorch
- Transformers
- Pandas, NumPy
- Matplotlib, Seaborn
- Ollama (for LLM classification)

## 📝 License

Project created for educational purposes.

## 👤 Author

BSP2 Project - Persuasion Dialogue Analysis
