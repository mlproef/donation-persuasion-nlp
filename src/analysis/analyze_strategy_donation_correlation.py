import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import FULL_INFO, STRATEGY_RESULTS, figure, result  # noqa: E402

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("АНАЛИЗ ЗАВИСИМОСТИ МЕЖДУ СТРАТЕГИЯМИ И DONATION")
print("="*80)

# Загружаем данные
print("\n1. Загружаем данные...")
strategies_df = pd.read_csv(str(STRATEGY_RESULTS))
info_df = pd.read_csv(str(FULL_INFO))

# Очищаем данные стратегий
strategies_df["strategy_ollama_single"] = strategies_df["strategy_ollama_single"].replace("", pd.NA)

print(f"   - Загружено {len(strategies_df)} строк из test_batch_results_single.csv")
print(f"   - Загружено {len(info_df)} строк из full_info.csv")

# Объединяем данные
print("\n2. Объединяем данные...")

# Берем только persuader сообщения со стратегиями
persuader_strategies = strategies_df[strategies_df['B4'] == 0].copy()
persuader_strategies = persuader_strategies[persuader_strategies['strategy_ollama_single'].notna() & 
                                            (persuader_strategies['strategy_ollama_single'].astype(str).str.strip() != '')]

# Объединяем с информацией о донатах по диалогам
dialog_donations = info_df.groupby('B2').agg({
    'B6': ['sum', 'max', 'count']
}).reset_index()
dialog_donations.columns = ['B2', 'total_donation', 'max_donation', 'n_people']
dialog_donations['donated'] = (dialog_donations['total_donation'] > 0).astype(int)

# Анализ: для каждой стратегии находим диалоги, где она использовалась, и проверяем донат
print("\n3. Анализ связи стратегия -> донат...")

strategy_donation_pairs = []

for dialog_id in persuader_strategies['B2'].unique():
    dialog_strategies = persuader_strategies[persuader_strategies['B2'] == dialog_id]
    
    # Получаем информацию о донате для этого диалога
    donation_info = dialog_donations[dialog_donations['B2'] == dialog_id]
    if len(donation_info) > 0:
        donated = donation_info.iloc[0]['donated']
        donation_amount = donation_info.iloc[0]['max_donation']
    else:
        donated = 0
        donation_amount = 0.0
    
    # Для каждой стратегии в диалоге создаем пару
    for _, row in dialog_strategies.iterrows():
        strategy_donation_pairs.append({
            'B2': dialog_id,
            'strategy': row['strategy_ollama_single'],
            'donated': donated,
            'donation_amount': donation_amount,
            'turn': row['Turn']
        })

pairs_df = pd.DataFrame(strategy_donation_pairs)
print(f"   Найдено пар стратегия->донат: {len(pairs_df)}")

if len(pairs_df) == 0:
    print("\n⚠️ Не найдено пар стратегия->донат для анализа!")
    exit(0)

# ========= 1. РАСПРЕДЕЛЕНИЕ DONATION ПО СТРАТЕГИЯМ =========
print("\n" + "="*80)
print("РАСПРЕДЕЛЕНИЕ DONATION ПО СТРАТЕГИЯМ")
print("="*80)

# Создаем contingency matrix
strategy_donation_matrix = pd.crosstab(pairs_df['strategy'], pairs_df['donated'], margins=True)
strategy_donation_matrix_pct = pd.crosstab(pairs_df['strategy'], pairs_df['donated'], normalize='index') * 100

# Переименовываем колонки для читаемости
strategy_donation_matrix.columns = ['No Donation', 'Donation', 'All']
strategy_donation_matrix_pct.columns = ['No Donation', 'Donation']

print("\nАбсолютные значения (топ-15 стратегий по частоте):")
top_strategies = pairs_df['strategy'].value_counts().head(15).index
print(strategy_donation_matrix.loc[top_strategies, ['No Donation', 'Donation']].round(0))

print("\nПроцентные значения (топ-15 стратегий):")
print(strategy_donation_matrix_pct.loc[top_strategies].round(1))

# ========= 2. СТАТИСТИКА ПО СТРАТЕГИЯМ =========
print("\n" + "="*80)
print("СТАТИСТИКА ПО СТРАТЕГИЯМ")
print("="*80)

strategy_stats = []
for strategy in pairs_df['strategy'].unique():
    strategy_data = pairs_df[pairs_df['strategy'] == strategy]
    donation_counts = strategy_data['donated'].value_counts()
    total = len(strategy_data)
    
    donated_count = donation_counts.get(1, 0)
    no_donation_count = donation_counts.get(0, 0)
    
    stats = {
        'strategy': strategy,
        'total_pairs': total,
        'no_donation_count': no_donation_count,
        'donated_count': donated_count,
        'no_donation_pct': (no_donation_count / total * 100) if total > 0 else 0,
        'donated_pct': (donated_count / total * 100) if total > 0 else 0,
        'avg_donation_amount': strategy_data[strategy_data['donated'] == 1]['donation_amount'].mean() if donated_count > 0 else 0
    }
    strategy_stats.append(stats)

strategy_stats_df = pd.DataFrame(strategy_stats).sort_values('total_pairs', ascending=False)
strategy_stats_df.to_csv(str(result("strategy_donation_stats.csv")), index=False)
print(f"\n✅ Статистика сохранена в: strategy_donation_stats.csv")

# Топ-10 стратегий с наибольшим процентом донатов
print("\nТоп-10 стратегий с наибольшим процентом донатов:")
top_donated = strategy_stats_df[strategy_stats_df['total_pairs'] >= 20].nlargest(10, 'donated_pct')
for idx, row in top_donated.iterrows():
    print(f"   {row['strategy']:50s}: {row['donated_pct']:5.1f}% донатов (n={int(row['total_pairs'])})")

# Топ-10 стратегий с наименьшим процентом донатов
print("\nТоп-10 стратегий с наименьшим процентом донатов:")
top_no_donation = strategy_stats_df[strategy_stats_df['total_pairs'] >= 20].nsmallest(10, 'donated_pct')
for idx, row in top_no_donation.iterrows():
    print(f"   {row['strategy']:50s}: {row['donated_pct']:5.1f}% донатов (n={int(row['total_pairs'])})")

# ========= 3. ВИЗУАЛИЗАЦИЯ =========
print("\n" + "="*80)
print("СОЗДАНИЕ ВИЗУАЛИЗАЦИИ")
print("="*80)

# Фильтруем стратегии с достаточным количеством примеров (>= 20)
filtered_stats = strategy_stats_df[strategy_stats_df['total_pairs'] >= 20].copy()
if len(filtered_stats) == 0:
    filtered_stats = strategy_stats_df[strategy_stats_df['total_pairs'] >= 10].copy()

# График 1: Топ-15 стратегий по проценту донатов (отдельный файл)
fig1 = plt.figure(figsize=(10, 8))
ax1 = fig1.add_subplot(111)
top_donated_plot = filtered_stats.nlargest(15, 'donated_pct')
bars1 = ax1.barh(range(len(top_donated_plot)), top_donated_plot['donated_pct'].values, 
                 color='#2ca02c', alpha=0.7)  # Зеленый для донатов
ax1.set_yticks(range(len(top_donated_plot)))
ax1.set_yticklabels([s[:40] for s in top_donated_plot['strategy']], fontsize=10)
ax1.set_xlabel('Donation Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Top-15 Strategies Leading to Donation', fontsize=14, fontweight='bold', pad=20)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)
for i, (idx, row) in enumerate(top_donated_plot.iterrows()):
    ax1.text(row['donated_pct'], i, f" {row['donated_pct']:.1f}% (n={int(row['total_pairs'])})", 
             va='center', fontsize=9)
plt.tight_layout()
plt.savefig(str(figure("strategies_leading_to_donation.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 1 сохранен: strategies_leading_to_donation.png")
plt.close(fig1)

# График 2: Топ-15 стратегий по проценту отсутствия донатов (отдельный файл)
fig2 = plt.figure(figsize=(10, 8))
ax2 = fig2.add_subplot(111)
top_no_donation_plot = filtered_stats.nlargest(15, 'no_donation_pct')
bars2 = ax2.barh(range(len(top_no_donation_plot)), top_no_donation_plot['no_donation_pct'].values, 
                 color='#d62728', alpha=0.7)  # Красный для отсутствия донатов
ax2.set_yticks(range(len(top_no_donation_plot)))
ax2.set_yticklabels([s[:40] for s in top_no_donation_plot['strategy']], fontsize=10)
ax2.set_xlabel('No Donation Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Top-15 Strategies Leading to No Donation', fontsize=14, fontweight='bold', pad=20)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)
for i, (idx, row) in enumerate(top_no_donation_plot.iterrows()):
    ax2.text(row['no_donation_pct'], i, f" {row['no_donation_pct']:.1f}% (n={int(row['total_pairs'])})", 
             va='center', fontsize=9)
plt.tight_layout()
plt.savefig(str(figure("strategies_leading_to_no_donation.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 2 сохранен: strategies_leading_to_no_donation.png")
plt.close(fig2)

# График 3: Heatmap - Стратегии × Donation (топ-20 стратегий) (отдельный файл)
fig3 = plt.figure(figsize=(10, 10))
ax3 = fig3.add_subplot(111)
top_20_strategies = pairs_df['strategy'].value_counts().head(20).index
heatmap_data = strategy_donation_matrix_pct.loc[top_20_strategies, ['No Donation', 'Donation']]

# Используем цветовую схему YlOrRd
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
        count = strategy_donation_matrix.loc[heatmap_data.index[i], heatmap_data.columns[j]]
        ax3.text(j, i, f'{value:.1f}%\n(n={int(count)})',
                ha="center", va="center", color=text_color, fontweight='bold', fontsize=8)

ax3.set_title('Strategy × Donation Correlation Matrix (Top-20 Strategies)', fontsize=14, fontweight='bold', pad=20)
ax3.set_xlabel('Donation Outcome', fontsize=12, fontweight='bold')
ax3.set_ylabel('Strategy', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(str(figure("strategy_donation_heatmap.png")), dpi=300, bbox_inches='tight')
print(f"✅ График 3 сохранен: strategy_donation_heatmap.png")
plt.close(fig3)

# ========= 4. ДЕТАЛЬНАЯ СТАТИСТИКА =========
print("\n" + "="*80)
print("ДЕТАЛЬНАЯ СТАТИСТИКА")
print("="*80)

print(f"\nВсего пар стратегия->донат: {len(pairs_df)}")
print(f"Уникальных стратегий: {pairs_df['strategy'].nunique()}")
print(f"\nРаспределение донатов:")
donation_dist = pairs_df['donated'].value_counts()
for donated, count in donation_dist.items():
    label = "Donation" if donated == 1 else "No Donation"
    print(f"   {label}: {count} ({count/len(pairs_df)*100:.1f}%)")

# Сохраняем все пары для детального анализа
pairs_df.to_csv(str(result("strategy_donation_pairs.csv")), index=False)
print(f"\n✅ Все пары сохранены в: strategy_donation_pairs.csv")

# ========= 5. СТАТИСТИКА ДЛЯ КАЖДОГО ГРАФИКА =========
print("\n" + "="*80)
print("СТАТИСТИКА ДЛЯ КАЖДОГО ГРАФИКА")
print("="*80)

# Статистика для графика 1: Strategies Leading to Donation
print("\n" + "-"*80)
print("ГРАФИК 1: Top-15 Strategies Leading to Donation")
print("-"*80)
top_donated_stats = filtered_stats.nlargest(15, 'donated_pct')
print(f"\nВсего стратегий в графике: {len(top_donated_stats)}")
print(f"Общее количество пар: {int(top_donated_stats['total_pairs'].sum())}")
print(f"\nДетальная статистика:")
for idx, row in top_donated_stats.iterrows():
    print(f"\n{row['strategy']}:")
    print(f"   - Donation: {row['donated_pct']:.1f}% ({int(row['donated_count'])} из {int(row['total_pairs'])})")
    print(f"   - No Donation: {row['no_donation_pct']:.1f}% ({int(row['no_donation_count'])})")
    print(f"   - Всего пар: {int(row['total_pairs'])}")
    if row['donated_count'] > 0:
        print(f"   - Средняя сумма доната: ${row['avg_donation_amount']:.2f}")

# Статистика для графика 2: Strategies Leading to No Donation
print("\n" + "-"*80)
print("ГРАФИК 2: Top-15 Strategies Leading to No Donation")
print("-"*80)
top_no_donation_stats = filtered_stats.nlargest(15, 'no_donation_pct')
print(f"\nВсего стратегий в графике: {len(top_no_donation_stats)}")
print(f"Общее количество пар: {int(top_no_donation_stats['total_pairs'].sum())}")
print(f"\nДетальная статистика:")
for idx, row in top_no_donation_stats.iterrows():
    print(f"\n{row['strategy']}:")
    print(f"   - No Donation: {row['no_donation_pct']:.1f}% ({int(row['no_donation_count'])} из {int(row['total_pairs'])})")
    print(f"   - Donation: {row['donated_pct']:.1f}% ({int(row['donated_count'])})")
    print(f"   - Всего пар: {int(row['total_pairs'])}")

# Статистика для графика 3: Strategy × Donation Heatmap
print("\n" + "-"*80)
print("ГРАФИК 3: Strategy × Donation Correlation Matrix (Top-20 Strategies)")
print("-"*80)
top_20_strategies_heatmap = pairs_df['strategy'].value_counts().head(20).index
heatmap_stats_df = strategy_donation_matrix_pct.loc[top_20_strategies_heatmap, ['No Donation', 'Donation']]
heatmap_counts_df = strategy_donation_matrix.loc[top_20_strategies_heatmap, ['No Donation', 'Donation']]

print(f"\nВсего стратегий в heatmap: {len(heatmap_stats_df)}")
print(f"Общее количество пар: {int(heatmap_counts_df.sum(axis=1).sum())}")
print(f"\nДетальная статистика по каждой стратегии:")
for strategy in heatmap_stats_df.index:
    print(f"\n{strategy}:")
    for outcome in ['No Donation', 'Donation']:
        pct = heatmap_stats_df.loc[strategy, outcome]
        count = int(heatmap_counts_df.loc[strategy, outcome])
        total = int(heatmap_counts_df.loc[strategy].sum())
        print(f"   - {outcome}: {pct:.1f}% ({count} из {total})")

print("\n" + "="*80)
print("✅ АНАЛИЗ ЗАВЕРШЕН")
print("="*80)
print("\nСозданные файлы:")
print("   - strategy_donation_stats.csv")
print("   - strategy_donation_pairs.csv")
print("   - strategies_leading_to_donation.png (Bar chart)")
print("   - strategies_leading_to_no_donation.png (Bar chart)")
print("   - strategy_donation_heatmap.png (Heatmap)")

