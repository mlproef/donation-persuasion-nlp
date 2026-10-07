import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import STRATEGY_RESULTS, figure, result  # noqa: E402

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'classification'))
from strategies_hierarchical import STRATEGIES_INFO, STRATEGY_CATEGORIES

print("="*80)
print("DETAILED ANALYSIS OF RESULTS FROM llama_task3_single.py")
print("="*80)

# Load data
print("\n1. Loading data...")
df = pd.read_csv(str(STRATEGY_RESULTS))

print(f"   - Total rows: {len(df):,}")
print(f"   - Persuader messages (B4=0): {len(df[df['B4'] == 0]):,}")
print(f"   - User messages (B4=1): {len(df[df['B4'] == 1]):,}")

# Analyze strategies
persuader = df[df['B4'] == 0].copy()

strategies_filled = persuader[
    persuader['strategy_ollama_single'].notna() & 
    (persuader['strategy_ollama_single'].astype(str).str.strip() != '')
]

print(f"\n2. Strategy statistics:")
print(f"   - Total persuader messages: {len(persuader):,}")
print(f"   - Messages with strategies: {len(strategies_filled):,}")
print(f"   - Analysis coverage: {len(strategies_filled)/len(persuader)*100:.1f}%")
print(f"   - Messages without strategies: {len(persuader) - len(strategies_filled):,}")

# Create mapping from strategies to categories
strategy_to_category = {}
strategy_to_parent = {}
for strategy in STRATEGIES_INFO:
    strategy_to_category[strategy['name']] = strategy.get('parent_category', 'Unknown')
    strategy_to_parent[strategy['name']] = strategy.get('parent_id', 'unknown')

# Add categories
strategies_filled = strategies_filled.copy()
strategies_filled['category'] = strategies_filled['strategy_ollama_single'].map(strategy_to_category)
strategies_filled['parent_id'] = strategies_filled['strategy_ollama_single'].map(strategy_to_parent)

# ========= 1. STRATEGY DISTRIBUTION =========
print("\n" + "="*80)
print("STRATEGY DISTRIBUTION")
print("="*80)

strategy_counts = strategies_filled['strategy_ollama_single'].value_counts()
print(f"\nTotal unique strategies: {len(strategy_counts)}")
print(f"\nAll strategies (sorted by frequency):")

for i, (strategy, count) in enumerate(strategy_counts.items(), 1):
    pct = count / len(strategies_filled) * 100
    category = strategy_to_category.get(strategy, 'Unknown')
    print(f"   {i:2d}. {strategy:50s} | {category:30s} | {count:4d} ({pct:5.2f}%)")

# ========= 2. CATEGORY DISTRIBUTION =========
print("\n" + "="*80)
print("CATEGORY DISTRIBUTION")
print("="*80)

category_counts = strategies_filled['category'].value_counts()
print(f"\nTotal categories: {len(category_counts)}")
for cat, count in category_counts.items():
    pct = count / len(strategies_filled) * 100
    print(f"   {cat:40s}: {count:4d} ({pct:5.2f}%)")

# ========= 3. DIALOG ANALYSIS =========
print("\n" + "="*80)
print("DIALOG ANALYSIS")
print("="*80)

dialog_stats = []
for dialog_id in persuader['B2'].unique():
    dialog_data = persuader[persuader['B2'] == dialog_id]
    dialog_strategies = strategies_filled[strategies_filled['B2'] == dialog_id]
    
    dialog_stats.append({
        'B2': dialog_id,
        'total_messages': len(dialog_data),
        'messages_with_strategy': len(dialog_strategies),
        'coverage_pct': len(dialog_strategies) / len(dialog_data) * 100 if len(dialog_data) > 0 else 0,
        'unique_strategies': dialog_strategies['strategy_ollama_single'].nunique(),
    })

dialog_df = pd.DataFrame(dialog_stats)

print(f"\nTotal dialogs: {len(dialog_df)}")
print(f"Dialogs with at least one strategy: {(dialog_df['messages_with_strategy'] > 0).sum()}")
print(f"Average coverage percentage: {dialog_df['coverage_pct'].mean():.1f}%")
print(f"Average number of unique strategies per dialog: {dialog_df['unique_strategies'].mean():.2f}")

# ========= 4. STRATEGIES BY POSITION IN DIALOG =========
print("\n" + "="*80)
print("СТРАТЕГИИ ПО ПОЗИЦИИ В ДИАЛОГЕ")
print("="*80)

# Определяем позицию сообщения в диалоге
strategies_filled['turn_rank'] = strategies_filled.groupby('B2')['Turn'].rank(method='first')
strategies_filled['position'] = pd.cut(
    strategies_filled['turn_rank'],
    bins=[0, 1, 3, 6, 100],
    labels=['First', 'Early (2-3)', 'Middle (4-6)', 'Late (7+)']
)

print("\nРаспределение стратегий по позиции в диалоге:")
for position in ['First', 'Early (2-3)', 'Middle (4-6)', 'Late (7+)']:
    pos_data = strategies_filled[strategies_filled['position'] == position]
    if len(pos_data) > 0:
        top_strategies = pos_data['strategy_ollama_single'].value_counts().head(5)
        print(f"\n   {position}:")
        for strategy, count in top_strategies.items():
            print(f"      {strategy}: {count}")

# ========= 5. ВИЗУАЛИЗАЦИЯ =========
print("\n" + "="*80)
print("СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ")
print("="*80)

fig = plt.figure(figsize=(18, 12))

# График 1: Топ-20 стратегий
ax1 = plt.subplot(2, 3, 1)
top_20 = strategy_counts.head(20)
bars = ax1.barh(range(len(top_20)), top_20.values, color='steelblue')
ax1.set_yticks(range(len(top_20)))
ax1.set_yticklabels([s[:40] for s in top_20.index], fontsize=8)
ax1.set_xlabel('Count')
ax1.set_title('Top-20 Strategies', fontweight='bold')
ax1.invert_yaxis()
for i, (idx, val) in enumerate(top_20.items()):
    ax1.text(val, i, f' {val}', va='center', fontsize=7)

# График 2: Распределение по категориям
ax2 = plt.subplot(2, 3, 2)
colors_list = plt.cm.Set3(range(len(category_counts)))
bars2 = ax2.bar(range(len(category_counts)), category_counts.values, color=colors_list)
ax2.set_xticks(range(len(category_counts)))
ax2.set_xticklabels([cat[:15] for cat in category_counts.index], rotation=45, ha='right', fontsize=8)
ax2.set_ylabel('Count')
ax2.set_title('Distribution by Category', fontweight='bold')
for i, (cat, val) in enumerate(category_counts.items()):
    ax2.text(i, val, f' {val}', va='bottom', fontsize=8)

# График 3: Покрытие диалогов
ax3 = plt.subplot(2, 3, 3)
coverage_bins = [0, 10, 25, 50, 75, 90, 100]
coverage_labels = ['0-10%', '10-25%', '25-50%', '50-75%', '75-90%', '90-100%']
dialog_df['coverage_group'] = pd.cut(dialog_df['coverage_pct'], bins=coverage_bins, labels=coverage_labels)
coverage_counts = dialog_df['coverage_group'].value_counts().sort_index()
bars3 = ax3.bar(range(len(coverage_counts)), coverage_counts.values, color='coral')
ax3.set_xticks(range(len(coverage_counts)))
ax3.set_xticklabels(coverage_counts.index, rotation=45, ha='right')
ax3.set_ylabel('Number of Dialogs')
ax3.set_title('Dialog Coverage Distribution', fontweight='bold')
for i, (label, val) in enumerate(coverage_counts.items()):
    ax3.text(i, val, f' {val}', va='bottom', fontsize=8)

# График 4: Стратегии по позиции в диалоге
ax4 = plt.subplot(2, 3, 4)
position_strategy = pd.crosstab(strategies_filled['position'], strategies_filled['strategy_ollama_single'])
top_strategies_in_pos = position_strategy.sum().nlargest(10).index
position_strategy_filtered = position_strategy[top_strategies_in_pos]
position_strategy_filtered.plot(kind='bar', ax=ax4, stacked=False, width=0.8)
ax4.set_xlabel('Position in Dialog')
ax4.set_ylabel('Count')
ax4.set_title('Top-10 Strategies by Position', fontweight='bold')
ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=7)
ax4.tick_params(axis='x', rotation=45)
ax4.grid(axis='y', alpha=0.3)

# График 5: Круговая диаграмма категорий
ax5 = plt.subplot(2, 3, 5)
colors_pie = plt.cm.Set3(range(len(category_counts)))
wedges, texts, autotexts = ax5.pie(category_counts.values, labels=category_counts.index, 
                                   autopct='%1.1f%%', colors=colors_pie, startangle=90)
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(8)
for text in texts:
    text.set_fontsize(8)
ax5.set_title('Category Distribution (Pie Chart)', fontweight='bold')

# График 6: Уникальные стратегии на диалог
ax6 = plt.subplot(2, 3, 6)
unique_strategies_counts = dialog_df['unique_strategies'].value_counts().sort_index()
bars6 = ax6.bar(unique_strategies_counts.index, unique_strategies_counts.values, color='mediumseagreen')
ax6.set_xlabel('Number of Unique Strategies')
ax6.set_ylabel('Number of Dialogs')
ax6.set_title('Unique Strategies per Dialog', fontweight='bold')
for idx, val in unique_strategies_counts.items():
    ax6.text(idx, val, f' {val}', va='bottom', fontsize=8)

plt.tight_layout()
output_file = str(figure("task3_single_analysis.png"))
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nГрафик сохранен: {output_file}")

# ========= 6. СОХРАНЕНИЕ РЕЗУЛЬТАТОВ =========
print("\n" + "="*80)
print("СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
print("="*80)

# Детальная статистика по стратегиям
strategy_details = []
for strategy in strategy_counts.index:
    strategy_data = strategies_filled[strategies_filled['strategy_ollama_single'] == strategy]
    strategy_details.append({
        'strategy': strategy,
        'category': strategy_to_category.get(strategy, 'Unknown'),
        'count': len(strategy_data),
        'percentage': len(strategy_data) / len(strategies_filled) * 100,
        'dialogs_with_strategy': strategy_data['B2'].nunique(),
        'avg_per_dialog': len(strategy_data) / strategy_data['B2'].nunique() if strategy_data['B2'].nunique() > 0 else 0,
    })

strategy_details_df = pd.DataFrame(strategy_details).sort_values('count', ascending=False)
strategy_details_df.to_csv(str(result("task3_single_strategy_details.csv")), index=False)
print(f"Детали по стратегиям сохранены: task3_single_strategy_details.csv")

# Статистика по категориям
category_details = []
for category in category_counts.index:
    category_data = strategies_filled[strategies_filled['category'] == category]
    category_details.append({
        'category': category,
        'count': len(category_data),
        'percentage': len(category_data) / len(strategies_filled) * 100,
        'unique_strategies': category_data['strategy_ollama_single'].nunique(),
        'dialogs_with_category': category_data['B2'].nunique(),
    })

category_details_df = pd.DataFrame(category_details).sort_values('count', ascending=False)
category_details_df.to_csv(str(result("task3_single_category_details.csv")), index=False)
print(f"Детали по категориям сохранены: task3_single_category_details.csv")

# Статистика по диалогам
dialog_df.to_csv(str(result("task3_single_dialog_stats.csv")), index=False)
print(f"Статистика по диалогам сохранена: task3_single_dialog_stats.csv")

# Сводная статистика
summary = {
    'Metric': [
        'Total persuader messages',
        'Messages with strategy',
        'Coverage percentage',
        'Messages without strategy',
        'Unique strategies found',
        'Total categories',
        'Total dialogs',
        'Dialogs with at least one strategy',
        'Average coverage per dialog',
        'Average unique strategies per dialog',
    ],
    'Value': [
        len(persuader),
        len(strategies_filled),
        f"{len(strategies_filled)/len(persuader)*100:.1f}%",
        len(persuader) - len(strategies_filled),
        len(strategy_counts),
        len(category_counts),
        len(dialog_df),
        (dialog_df['messages_with_strategy'] > 0).sum(),
        f"{dialog_df['coverage_pct'].mean():.1f}%",
        f"{dialog_df['unique_strategies'].mean():.2f}",
    ]
}

summary_df = pd.DataFrame(summary)
summary_df.to_csv(str(result("task3_single_summary.csv")), index=False)
print(f"Сводная статистика сохранена: task3_single_summary.csv")

print("\n" + "="*80)
print("АНАЛИЗ ЗАВЕРШЕН")
print("="*80)

