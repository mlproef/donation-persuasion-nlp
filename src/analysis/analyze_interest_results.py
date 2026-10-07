import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import INTEREST_RESULTS, figure, result  # noqa: E402

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("ANALYZING RESULTS FROM test_batch_interest_results.csv")
print("="*80)

# Load data
print("\n1. Loading data...")
df = pd.read_csv(str(INTEREST_RESULTS))

# Convert empty strings to NaN for proper checking
if "interest_ollama_v2" in df.columns:
    df["interest_ollama_v2"] = df["interest_ollama_v2"].replace("", pd.NA)
    df["interest_ollama_v2"] = df["interest_ollama_v2"].replace("nan", pd.NA)
    df["interest_ollama_v2"] = df["interest_ollama_v2"].replace("None", pd.NA)

print(f"   - Total rows: {len(df):,}")
print(f"   - Target messages (B4=1): {len(df[df['B4'] == 1]):,}")
print(f"   - Persuader messages (B4=0): {len(df[df['B4'] == 0]):,}")

# Analyze interest v2
target_messages = df[df['B4'] == 1].copy()

interest_filled = target_messages[
    target_messages['interest_ollama_v2'].notna() & 
    (target_messages['interest_ollama_v2'].astype(str).str.strip() != '')
]

print(f"\n2. Interest statistics (v2):")
print(f"   - Total target messages: {len(target_messages):,}")
print(f"   - Messages with interest: {len(interest_filled):,}")
if len(target_messages) > 0:
    print(f"   - Analysis coverage: {len(interest_filled)/len(target_messages)*100:.1f}%")
print(f"   - Messages without interest: {len(target_messages) - len(interest_filled):,}")

if len(interest_filled) == 0:
    print("\n⚠️ No data in interest_ollama_v2 for analysis!")
    print("   Run analysis first: python3 bsp2/test_batch_interest.py")
    exit(0)

# ========= 1. INTEREST DISTRIBUTION =========
print("\n" + "="*80)
print("INTEREST DISTRIBUTION (v2)")
print("="*80)

interest_counts = interest_filled['interest_ollama_v2'].value_counts()
print(f"\nTotal unique interests: {len(interest_counts)}")
print(f"\nDistribution:")

total = len(interest_filled)
for interest, count in interest_counts.items():
    pct = count / total * 100
    print(f"   {interest:20s}: {count:5d} ({pct:5.2f}%)")

# Save detailed statistics
interest_details = pd.DataFrame({
    'interest': interest_counts.index,
    'count': interest_counts.values,
    'percentage': (interest_counts.values / total * 100).round(2)
})
interest_details.to_csv(str(result("interest_v2_details.csv")), index=False)
print(f"\n✅ Detailed statistics saved to: interest_v2_details.csv")

# ========= 2. LABEL DISTRIBUTION =========
print("\n" + "="*80)
print("LABEL DISTRIBUTION (v2)")
print("="*80)

if "interest_label_ollama_v2" in interest_filled.columns:
    # Convert labels to numeric format
    interest_filled_labels = interest_filled.copy()
    interest_filled_labels['interest_label_ollama_v2'] = interest_filled_labels['interest_label_ollama_v2'].replace("", pd.NA)
    interest_filled_labels = interest_filled_labels[interest_filled_labels['interest_label_ollama_v2'].notna()]
    
    # Convert to numeric format
    interest_filled_labels['label_num'] = pd.to_numeric(interest_filled_labels['interest_label_ollama_v2'], errors='coerce')
    interest_filled_labels = interest_filled_labels[interest_filled_labels['label_num'].notna()]
    
    label_counts = interest_filled_labels['label_num'].value_counts().sort_index()
    label_names = {0: "Not Interested", 1: "Neutral", 2: "Interested"}
    
    print(f"\nLabel distribution:")
    for label, count in label_counts.items():
        label_int = int(label)
        label_name = label_names.get(label_int, f"Unknown ({label_int})")
        pct = count / len(interest_filled_labels) * 100
        print(f"   {label_int} ({label_name:20s}): {count:5d} ({pct:5.2f}%)")

# ========= 3. DIALOG ANALYSIS =========
print("\n" + "="*80)
print("DIALOG ANALYSIS")
print("="*80)

dialog_stats = []
for dialog_id in target_messages['B2'].unique():
    dialog_data = target_messages[target_messages['B2'] == dialog_id]
    dialog_interest = interest_filled[interest_filled['B2'] == dialog_id]
    
    dialog_stats.append({
        'B2': dialog_id,
        'total_messages': len(dialog_data),
        'messages_with_interest': len(dialog_interest),
        'coverage_pct': len(dialog_interest) / len(dialog_data) * 100 if len(dialog_data) > 0 else 0,
        'unique_interests': dialog_interest['interest_ollama_v2'].nunique() if len(dialog_interest) > 0 else 0,
    })

dialog_df = pd.DataFrame(dialog_stats)

print(f"\nВсего уникальных диалогов: {len(dialog_df)}")
print(f"Диалогов с хотя бы одним interest: {(dialog_df['messages_with_interest'] > 0).sum()}")
print(f"Средний процент покрытия: {dialog_df['coverage_pct'].mean():.1f}%")
print(f"Медианный процент покрытия: {dialog_df['coverage_pct'].median():.1f}%")

# Распределение покрытия
coverage_bins = [0, 25, 50, 75, 100]
coverage_labels = ['0-25%', '25-50%', '50-75%', '75-100%']
dialog_df['coverage_group'] = pd.cut(dialog_df['coverage_pct'], bins=coverage_bins, labels=coverage_labels)
print(f"\nРаспределение диалогов по покрытию:")
for label in coverage_labels:
    count = (dialog_df['coverage_group'] == label).sum()
    if count > 0:
        print(f"   {label}: {count} диалогов")

dialog_df.to_csv(str(result("interest_v2_dialog_stats.csv")), index=False)
print(f"\n✅ Статистика по диалогам сохранена в: interest_v2_dialog_stats.csv")

# ========= 4. INTEREST ПО ПОЗИЦИИ В ДИАЛОГЕ =========
print("\n" + "="*80)
print("INTEREST ПО ПОЗИЦИИ В ДИАЛОГЕ")
print("="*80)

# Определяем позицию сообщения в диалоге
interest_filled = interest_filled.copy()
interest_filled['turn_rank'] = interest_filled.groupby('B2')['Turn'].rank(method='first')
interest_filled['position'] = pd.cut(
    interest_filled['turn_rank'],
    bins=[0, 1, 3, 6, 100],
    labels=['First', 'Early (2-3)', 'Middle (4-6)', 'Late (7+)']
)

position_interest = pd.crosstab(interest_filled['position'], interest_filled['interest_ollama_v2'])
print("\nРаспределение interest по позиции в диалоге:")
print(position_interest)

# Проценты по позициям
print("\nПроценты по позициям:")
position_pct = position_interest.div(position_interest.sum(axis=1), axis=0) * 100
print(position_pct.round(1))

# ========= 5. ВИЗУАЛИЗАЦИЯ =========
print("\n" + "="*80)
print("СОЗДАНИЕ ВИЗУАЛИЗАЦИИ")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# Graph 1: Distribution by interest
ax1 = axes[0, 0]
colors = {'Not Interested': '#2ca02c', 'Neutral': '#ff7f0e', 'Interested': '#d62728'}  # Поменяли местами Not Interested и Interested
interest_order = ['Not Interested', 'Neutral', 'Interested']
interest_counts_ordered = [interest_counts.get(s, 0) for s in interest_order]
bars = ax1.bar(interest_order, interest_counts_ordered, 
               color=[colors.get(s, '#1f77b4') for s in interest_order], alpha=0.7)
ax1.set_xlabel('Interest Level', fontsize=11)
ax1.set_ylabel('Number of Messages', fontsize=11)
ax1.set_title('Distribution by Interest Level', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Add values on bars
for bar, count in zip(bars, interest_counts_ordered):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{count}\n({count/total*100:.1f}%)',
             ha='center', va='bottom', fontsize=9)

# Graph 2: Interest by position in dialog
ax2 = axes[0, 1]
position_interest.plot(kind='bar', stacked=True, ax=ax2, 
                        color=[colors.get(s, '#1f77b4') for s in interest_order if s in position_interest.columns])
ax2.set_xlabel('Position in Dialog', fontsize=11)
ax2.set_ylabel('Number of Messages', fontsize=11)
ax2.set_title('Interest by Position in Dialog', fontsize=12, fontweight='bold')
ax2.legend(title='Interest Level', loc='upper right', fontsize=9)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', alpha=0.3)

# Graph 3: Coverage distribution by dialogs
ax3 = axes[1, 0]
coverage_counts = dialog_df['coverage_group'].value_counts().sort_index()
ax3.bar(coverage_counts.index.astype(str), coverage_counts.values, color='#2ca02c', alpha=0.7)
ax3.set_xlabel('Coverage Percentage', fontsize=11)
ax3.set_ylabel('Number of Dialogs', fontsize=11)
ax3.set_title('Coverage Distribution by Dialogs', fontsize=12, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

# Graph 4: Percentage distribution by positions
ax4 = axes[1, 1]
position_pct.plot(kind='bar', ax=ax4, 
                   color=[colors.get(s, '#1f77b4') for s in interest_order if s in position_pct.columns],
                   width=0.8)
ax4.set_xlabel('Position in Dialog', fontsize=11)
ax4.set_ylabel('Percentage (%)', fontsize=11)
ax4.set_title('Percentage Distribution of Interest by Position', fontsize=12, fontweight='bold')
ax4.legend(title='Interest Level', loc='upper right', fontsize=9)
ax4.tick_params(axis='x', rotation=45)
ax4.grid(axis='y', alpha=0.3)
ax4.set_ylim([0, 100])

plt.tight_layout()
plt.savefig(str(figure("interest_v2_analysis.png")), dpi=300, bbox_inches='tight')
print(f"✅ Визуализация сохранена в: interest_v2_analysis.png")

# ========= 6. СВОДНАЯ СТАТИСТИКА =========
print("\n" + "="*80)
print("СВОДНАЯ СТАТИСТИКА")
print("="*80)

summary = {
    'metric': [
        'Всего target сообщений',
        'Проанализировано',
        'Процент покрытия',
        'Уникальных interest',
        'Уникальных диалогов',
        'Средний процент покрытия по диалогам',
        'Медианный процент покрытия по диалогам'
    ],
    'value': [
        len(target_messages),
        len(interest_filled),
        f"{len(interest_filled)/len(target_messages)*100:.1f}%",
        len(interest_counts),
        len(dialog_df),
        f"{dialog_df['coverage_pct'].mean():.1f}%",
        f"{dialog_df['coverage_pct'].median():.1f}%"
    ]
}

summary_df = pd.DataFrame(summary)
print("\n" + summary_df.to_string(index=False))
summary_df.to_csv(str(result("interest_v2_summary.csv")), index=False)
print(f"\n✅ Сводная статистика сохранена в: interest_v2_summary.csv")

print("\n" + "="*80)
print("✅ АНАЛИЗ ЗАВЕРШЕН")
print("="*80)
print("\nСозданные файлы:")
print("   - interest_v2_details.csv")
print("   - interest_v2_dialog_stats.csv")
print("   - interest_v2_summary.csv")
print("   - interest_v2_analysis.png")

