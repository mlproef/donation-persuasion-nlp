import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import INTEREST_RESULTS, STRATEGY_RESULTS, figure, result  # noqa: E402

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("АНАЛИЗ ЗАВИСИМОСТИ МЕЖДУ СТРАТЕГИЯМИ И ИНТЕРЕСОМ (INTEREST)")
print("="*80)

# Загружаем данные
print("\n1. Загружаем данные...")
strategies_df = pd.read_csv(str(STRATEGY_RESULTS))
interest_df = pd.read_csv(str(INTEREST_RESULTS))

# Очищаем данные
strategies_df["strategy_ollama_single"] = strategies_df["strategy_ollama_single"].replace("", pd.NA)
interest_df["interest_ollama_v2"] = interest_df["interest_ollama_v2"].replace("", pd.NA).replace("nan", pd.NA).replace("None", pd.NA)

print(f"   - Загружено {len(strategies_df)} строк из test_batch_results_single.csv")
print(f"   - Загружено {len(interest_df)} строк из test_batch_interest_results.csv")

# Объединяем данные
print("\n2. Объединяем данные...")
merged_df = strategies_df.merge(
    interest_df[['B2', 'Turn', 'B4', 'interest_ollama_v2']],
    on=['B2', 'Turn', 'B4'],
    how='left',
    suffixes=('', '_interest')
)

# Анализ: для каждой стратегии persuader находим следующий interest target
print("\n3. Анализ связи стратегия -> следующий interest...")

strategy_interest_pairs = []

for dialog_id in merged_df['B2'].unique():
    dialog_data = merged_df[merged_df['B2'] == dialog_id].sort_values('Turn').reset_index(drop=True)
    
    for idx in range(len(dialog_data) - 1):
        current_row = dialog_data.iloc[idx]
        next_row = dialog_data.iloc[idx + 1]
        
        # Если текущее сообщение - persuader со стратегией, а следующее - target с interest
        if (current_row['B4'] == 0 and 
            pd.notna(current_row['strategy_ollama_single']) and 
            str(current_row['strategy_ollama_single']).strip() != '' and
            next_row['B4'] == 1 and
            pd.notna(next_row['interest_ollama_v2']) and
            str(next_row['interest_ollama_v2']).strip() != ''):
            
            strategy_interest_pairs.append({
                'B2': dialog_id,
                'strategy': current_row['strategy_ollama_single'],
                'interest': next_row['interest_ollama_v2'],
                'strategy_turn': current_row['Turn'],
                'interest_turn': next_row['Turn']
            })

pairs_df = pd.DataFrame(strategy_interest_pairs)
print(f"   Найдено пар стратегия->interest: {len(pairs_df)}")

if len(pairs_df) == 0:
    print("\n⚠️ Не найдено пар стратегия->interest для анализа!")
    exit(0)

# ========= 1. РАСПРЕДЕЛЕНИЕ INTEREST ПО СТРАТЕГИЯМ =========
print("\n" + "="*80)
print("РАСПРЕДЕЛЕНИЕ INTEREST ПО СТРАТЕГИЯМ")
print("="*80)

# Создаем contingency matrix
strategy_interest_matrix = pd.crosstab(pairs_df['strategy'], pairs_df['interest'], margins=True)
strategy_interest_matrix_pct = pd.crosstab(pairs_df['strategy'], pairs_df['interest'], normalize='index') * 100

print("\nАбсолютные значения (топ-15 стратегий по частоте):")
top_strategies = pairs_df['strategy'].value_counts().head(15).index
print(strategy_interest_matrix.loc[top_strategies].round(0))

print("\nПроцентные значения (топ-15 стратегий):")
print(strategy_interest_matrix_pct.loc[top_strategies].round(1))

# ========= 2. СТАТИСТИКА ПО СТРАТЕГИЯМ =========
print("\n" + "="*80)
print("СТАТИСТИКА ПО СТРАТЕГИЯМ")
print("="*80)

strategy_stats = []
for strategy in pairs_df['strategy'].unique():
    strategy_data = pairs_df[pairs_df['strategy'] == strategy]
    interest_counts = strategy_data['interest'].value_counts()
    total = len(strategy_data)
    
    stats = {
        'strategy': strategy,
        'total_pairs': total,
        'not_interested_count': interest_counts.get('Not Interested', 0),
        'neutral_count': interest_counts.get('Neutral', 0),
        'interested_count': interest_counts.get('Interested', 0),
        'not_interested_pct': (interest_counts.get('Not Interested', 0) / total * 100) if total > 0 else 0,
        'neutral_pct': (interest_counts.get('Neutral', 0) / total * 100) if total > 0 else 0,
        'interested_pct': (interest_counts.get('Interested', 0) / total * 100) if total > 0 else 0,
    }
    strategy_stats.append(stats)

strategy_stats_df = pd.DataFrame(strategy_stats).sort_values('total_pairs', ascending=False)
strategy_stats_df.to_csv(str(result("strategy_interest_stats.csv")), index=False)
print(f"\n✅ Статистика сохранена в: strategy_interest_stats.csv")

# Топ-10 стратегий с наибольшим процентом "Not Interested"
print("\nТоп-10 стратегий с наибольшим процентом 'Not Interested':")
top_not_interested = strategy_stats_df[strategy_stats_df['total_pairs'] >= 10].nlargest(10, 'not_interested_pct')
for idx, row in top_not_interested.iterrows():
    print(f"   {row['strategy']:50s}: {row['not_interested_pct']:5.1f}% Not Interested (n={int(row['total_pairs'])})")

# Топ-10 стратегий с наибольшим процентом "Interested"
print("\nТоп-10 стратегий с наибольшим процентом 'Interested':")
top_interested = strategy_stats_df[strategy_stats_df['total_pairs'] >= 10].nlargest(10, 'interested_pct')
for idx, row in top_interested.iterrows():
    print(f"   {row['strategy']:50s}: {row['interested_pct']:5.1f}% Interested (n={int(row['total_pairs'])})")

# ========= 3. ВИЗУАЛИЗАЦИЯ =========
print("\n" + "="*80)
print("СОЗДАНИЕ ВИЗУАЛИЗАЦИИ")
print("="*80)

# Фильтруем стратегии с достаточным количеством примеров (>= 20)
filtered_stats = strategy_stats_df[strategy_stats_df['total_pairs'] >= 20].copy()
if len(filtered_stats) == 0:
    filtered_stats = strategy_stats_df[strategy_stats_df['total_pairs'] >= 10].copy()

# График 1: Топ-15 стратегий по проценту "Not Interested" (отдельный файл)
fig1 = plt.figure(figsize=(10, 8))
ax1 = fig1.add_subplot(111)
top_not_interested_plot = filtered_stats.nlargest(15, 'not_interested_pct')
bars1 = ax1.barh(range(len(top_not_interested_plot)), top_not_interested_plot['not_interested_pct'].values, 
                 color='#d62728', alpha=0.7)  # Красный для Not Interested
ax1.set_yticks(range(len(top_not_interested_plot)))
ax1.set_yticklabels([s[:40] for s in top_not_interested_plot['strategy']], fontsize=10)
ax1.set_xlabel('Not Interested Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Top-15 Strategies Leading to Not Interested', fontsize=14, fontweight='bold', pad=20)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)
for i, (idx, row) in enumerate(top_not_interested_plot.iterrows()):
    ax1.text(row['not_interested_pct'], i, f" {row['not_interested_pct']:.1f}% (n={int(row['total_pairs'])})", 
             va='center', fontsize=9)
plt.tight_layout()
plt.savefig(str(figure("strategies_leading_to_not_interested.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 1 сохранен: strategies_leading_to_not_interested.png")
plt.close(fig1)

# График 2: Топ-15 стратегий по проценту "Interested" (отдельный файл)
fig2 = plt.figure(figsize=(10, 8))
ax2 = fig2.add_subplot(111)
top_interested_plot = filtered_stats.nlargest(15, 'interested_pct')
bars2 = ax2.barh(range(len(top_interested_plot)), top_interested_plot['interested_pct'].values, 
                 color='#2ca02c', alpha=0.7)  # Зеленый для Interested
ax2.set_yticks(range(len(top_interested_plot)))
ax2.set_yticklabels([s[:40] for s in top_interested_plot['strategy']], fontsize=10)
ax2.set_xlabel('Interested Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Top-15 Strategies Leading to Interested', fontsize=14, fontweight='bold', pad=20)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)
for i, (idx, row) in enumerate(top_interested_plot.iterrows()):
    ax2.text(row['interested_pct'], i, f" {row['interested_pct']:.1f}% (n={int(row['total_pairs'])})", 
             va='center', fontsize=9)
plt.tight_layout()
plt.savefig(str(figure("strategies_leading_to_interested.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 2 сохранен: strategies_leading_to_interested.png")
plt.close(fig2)

# График 3: Heatmap - Стратегии × Interest (топ-20 стратегий) (отдельный файл)
fig3 = plt.figure(figsize=(12, 10))
ax3 = fig3.add_subplot(111)
top_20_strategies = pairs_df['strategy'].value_counts().head(20).index
heatmap_data = strategy_interest_matrix_pct.loc[top_20_strategies, ['Not Interested', 'Neutral', 'Interested']]

# Используем цветовую схему YlOrRd как в других heatmap'ах
im = ax3.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
ax3.set_xticks(range(len(heatmap_data.columns)))
ax3.set_yticks(range(len(heatmap_data.index)))
ax3.set_xticklabels(heatmap_data.columns, fontsize=11, fontweight='bold')
ax3.set_yticklabels([s[:35] for s in heatmap_data.index], fontsize=9)
cbar = plt.colorbar(im, ax=ax3, label='Percentage (%)', shrink=0.8)
cbar.set_label('Percentage (%)', fontsize=12, fontweight='bold')

for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        value = heatmap_data.iloc[i, j]
        text_color = 'white' if value > 50 else 'black'
        count = strategy_interest_matrix.loc[heatmap_data.index[i], heatmap_data.columns[j]]
        ax3.text(j, i, f'{value:.1f}%\n(n={int(count)})',
                ha="center", va="center", color=text_color, fontweight='bold', fontsize=8)

ax3.set_title('Strategy × Interest Correlation Matrix (Top-20 Strategies)', fontsize=14, fontweight='bold', pad=20)
ax3.set_xlabel('Interest Level', fontsize=12, fontweight='bold')
ax3.set_ylabel('Strategy', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(str(figure("strategy_interest_heatmap.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 3 сохранен: strategy_interest_heatmap.png")
plt.close(fig3)

# ========= 4. ДЕТАЛЬНАЯ СТАТИСТИКА =========
print("\n" + "="*80)
print("ДЕТАЛЬНАЯ СТАТИСТИКА")
print("="*80)

print(f"\nВсего пар стратегия->interest: {len(pairs_df)}")
print(f"Уникальных стратегий: {pairs_df['strategy'].nunique()}")
print(f"\nРаспределение interest:")
interest_dist = pairs_df['interest'].value_counts()
for interest, count in interest_dist.items():
    print(f"   {interest}: {count} ({count/len(pairs_df)*100:.1f}%)")

# Сохраняем все пары для детального анализа
pairs_df.to_csv(str(result("strategy_interest_pairs.csv")), index=False)
print(f"\n✅ Все пары сохранены в: strategy_interest_pairs.csv")

# ========= 5. СТАТИСТИКА ДЛЯ КАЖДОГО ГРАФИКА =========
print("\n" + "="*80)
print("СТАТИСТИКА ДЛЯ КАЖДОГО ГРАФИКА")
print("="*80)

# Статистика для графика 1: Strategies Leading to Not Interested
print("\n" + "-"*80)
print("ГРАФИК 1: Top-15 Strategies Leading to Not Interested")
print("-"*80)
top_not_interested_stats = filtered_stats.nlargest(15, 'not_interested_pct')
print(f"\nВсего стратегий в графике: {len(top_not_interested_stats)}")
print(f"Общее количество пар: {int(top_not_interested_stats['total_pairs'].sum())}")
print(f"\nДетальная статистика:")
for idx, row in top_not_interested_stats.iterrows():
    print(f"\n{row['strategy']}:")
    print(f"   - Not Interested: {row['not_interested_pct']:.1f}% ({int(row['not_interested_count'])} из {int(row['total_pairs'])})")
    print(f"   - Neutral: {row['neutral_pct']:.1f}% ({int(row['neutral_count'])})")
    print(f"   - Interested: {row['interested_pct']:.1f}% ({int(row['interested_count'])})")
    print(f"   - Всего пар: {int(row['total_pairs'])}")

# Статистика для графика 2: Strategies Leading to Interested
print("\n" + "-"*80)
print("ГРАФИК 2: Top-15 Strategies Leading to Interested")
print("-"*80)
top_interested_stats = filtered_stats.nlargest(15, 'interested_pct')
print(f"\nВсего стратегий в графике: {len(top_interested_stats)}")
print(f"Общее количество пар: {int(top_interested_stats['total_pairs'].sum())}")
print(f"\nДетальная статистика:")
for idx, row in top_interested_stats.iterrows():
    print(f"\n{row['strategy']}:")
    print(f"   - Interested: {row['interested_pct']:.1f}% ({int(row['interested_count'])} из {int(row['total_pairs'])})")
    print(f"   - Neutral: {row['neutral_pct']:.1f}% ({int(row['neutral_count'])})")
    print(f"   - Not Interested: {row['not_interested_pct']:.1f}% ({int(row['not_interested_count'])})")
    print(f"   - Всего пар: {int(row['total_pairs'])}")

# Статистика для графика 3: Strategy × Interest Heatmap
print("\n" + "-"*80)
print("ГРАФИК 3: Strategy × Interest Correlation Matrix (Top-20 Strategies)")
print("-"*80)
top_20_strategies_heatmap = pairs_df['strategy'].value_counts().head(20).index
heatmap_stats_df = strategy_interest_matrix_pct.loc[top_20_strategies_heatmap, ['Not Interested', 'Neutral', 'Interested']]
heatmap_counts_df = strategy_interest_matrix.loc[top_20_strategies_heatmap, ['Not Interested', 'Neutral', 'Interested']]

print(f"\nВсего стратегий в heatmap: {len(heatmap_stats_df)}")
print(f"Общее количество пар: {int(heatmap_counts_df.sum(axis=1).sum())}")
print(f"\nДетальная статистика по каждой стратегии:")
for strategy in heatmap_stats_df.index:
    print(f"\n{strategy}:")
    for interest in ['Not Interested', 'Neutral', 'Interested']:
        pct = heatmap_stats_df.loc[strategy, interest]
        count = int(heatmap_counts_df.loc[strategy, interest])
        total = int(heatmap_counts_df.loc[strategy].sum())
        print(f"   - {interest}: {pct:.1f}% ({count} из {total})")

print("\n" + "="*80)
print("✅ АНАЛИЗ ЗАВЕРШЕН")
print("="*80)
print("\nСозданные файлы:")
print("   - strategy_interest_stats.csv")
print("   - strategy_interest_pairs.csv")
print("   - strategies_leading_to_not_interested.png (Bar chart)")
print("   - strategies_leading_to_interested.png (Bar chart)")
print("   - strategy_interest_heatmap.png (Heatmap)")

