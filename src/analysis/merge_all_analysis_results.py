import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import ALL_ANALYSIS, FULL_DIALOG, INTEREST_RESULTS, SENTIMENT_RESULTS, STRATEGY_RESULTS  # noqa: E402

import pandas as pd
import os

print("="*80)
print("MERGING ALL ANALYSIS RESULTS")
print("="*80)

# Load base dialog file
print("\n1. Loading base dialog file...")
if not os.path.exists(str(FULL_DIALOG)):
    print("❌ Error: full_dialog.csv not found!")
    exit(1)

df_base = pd.read_csv(str(FULL_DIALOG))
print(f"   ✅ Loaded full_dialog.csv: {len(df_base)} rows, {len(df_base.columns)} columns")
print(f"   Columns: {list(df_base.columns)}")

# Load strategy results
print("\n2. Loading strategy results...")
if os.path.exists(str(STRATEGY_RESULTS)):
    df_strategies = pd.read_csv(str(STRATEGY_RESULTS))
    print(f"   ✅ Loaded test_batch_results_single.csv: {len(df_strategies)} rows")
    
    # Select only strategy column and merge keys
    strategy_cols = ['B2', 'Turn', 'B4', 'strategy_ollama_single']
    if 'strategy_ollama_single' in df_strategies.columns:
        df_strategies_merge = df_strategies[strategy_cols].copy()
        print(f"   ✅ Strategy column found: strategy_ollama_single")
    else:
        print(f"   ⚠️  Warning: strategy_ollama_single column not found")
        df_strategies_merge = None
else:
    print(f"   ⚠️  Warning: test_batch_results_single.csv not found, skipping strategies")
    df_strategies_merge = None

# Load sentiment results
print("\n3. Loading sentiment results...")
if os.path.exists(str(SENTIMENT_RESULTS)):
    df_sentiment = pd.read_csv(str(SENTIMENT_RESULTS))
    print(f"   ✅ Loaded test_batch_sentiment_results.csv: {len(df_sentiment)} rows")
    
    # Select only sentiment_v2 column and merge keys
    sentiment_cols = ['B2', 'Turn', 'B4', 'sentiment_ollama_v2']
    if 'sentiment_ollama_v2' in df_sentiment.columns:
        df_sentiment_merge = df_sentiment[sentiment_cols].copy()
        print(f"   ✅ Sentiment column found: sentiment_ollama_v2")
    else:
        print(f"   ⚠️  Warning: sentiment_ollama_v2 column not found")
        df_sentiment_merge = None
else:
    print(f"   ⚠️  Warning: test_batch_sentiment_results.csv not found, skipping sentiment")
    df_sentiment_merge = None

# Load interest results
print("\n4. Loading interest results...")
if os.path.exists(str(INTEREST_RESULTS)):
    df_interest = pd.read_csv(str(INTEREST_RESULTS))
    print(f"   ✅ Loaded test_batch_interest_results.csv: {len(df_interest)} rows")
    
    # Select only interest_v2 columns and merge keys
    interest_cols = ['B2', 'Turn', 'B4', 'interest_ollama_v2', 'interest_label_ollama_v2']
    available_cols = [col for col in interest_cols if col in df_interest.columns]
    if 'interest_ollama_v2' in df_interest.columns:
        df_interest_merge = df_interest[available_cols].copy()
        print(f"   ✅ Interest columns found: {[col for col in available_cols if 'interest' in col]}")
    else:
        print(f"   ⚠️  Warning: interest_ollama_v2 column not found")
        df_interest_merge = None
else:
    print(f"   ⚠️  Warning: test_batch_interest_results.csv not found, skipping interest")
    df_interest_merge = None

# Merge all data
print("\n5. Merging all data...")
df_merged = df_base.copy()

# Merge strategies
if df_strategies_merge is not None:
    print("   Merging strategies...")
    df_merged = df_merged.merge(
        df_strategies_merge[['B2', 'Turn', 'B4', 'strategy_ollama_single']],
        on=['B2', 'Turn', 'B4'],
        how='left',
        suffixes=('', '_strategy')
    )
    # Remove duplicate columns if any
    if 'strategy_ollama_single_strategy' in df_merged.columns:
        df_merged['strategy_ollama_single'] = df_merged['strategy_ollama_single_strategy'].fillna(df_merged['strategy_ollama_single'])
        df_merged = df_merged.drop(columns=['strategy_ollama_single_strategy'])
    print(f"   ✅ Strategies merged: {df_merged['strategy_ollama_single'].notna().sum()} rows with strategies")

# Merge sentiment
if df_sentiment_merge is not None:
    print("   Merging sentiment...")
    df_merged = df_merged.merge(
        df_sentiment_merge[['B2', 'Turn', 'B4', 'sentiment_ollama_v2']],
        on=['B2', 'Turn', 'B4'],
        how='left',
        suffixes=('', '_sentiment')
    )
    # Remove duplicate columns if any
    if 'sentiment_ollama_v2_sentiment' in df_merged.columns:
        df_merged['sentiment_ollama_v2'] = df_merged['sentiment_ollama_v2_sentiment'].fillna(df_merged.get('sentiment_ollama_v2', pd.Series()))
        df_merged = df_merged.drop(columns=['sentiment_ollama_v2_sentiment'])
    print(f"   ✅ Sentiment merged: {df_merged['sentiment_ollama_v2'].notna().sum()} rows with sentiment")

# Merge interest
if df_interest_merge is not None:
    print("   Merging interest...")
    interest_cols_to_merge = ['B2', 'Turn', 'B4'] + [col for col in df_interest_merge.columns if 'interest' in col]
    df_merged = df_merged.merge(
        df_interest_merge[interest_cols_to_merge],
        on=['B2', 'Turn', 'B4'],
        how='left',
        suffixes=('', '_interest')
    )
    # Remove duplicate columns if any
    for col in interest_cols_to_merge:
        if col != 'B2' and col != 'Turn' and col != 'B4':
            if f'{col}_interest' in df_merged.columns:
                df_merged[col] = df_merged[f'{col}_interest'].fillna(df_merged.get(col, pd.Series()))
                df_merged = df_merged.drop(columns=[f'{col}_interest'])
    print(f"   ✅ Interest merged: {df_merged['interest_ollama_v2'].notna().sum()} rows with interest")

# Save merged dataset
print("\n6. Saving merged dataset...")
output_file = str(ALL_ANALYSIS)
df_merged.to_csv(output_file, index=False)
print(f"   ✅ Saved to: {output_file}")
print(f"   Total rows: {len(df_merged)}")
print(f"   Total columns: {len(df_merged.columns)}")

# Statistics
print("\n" + "="*80)
print("MERGE STATISTICS")
print("="*80)

print(f"\nTotal rows in merged dataset: {len(df_merged):,}")

if 'strategy_ollama_single' in df_merged.columns:
    strategy_count = df_merged['strategy_ollama_single'].notna().sum()
    strategy_filled = (df_merged['strategy_ollama_single'] != '').sum()
    print(f"\nStrategies:")
    print(f"   Rows with strategy (not null): {strategy_count:,}")
    print(f"   Rows with strategy (filled): {strategy_filled:,}")
    print(f"   Coverage: {strategy_filled/len(df_merged)*100:.2f}%")

if 'sentiment_ollama_v2' in df_merged.columns:
    sentiment_count = df_merged['sentiment_ollama_v2'].notna().sum()
    sentiment_filled = (df_merged['sentiment_ollama_v2'] != '').sum()
    print(f"\nSentiment:")
    print(f"   Rows with sentiment (not null): {sentiment_count:,}")
    print(f"   Rows with sentiment (filled): {sentiment_filled:,}")
    print(f"   Coverage: {sentiment_filled/len(df_merged)*100:.2f}%")

if 'interest_ollama_v2' in df_merged.columns:
    interest_count = df_merged['interest_ollama_v2'].notna().sum()
    interest_filled = (df_merged['interest_ollama_v2'] != '').sum()
    print(f"\nInterest:")
    print(f"   Rows with interest (not null): {interest_count:,}")
    print(f"   Rows with interest (filled): {interest_filled:,}")
    print(f"   Coverage: {interest_filled/len(df_merged)*100:.2f}%")

# Show column list
print(f"\nColumns in merged dataset ({len(df_merged.columns)}):")
for i, col in enumerate(df_merged.columns, 1):
    print(f"   {i:2d}. {col}")

print("\n" + "="*80)
print("✅ MERGE COMPLETED SUCCESSFULLY")
print("="*80)
print(f"\nOutput file: {output_file}")
print(f"Total rows: {len(df_merged):,}")
print(f"Total columns: {len(df_merged.columns)}")
