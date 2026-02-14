import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("АНАЛИЗ ЗАВИСИМОСТИ МЕЖДУ СТРАТЕГИЯМИ И СЕНТИМЕНТАМИ")
print("="*80)

# Загружаем данные
print("\n1. Загружаем данные...")
strategies_df = pd.read_csv("test_batch_results_single.csv")
sentiment_df = pd.read_csv("test_batch_sentiment_results.csv")

# Очищаем данные
strategies_df["strategy_ollama_single"] = strategies_df["strategy_ollama_single"].replace("", pd.NA)
sentiment_df["sentiment_ollama_v2"] = sentiment_df["sentiment_ollama_v2"].replace("", pd.NA).replace("nan", pd.NA).replace("None", pd.NA)

print(f"   - Загружено {len(strategies_df)} строк из test_batch_results_single.csv")
print(f"   - Загружено {len(sentiment_df)} строк из test_batch_sentiment_results.csv")

# Объединяем данные
print("\n2. Объединяем данные...")
merged_df = strategies_df.merge(
    sentiment_df[['B2', 'Turn', 'B4', 'sentiment_ollama_v2']],
    on=['B2', 'Turn', 'B4'],
    how='left',
    suffixes=('', '_sentiment')
)

# Анализ: для каждой стратегии persuader находим следующий сентимент target
print("\n3. Анализ связи стратегия -> следующий сентимент...")

strategy_sentiment_pairs = []

for dialog_id in merged_df['B2'].unique():
    dialog_data = merged_df[merged_df['B2'] == dialog_id].sort_values('Turn').reset_index(drop=True)
    
    for idx in range(len(dialog_data) - 1):
        current_row = dialog_data.iloc[idx]
        next_row = dialog_data.iloc[idx + 1]
        
        # Если текущее сообщение - persuader со стратегией, а следующее - target с сентиментом
        if (current_row['B4'] == 0 and 
            pd.notna(current_row['strategy_ollama_single']) and 
            str(current_row['strategy_ollama_single']).strip() != '' and
            next_row['B4'] == 1 and
            pd.notna(next_row['sentiment_ollama_v2']) and
            str(next_row['sentiment_ollama_v2']).strip() != ''):
            
            strategy_sentiment_pairs.append({
                'B2': dialog_id,
                'strategy': current_row['strategy_ollama_single'],
                'sentiment': next_row['sentiment_ollama_v2'],
                'strategy_turn': current_row['Turn'],
                'sentiment_turn': next_row['Turn']
            })

pairs_df = pd.DataFrame(strategy_sentiment_pairs)
print(f"   Найдено пар стратегия->сентимент: {len(pairs_df)}")

if len(pairs_df) == 0:
    print("\n⚠️ Не найдено пар стратегия->сентимент для анализа!")
    exit(0)

# ========= 1. РАСПРЕДЕЛЕНИЕ СЕНТИМЕНТОВ ПО СТРАТЕГИЯМ =========
print("\n" + "="*80)
print("РАСПРЕДЕЛЕНИЕ СЕНТИМЕНТОВ ПО СТРАТЕГИЯМ")
print("="*80)

# Создаем contingency matrix
strategy_sentiment_matrix = pd.crosstab(pairs_df['strategy'], pairs_df['sentiment'], margins=True)
strategy_sentiment_matrix_pct = pd.crosstab(pairs_df['strategy'], pairs_df['sentiment'], normalize='index') * 100

print("\nАбсолютные значения (топ-15 стратегий по частоте):")
top_strategies = pairs_df['strategy'].value_counts().head(15).index
print(strategy_sentiment_matrix.loc[top_strategies].round(0))

print("\nПроцентные значения (топ-15 стратегий):")
print(strategy_sentiment_matrix_pct.loc[top_strategies].round(1))

# ========= 2. СТАТИСТИКА ПО СТРАТЕГИЯМ =========
print("\n" + "="*80)
print("СТАТИСТИКА ПО СТРАТЕГИЯМ")
print("="*80)

strategy_stats = []
for strategy in pairs_df['strategy'].unique():
    strategy_data = pairs_df[pairs_df['strategy'] == strategy]
    sentiment_counts = strategy_data['sentiment'].value_counts()
    total = len(strategy_data)
    
    stats = {
        'strategy': strategy,
        'total_pairs': total,
        'negative_count': sentiment_counts.get('negative', 0),
        'neutral_count': sentiment_counts.get('neutral', 0),
        'positive_count': sentiment_counts.get('positive', 0),
        'negative_pct': (sentiment_counts.get('negative', 0) / total * 100) if total > 0 else 0,
        'neutral_pct': (sentiment_counts.get('neutral', 0) / total * 100) if total > 0 else 0,
        'positive_pct': (sentiment_counts.get('positive', 0) / total * 100) if total > 0 else 0,
    }
    strategy_stats.append(stats)

strategy_stats_df = pd.DataFrame(strategy_stats).sort_values('total_pairs', ascending=False)
strategy_stats_df.to_csv('strategy_sentiment_stats.csv', index=False)
print(f"\n✅ Статистика сохранена в: strategy_sentiment_stats.csv")

# Топ-10 стратегий с наибольшим процентом негативных сентиментов
print("\nТоп-10 стратегий с наибольшим процентом негативных сентиментов:")
top_negative = strategy_stats_df[strategy_stats_df['total_pairs'] >= 10].nlargest(10, 'negative_pct')
for idx, row in top_negative.iterrows():
    print(f"   {row['strategy']:50s}: {row['negative_pct']:5.1f}% негативных (n={int(row['total_pairs'])})")

# Топ-10 стратегий с наибольшим процентом позитивных сентиментов
print("\nТоп-10 стратегий с наибольшим процентом позитивных сентиментов:")
top_positive = strategy_stats_df[strategy_stats_df['total_pairs'] >= 10].nlargest(10, 'positive_pct')
for idx, row in top_positive.iterrows():
    print(f"   {row['strategy']:50s}: {row['positive_pct']:5.1f}% позитивных (n={int(row['total_pairs'])})")

# ========= 3. ВИЗУАЛИЗАЦИЯ =========
print("\n" + "="*80)
print("СОЗДАНИЕ ВИЗУАЛИЗАЦИИ")
print("="*80)

# Фильтруем стратегии с достаточным количеством примеров (>= 20)
filtered_stats = strategy_stats_df[strategy_stats_df['total_pairs'] >= 20].copy()
if len(filtered_stats) == 0:
    filtered_stats = strategy_stats_df[strategy_stats_df['total_pairs'] >= 10].copy()

# График 1: Топ-15 стратегий по проценту негативных сентиментов (отдельный файл)
fig1 = plt.figure(figsize=(10, 8))
ax1 = fig1.add_subplot(111)
top_negative_plot = filtered_stats.nlargest(15, 'negative_pct')
bars1 = ax1.barh(range(len(top_negative_plot)), top_negative_plot['negative_pct'].values, color='#d62728', alpha=0.7)
ax1.set_yticks(range(len(top_negative_plot)))
ax1.set_yticklabels([s[:40] for s in top_negative_plot['strategy']], fontsize=10)
ax1.set_xlabel('Negative Sentiment Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Top-15 Strategies Leading to Negative Sentiment', fontsize=14, fontweight='bold', pad=20)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)
for i, (idx, row) in enumerate(top_negative_plot.iterrows()):
    ax1.text(row['negative_pct'], i, f" {row['negative_pct']:.1f}% (n={int(row['total_pairs'])})", 
             va='center', fontsize=9)
plt.tight_layout()
plt.savefig("strategies_leading_to_negative_sentiment.png", dpi=300, bbox_inches='tight')
print(f"✅ График 1 сохранен: strategies_leading_to_negative_sentiment.png")
plt.close(fig1)

# График 2: Топ-15 стратегий по проценту позитивных сентиментов (отдельный файл)
fig2 = plt.figure(figsize=(10, 8))
ax2 = fig2.add_subplot(111)
top_positive_plot = filtered_stats.nlargest(15, 'positive_pct')
bars2 = ax2.barh(range(len(top_positive_plot)), top_positive_plot['positive_pct'].values, color='#2ca02c', alpha=0.7)
ax2.set_yticks(range(len(top_positive_plot)))
ax2.set_yticklabels([s[:40] for s in top_positive_plot['strategy']], fontsize=10)
ax2.set_xlabel('Positive Sentiment Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Top-15 Strategies Leading to Positive Sentiment', fontsize=14, fontweight='bold', pad=20)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)
for i, (idx, row) in enumerate(top_positive_plot.iterrows()):
    ax2.text(row['positive_pct'], i, f" {row['positive_pct']:.1f}% (n={int(row['total_pairs'])})", 
             va='center', fontsize=9)
plt.tight_layout()
plt.savefig("strategies_leading_to_positive_sentiment.png", dpi=300, bbox_inches='tight')
print(f"✅ График 2 сохранен: strategies_leading_to_positive_sentiment.png")
plt.close(fig2)

# График 3: Heatmap - Стратегии × Сентименты (топ-20 стратегий) (отдельный файл)
fig3 = plt.figure(figsize=(12, 10))
ax3 = fig3.add_subplot(111)
top_20_strategies = pairs_df['strategy'].value_counts().head(20).index
heatmap_data = strategy_sentiment_matrix_pct.loc[top_20_strategies, ['negative', 'neutral', 'positive']]

im = ax3.imshow(heatmap_data.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
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
        count = strategy_sentiment_matrix.loc[heatmap_data.index[i], heatmap_data.columns[j]]
        ax3.text(j, i, f'{value:.1f}%\n(n={int(count)})',
                ha="center", va="center", color=text_color, fontweight='bold', fontsize=8)

ax3.set_title('Strategy × Sentiment Correlation Matrix (Top-20 Strategies)', fontsize=14, fontweight='bold', pad=20)
ax3.set_xlabel('Sentiment', fontsize=12, fontweight='bold')
ax3.set_ylabel('Strategy', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig("strategy_sentiment_heatmap.png", dpi=300, bbox_inches='tight')
print(f"✅ График 3 сохранен: strategy_sentiment_heatmap.png")
plt.close(fig3)

# ========= 4. ДЕТАЛЬНАЯ СТАТИСТИКА =========
print("\n" + "="*80)
print("ДЕТАЛЬНАЯ СТАТИСТИКА")
print("="*80)

print(f"\nВсего пар стратегия->сентимент: {len(pairs_df)}")
print(f"Уникальных стратегий: {pairs_df['strategy'].nunique()}")
print(f"\nРаспределение сентиментов:")
sentiment_dist = pairs_df['sentiment'].value_counts()
for sentiment, count in sentiment_dist.items():
    print(f"   {sentiment}: {count} ({count/len(pairs_df)*100:.1f}%)")

# Сохраняем все пары для детального анализа
pairs_df.to_csv('strategy_sentiment_pairs.csv', index=False)
print(f"\n✅ Все пары сохранены в: strategy_sentiment_pairs.csv")

print("\n" + "="*80)
print("✅ АНАЛИЗ ЗАВЕРШЕН")
print("="*80)
print("\nСозданные файлы:")
print("   - strategy_sentiment_stats.csv")
print("   - strategy_sentiment_pairs.csv")
print("   - strategies_leading_to_negative_sentiment.png (Bar chart)")
print("   - strategies_leading_to_positive_sentiment.png (Bar chart)")
print("   - strategy_sentiment_heatmap.png (Heatmap)")


