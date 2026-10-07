import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import FULL_INFO, INTEREST_RESULTS, figure, interim, result  # noqa: E402

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("АНАЛИЗ КОРРЕЛЯЦИИ МЕЖДУ INTEREST И DONATION")
print("="*80)

# Загружаем данные
print("\n1. Загружаем данные...")
interest_df = pd.read_csv(str(INTEREST_RESULTS))
info_df = pd.read_csv(str(FULL_INFO))

# Очищаем данные interest
interest_df["interest_ollama_v2"] = interest_df["interest_ollama_v2"].replace("", pd.NA).replace("nan", pd.NA).replace("None", pd.NA)

print(f"   - Загружено {len(interest_df)} строк из test_batch_interest_results.csv")
print(f"   - Загружено {len(info_df)} строк из full_info.csv")

# Объединяем данные
print("\n2. Объединяем данные...")
# Берем только target сообщения с interest
target_interest = interest_df[interest_df['B4'] == 1].copy()
target_interest = target_interest[target_interest['interest_ollama_v2'].notna() & 
                                  (target_interest['interest_ollama_v2'].astype(str).str.strip() != '')]

# Объединяем с информацией о донатах по диалогам
dialog_donations = info_df.groupby('B2').agg({
    'B6': ['sum', 'max', 'count']
}).reset_index()
dialog_donations.columns = ['B2', 'total_donation', 'max_donation', 'n_people']
dialog_donations['donated'] = (dialog_donations['total_donation'] > 0).astype(int)

# Анализ по диалогам: максимальный interest level в диалоге
print("\n3. Анализ по диалогам...")
dialog_interest_stats = []
for dialog_id in target_interest['B2'].unique():
    dialog_data = target_interest[target_interest['B2'] == dialog_id]
    
    # Подсчитываем количество каждого interest level
    interest_counts = dialog_data['interest_ollama_v2'].value_counts()
    
    # Определяем максимальный interest level
    interest_levels = {'Not Interested': 0, 'Neutral': 1, 'Interested': 2}
    max_interest_level = max([interest_levels.get(interest, 1) for interest in interest_counts.index])
    max_interest_name = [k for k, v in interest_levels.items() if v == max_interest_level][0]
    
    # Подсчитываем количество каждого типа
    n_not_interested = interest_counts.get('Not Interested', 0)
    n_neutral = interest_counts.get('Neutral', 0)
    n_interested = interest_counts.get('Interested', 0)
    
    # Есть ли отказы
    has_refusal = (n_not_interested > 0)
    
    # Процент interested
    total_messages = len(dialog_data)
    interested_rate = (n_interested / total_messages * 100) if total_messages > 0 else 0
    
    # Получаем информацию о донате
    donation_info = dialog_donations[dialog_donations['B2'] == dialog_id]
    if len(donation_info) > 0:
        donated = donation_info.iloc[0]['donated']
        donation_amount = donation_info.iloc[0]['max_donation']
    else:
        donated = 0
        donation_amount = 0.0
    
    dialog_interest_stats.append({
        'B2': dialog_id,
        'donated': donated,
        'donation_amount': donation_amount,
        'max_interest_level': max_interest_level,
        'max_interest_name': max_interest_name,
        'n_not_interested': n_not_interested,
        'n_neutral': n_neutral,
        'n_interested': n_interested,
        'has_refusal': has_refusal,
        'interested_rate': interested_rate,
        'n_messages': total_messages
    })

dialog_stats_df = pd.DataFrame(dialog_interest_stats)
dialog_stats_df.to_csv(str(interim("interest_donation_by_dialog.csv")), index=False)
print(f"   ✅ Статистика по диалогам сохранена в: interest_donation_by_dialog.csv")

# ========= 1. DONATION RATE BY MAXIMUM INTEREST LEVEL =========
print("\n" + "="*80)
print("DONATION RATE BY MAXIMUM INTEREST LEVEL")
print("="*80)

donation_by_max_interest = dialog_stats_df.groupby('max_interest_name').agg({
    'donated': ['sum', 'count', 'mean'],
    'donation_amount': ['mean', 'sum']
}).round(2)

donation_by_max_interest.columns = ['donated_count', 'total_dialogs', 'donation_rate', 'avg_donation', 'total_donation']
donation_by_max_interest['donation_rate_pct'] = (donation_by_max_interest['donation_rate'] * 100).round(1)

print("\nСтатистика по максимальному interest level в диалоге:")
print(donation_by_max_interest)

# ========= 2. CONTINGENCY MATRIX: INTEREST X DONATION =========
print("\n" + "="*80)
print("CONTINGENCY MATRIX: INTEREST X DONATION")
print("="*80)

# Создаем contingency matrix
contingency = pd.crosstab(dialog_stats_df['max_interest_name'], dialog_stats_df['donated'], 
                          margins=True, margins_name="Total")
contingency.columns = ['No Donation', 'Donation', 'Total']

print("\nContingency Matrix (Interest × Donation):")
print(contingency)

# Процентные значения
contingency_pct = pd.crosstab(dialog_stats_df['max_interest_name'], dialog_stats_df['donated'], 
                               normalize='index') * 100
contingency_pct.columns = ['No Donation %', 'Donation %']
print("\nContingency Matrix (Percentages):")
print(contingency_pct.round(1))

# ========= 3. REFUSALS X DONATION =========
print("\n" + "="*80)
print("REFUSALS X DONATION")
print("="*80)

refusal_donation = pd.crosstab(dialog_stats_df['has_refusal'], dialog_stats_df['donated'], 
                               margins=True, margins_name="Total")
refusal_donation.columns = ['No Donation', 'Donation', 'Total']
refusal_donation.index = ['No Refusal', 'Has Refusal', 'Total']

print("\nContingency Matrix (Refusals × Donation):")
print(refusal_donation)

refusal_donation_pct = pd.crosstab(dialog_stats_df['has_refusal'], dialog_stats_df['donated'], 
                                   normalize='index') * 100
refusal_donation_pct.columns = ['No Donation %', 'Donation %']
refusal_donation_pct.index = ['No Refusal', 'Has Refusal']
print("\nContingency Matrix (Percentages):")
print(refusal_donation_pct.round(1))

# ========= 4. СВОДНАЯ СТАТИСТИКА =========
print("\n" + "="*80)
print("СВОДНАЯ СТАТИСТИКА")
print("="*80)

total_dialogs = len(dialog_stats_df)
dialogs_with_donation = dialog_stats_df['donated'].sum()
overall_donation_rate = (dialogs_with_donation / total_dialogs * 100) if total_dialogs > 0 else 0

summary_stats = {
    'Metric': [
        'Total dialogs',
        'Dialogs with donation',
        'Overall donation rate',
        'Donation rate (Not Interested max)',
        'Donation rate (Neutral max)',
        'Donation rate (Interested max)',
        'Donation rate (with refusals)',
        'Donation rate (without refusals)'
    ],
    'Value': [
        total_dialogs,
        dialogs_with_donation,
        f"{overall_donation_rate:.2f}%",
        f"{donation_by_max_interest.loc['Not Interested', 'donation_rate_pct']:.2f}%",
        f"{donation_by_max_interest.loc['Neutral', 'donation_rate_pct']:.2f}%",
        f"{donation_by_max_interest.loc['Interested', 'donation_rate_pct']:.2f}%",
        f"{refusal_donation_pct.loc['Has Refusal', 'Donation %']:.2f}%",
        f"{refusal_donation_pct.loc['No Refusal', 'Donation %']:.2f}%"
    ]
}

summary_df = pd.DataFrame(summary_stats)
print("\n" + summary_df.to_string(index=False))
summary_df.to_csv(str(result("interest_donation_summary.csv")), index=False)
print(f"\n✅ Сводная статистика сохранена в: interest_donation_summary.csv")

# ========= 5. ВИЗУАЛИЗАЦИЯ =========
print("\n" + "="*80)
print("СОЗДАНИЕ ВИЗУАЛИЗАЦИИ")
print("="*80)

# Создаем отдельные графики

# График 1: Donation Rate by Maximum Interest Level (Bar Chart) - отдельный файл
fig1 = plt.figure(figsize=(8, 6))
ax1 = fig1.add_subplot(111)
interest_order = ['Not Interested', 'Neutral', 'Interested']
interest_labels = ['0', '1', '2']  # Labels как на изображении
donation_rates = [donation_by_max_interest.loc[interest, 'donation_rate_pct'] for interest in interest_order]
colors = ['#ffffff', '#ff7f0e', '#2ca02c']  # Белый, оранжевый, зеленый как на изображении
bars = ax1.bar(interest_labels, donation_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
ax1.set_ylabel('Donation Rate (%)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Maximum Interest Level', fontsize=12, fontweight='bold')
ax1.set_title('Donation Rate by Maximum Interest Level', fontsize=14, fontweight='bold', pad=20)
ax1.set_ylim(0, 100)
ax1.set_yticks([0, 20, 40, 60, 80, 100])
ax1.grid(axis='y', alpha=0.3, linestyle='--')
for bar, rate, label in zip(bars, donation_rates, interest_order):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{rate:.1f}%',
             ha='center', va='bottom', fontsize=12, fontweight='bold')
    # Добавляем подписи под осями
    ax1.text(bar.get_x() + bar.get_width()/2., -5,
             label,
             ha='center', va='top', fontsize=10, style='italic')

plt.tight_layout()
plt.savefig(str(figure("interest_donation_rate_by_level.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 1 сохранен: interest_donation_rate_by_level.png")
plt.close(fig1)

# График 2: Contingency Matrix - Interest × Donation (Heatmap) - отдельный файл
fig2 = plt.figure(figsize=(8, 6))
ax2 = fig2.add_subplot(111)
contingency_matrix = pd.crosstab(dialog_stats_df['max_interest_name'], dialog_stats_df['donated'])
contingency_matrix.columns = ['No Donation', 'Donated']
contingency_matrix = contingency_matrix.reindex(interest_order)
contingency_matrix_pct = contingency_matrix.div(contingency_matrix.sum(axis=1), axis=0) * 100

# Используем цветовую схему как на изображении (желтый-красный)
im = ax2.imshow(contingency_matrix_pct.values, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
ax2.set_xticks(range(len(contingency_matrix_pct.columns)))
ax2.set_yticks(range(len(contingency_matrix_pct.index)))
ax2.set_xticklabels(contingency_matrix_pct.columns, fontsize=11, fontweight='bold')
ax2.set_yticklabels(contingency_matrix_pct.index, fontsize=11, fontweight='bold')
cbar = plt.colorbar(im, ax=ax2, label='Percentage (%)', shrink=0.8)
cbar.set_label('Percentage (%)', fontsize=11, fontweight='bold')
for i in range(len(contingency_matrix_pct.index)):
    for j in range(len(contingency_matrix_pct.columns)):
        value = contingency_matrix_pct.iloc[i, j]
        # Выбираем цвет текста в зависимости от значения
        text_color = 'white' if value > 50 else 'black'
        ax2.text(j, i, f'{value:.1f}%',
                ha="center", va="center", color=text_color, fontweight='bold', fontsize=11)
ax2.set_title('Contingency Matrix: Interest × Donation', fontsize=13, fontweight='bold', pad=15)
ax2.set_xlabel('Donation Outcome', fontsize=11, fontweight='bold')
ax2.set_ylabel('Interest Level', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(str(figure("interest_donation_contingency_matrix.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 2 сохранен: interest_donation_contingency_matrix.png")
plt.close(fig2)

# График 3: Refusals × Donation (Heatmap) - отдельный файл
fig3 = plt.figure(figsize=(8, 6))
ax3 = fig3.add_subplot(111)
refusal_matrix = pd.crosstab(dialog_stats_df['has_refusal'], dialog_stats_df['donated'])
refusal_matrix.columns = ['No Donation', 'Donated']
refusal_matrix.index = ['No Refusals', 'Has Refusals']
refusal_matrix_pct = refusal_matrix.div(refusal_matrix.sum(axis=1), axis=0) * 100

# Используем цветовую схему как на изображении
im3 = ax3.imshow(refusal_matrix_pct.values, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
ax3.set_xticks(range(len(refusal_matrix_pct.columns)))
ax3.set_yticks(range(len(refusal_matrix_pct.index)))
ax3.set_xticklabels(refusal_matrix_pct.columns, fontsize=11, fontweight='bold')
ax3.set_yticklabels(refusal_matrix_pct.index, fontsize=11, fontweight='bold')
cbar3 = plt.colorbar(im3, ax=ax3, label='Percentage (%)', shrink=0.8)
cbar3.set_label('Percentage (%)', fontsize=11, fontweight='bold')
for i in range(len(refusal_matrix_pct.index)):
    for j in range(len(refusal_matrix_pct.columns)):
        value = refusal_matrix_pct.iloc[i, j]
        text_color = 'white' if value > 50 else 'black'
        ax3.text(j, i, f'{value:.1f}%',
                ha="center", va="center", color=text_color, fontweight='bold', fontsize=11)
ax3.set_title('Contingency Matrix: Refusals × Donation', fontsize=13, fontweight='bold', pad=15)
ax3.set_xlabel('Donation Outcome', fontsize=11, fontweight='bold')
ax3.set_ylabel('Refusal Status', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(str(figure("refusals_donation_contingency_matrix.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 3 сохранен: refusals_donation_contingency_matrix.png")
plt.close(fig3)

print("\n" + "="*80)
print("✅ АНАЛИЗ ЗАВЕРШЕН")
print("="*80)
print("\nСозданные файлы:")
print("   - interest_donation_by_dialog.csv")
print("   - interest_donation_summary.csv")
print("   - interest_donation_rate_by_level.png (Bar chart)")
print("   - interest_donation_contingency_matrix.png (Heatmap)")
print("   - refusals_donation_contingency_matrix.png (Heatmap)")

