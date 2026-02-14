import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("JOINT ANALYSIS: SELECTED PERSUASION STRATEGIES")
print("="*80)

# Выбранные стратегии для анализа
SELECTED_STRATEGIES = [
    'Fear Appeal',
    'Guilt Induction',
    'Reciprocity',
    'Commitment and Consistency'
]

# Загружаем данные
print("\n1. Загружаем данные...")
strategies_df = pd.read_csv("test_batch_results_single.csv")
sentiment_df = pd.read_csv("test_batch_sentiment_results.csv")
interest_df = pd.read_csv("test_batch_interest_results.csv")
info_df = pd.read_csv("full_info.csv")

# Очищаем данные
strategies_df["strategy_ollama_single"] = strategies_df["strategy_ollama_single"].replace("", pd.NA)
sentiment_df["sentiment_ollama_v2"] = sentiment_df["sentiment_ollama_v2"].replace("", pd.NA).replace("nan", pd.NA).replace("None", pd.NA)
interest_df["interest_ollama_v2"] = interest_df["interest_ollama_v2"].replace("", pd.NA).replace("nan", pd.NA).replace("None", pd.NA)

print(f"   - Загружено {len(strategies_df)} строк из test_batch_results_single.csv")
print(f"   - Загружено {len(sentiment_df)} строк из test_batch_sentiment_results.csv")
print(f"   - Загружено {len(interest_df)} строк из test_batch_interest_results.csv")
print(f"   - Загружено {len(info_df)} строк из full_info.csv")

# Объединяем данные
print("\n2. Объединяем данные...")

# Объединяем стратегии с sentiment
merged_df = strategies_df.merge(
    sentiment_df[['B2', 'Turn', 'B4', 'sentiment_ollama_v2']],
    on=['B2', 'Turn', 'B4'],
    how='left',
    suffixes=('', '_sentiment')
)

# Объединяем с interest
merged_df = merged_df.merge(
    interest_df[['B2', 'Turn', 'B4', 'interest_ollama_v2']],
    on=['B2', 'Turn', 'B4'],
    how='left',
    suffixes=('', '_interest')
)

# Объединяем с donation info
dialog_donations = info_df.groupby('B2').agg({
    'B6': ['sum', 'max']
}).reset_index()
dialog_donations.columns = ['B2', 'total_donation', 'max_donation']
dialog_donations['donated'] = (dialog_donations['total_donation'] > 0).astype(int)

merged_df = merged_df.merge(
    dialog_donations[['B2', 'donated', 'max_donation']],
    on='B2',
    how='left'
)

# Фильтруем только persuader сообщения с выбранными стратегиями
persuader_strategies = merged_df[
    (merged_df['B4'] == 0) & 
    (merged_df['strategy_ollama_single'].isin(SELECTED_STRATEGIES)) &
    (merged_df['strategy_ollama_single'].notna())
].copy()

print(f"   Найдено сообщений с выбранными стратегиями: {len(persuader_strategies)}")

# ========= 3. АНАЛИЗ: СТРАТЕГИЯ -> SENTIMENT =========
print("\n3. Анализ: Стратегия -> Sentiment...")

strategy_sentiment_pairs = []
for dialog_id in persuader_strategies['B2'].unique():
    dialog_data = merged_df[merged_df['B2'] == dialog_id].sort_values('Turn').reset_index(drop=True)
    
    for idx in range(len(dialog_data) - 1):
        current_row = dialog_data.iloc[idx]
        next_row = dialog_data.iloc[idx + 1]
        
        if (current_row['B4'] == 0 and 
            pd.notna(current_row['strategy_ollama_single']) and
            current_row['strategy_ollama_single'] in SELECTED_STRATEGIES and
            next_row['B4'] == 1 and
            pd.notna(next_row['sentiment_ollama_v2']) and
            str(next_row['sentiment_ollama_v2']).strip() != ''):
            
            strategy_sentiment_pairs.append({
                'strategy': current_row['strategy_ollama_single'],
                'sentiment': next_row['sentiment_ollama_v2']
            })

sentiment_pairs_df = pd.DataFrame(strategy_sentiment_pairs)

# ========= 4. АНАЛИЗ: СТРАТЕГИЯ -> INTEREST =========
print("4. Анализ: Стратегия -> Interest...")

strategy_interest_pairs = []
for dialog_id in persuader_strategies['B2'].unique():
    dialog_data = merged_df[merged_df['B2'] == dialog_id].sort_values('Turn').reset_index(drop=True)
    
    for idx in range(len(dialog_data) - 1):
        current_row = dialog_data.iloc[idx]
        next_row = dialog_data.iloc[idx + 1]
        
        if (current_row['B4'] == 0 and 
            pd.notna(current_row['strategy_ollama_single']) and
            current_row['strategy_ollama_single'] in SELECTED_STRATEGIES and
            next_row['B4'] == 1 and
            pd.notna(next_row['interest_ollama_v2']) and
            str(next_row['interest_ollama_v2']).strip() != ''):
            
            strategy_interest_pairs.append({
                'strategy': current_row['strategy_ollama_single'],
                'interest': next_row['interest_ollama_v2']
            })

interest_pairs_df = pd.DataFrame(strategy_interest_pairs)

# ========= 5. АНАЛИЗ: СТРАТЕГИЯ -> DONATION =========
print("5. Анализ: Стратегия -> Donation...")

strategy_donation_pairs = []
for dialog_id in persuader_strategies['B2'].unique():
    dialog_strategies = persuader_strategies[persuader_strategies['B2'] == dialog_id]
    
    for _, row in dialog_strategies.iterrows():
        strategy_donation_pairs.append({
            'strategy': row['strategy_ollama_single'],
            'donated': row['donated'] if pd.notna(row['donated']) else 0
        })

donation_pairs_df = pd.DataFrame(strategy_donation_pairs)

# ========= 6. ПОДГОТОВКА ДАННЫХ ДЛЯ ВИЗУАЛИЗАЦИИ =========
print("\n6. Подготовка данных для визуализации...")

# Собираем статистику для каждой стратегии
joint_stats = []

for strategy in SELECTED_STRATEGIES:
    # Sentiment статистика
    sentiment_data = sentiment_pairs_df[sentiment_pairs_df['strategy'] == strategy]
    sentiment_counts = sentiment_data['sentiment'].value_counts()
    sentiment_total = len(sentiment_data)
    
    # Interest статистика
    interest_data = interest_pairs_df[interest_pairs_df['strategy'] == strategy]
    interest_counts = interest_data['interest'].value_counts()
    interest_total = len(interest_data)
    
    # Donation статистика
    donation_data = donation_pairs_df[donation_pairs_df['strategy'] == strategy]
    donation_counts = donation_data['donated'].value_counts()
    donation_total = len(donation_data)
    
    stats = {
        'strategy': strategy,
        # Sentiment
        'sentiment_negative': sentiment_counts.get('negative', 0),
        'sentiment_neutral': sentiment_counts.get('neutral', 0),
        'sentiment_positive': sentiment_counts.get('positive', 0),
        'sentiment_total': sentiment_total,
        'sentiment_negative_pct': (sentiment_counts.get('negative', 0) / sentiment_total * 100) if sentiment_total > 0 else 0,
        'sentiment_neutral_pct': (sentiment_counts.get('neutral', 0) / sentiment_total * 100) if sentiment_total > 0 else 0,
        'sentiment_positive_pct': (sentiment_counts.get('positive', 0) / sentiment_total * 100) if sentiment_total > 0 else 0,
        # Interest
        'interest_not_interested': interest_counts.get('Not Interested', 0),
        'interest_neutral': interest_counts.get('Neutral', 0),
        'interest_interested': interest_counts.get('Interested', 0),
        'interest_total': interest_total,
        'interest_not_interested_pct': (interest_counts.get('Not Interested', 0) / interest_total * 100) if interest_total > 0 else 0,
        'interest_neutral_pct': (interest_counts.get('Neutral', 0) / interest_total * 100) if interest_total > 0 else 0,
        'interest_interested_pct': (interest_counts.get('Interested', 0) / interest_total * 100) if interest_total > 0 else 0,
        # Donation
        'donation_no': donation_counts.get(0, 0),
        'donation_yes': donation_counts.get(1, 0),
        'donation_total': donation_total,
        'donation_no_pct': (donation_counts.get(0, 0) / donation_total * 100) if donation_total > 0 else 0,
        'donation_yes_pct': (donation_counts.get(1, 0) / donation_total * 100) if donation_total > 0 else 0,
    }
    joint_stats.append(stats)

joint_stats_df = pd.DataFrame(joint_stats)

# Сохраняем статистику
joint_stats_df.to_csv('joint_strategies_stats.csv', index=False)
print(f"✅ Статистика сохранена в: joint_strategies_stats.csv")

# ========= 7. ВИЗУАЛИЗАЦИЯ =========
print("\n7. Создание визуализации...")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Joint Effect of Selected Persuasion Strategies on Emotional Tone, Interest Dynamics, and Final Donation Outcome', 
             fontsize=16, fontweight='bold', y=1.02)

# График 1: Sentiment (Emotional Tone)
ax1 = axes[0]
x = np.arange(len(SELECTED_STRATEGIES))
width = 0.25

negative_pct = [joint_stats_df[joint_stats_df['strategy'] == s]['sentiment_negative_pct'].values[0] for s in SELECTED_STRATEGIES]
neutral_pct = [joint_stats_df[joint_stats_df['strategy'] == s]['sentiment_neutral_pct'].values[0] for s in SELECTED_STRATEGIES]
positive_pct = [joint_stats_df[joint_stats_df['strategy'] == s]['sentiment_positive_pct'].values[0] for s in SELECTED_STRATEGIES]

bars1 = ax1.bar(x - width, negative_pct, width, label='Negative', color='#d62728', alpha=0.8)
bars2 = ax1.bar(x, neutral_pct, width, label='Neutral', color='#ff7f0e', alpha=0.8)
bars3 = ax1.bar(x + width, positive_pct, width, label='Positive', color='#2ca02c', alpha=0.8)

ax1.set_xlabel('Strategy', fontsize=12, fontweight='bold')
ax1.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax1.set_title('Emotional Tone (Sentiment)', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels([s.replace(' ', '\n') for s in SELECTED_STRATEGIES], fontsize=9)
ax1.legend(loc='upper left')
ax1.set_ylim(0, 100)
ax1.grid(axis='y', alpha=0.3)

# Добавляем значения на столбцы
for i, strategy in enumerate(SELECTED_STRATEGIES):
    row = joint_stats_df[joint_stats_df['strategy'] == strategy].iloc[0]
    if row['sentiment_negative'] > 0:
        ax1.text(i - width, row['sentiment_negative_pct'] + 1, f"{row['sentiment_negative_pct']:.1f}%", 
                ha='center', va='bottom', fontsize=8)
    if row['sentiment_neutral'] > 0:
        ax1.text(i, row['sentiment_neutral_pct'] + 1, f"{row['sentiment_neutral_pct']:.1f}%", 
                ha='center', va='bottom', fontsize=8)
    if row['sentiment_positive'] > 0:
        ax1.text(i + width, row['sentiment_positive_pct'] + 1, f"{row['sentiment_positive_pct']:.1f}%", 
                ha='center', va='bottom', fontsize=8)

# График 2: Interest (Interest Dynamics)
ax2 = axes[1]
not_interested_pct = [joint_stats_df[joint_stats_df['strategy'] == s]['interest_not_interested_pct'].values[0] for s in SELECTED_STRATEGIES]
interest_neutral_pct = [joint_stats_df[joint_stats_df['strategy'] == s]['interest_neutral_pct'].values[0] for s in SELECTED_STRATEGIES]
interested_pct = [joint_stats_df[joint_stats_df['strategy'] == s]['interest_interested_pct'].values[0] for s in SELECTED_STRATEGIES]

bars4 = ax2.bar(x - width, not_interested_pct, width, label='Not Interested', color='#d62728', alpha=0.8)
bars5 = ax2.bar(x, interest_neutral_pct, width, label='Neutral', color='#ff7f0e', alpha=0.8)
bars6 = ax2.bar(x + width, interested_pct, width, label='Interested', color='#2ca02c', alpha=0.8)

ax2.set_xlabel('Strategy', fontsize=12, fontweight='bold')
ax2.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax2.set_title('Interest Dynamics', fontsize=13, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels([s.replace(' ', '\n') for s in SELECTED_STRATEGIES], fontsize=9)
ax2.legend(loc='upper left')
ax2.set_ylim(0, 100)
ax2.grid(axis='y', alpha=0.3)

# Добавляем значения на столбцы
for i, strategy in enumerate(SELECTED_STRATEGIES):
    row = joint_stats_df[joint_stats_df['strategy'] == strategy].iloc[0]
    if row['interest_not_interested'] > 0:
        ax2.text(i - width, row['interest_not_interested_pct'] + 1, f"{row['interest_not_interested_pct']:.1f}%", 
                ha='center', va='bottom', fontsize=8)
    if row['interest_neutral'] > 0:
        ax2.text(i, row['interest_neutral_pct'] + 1, f"{row['interest_neutral_pct']:.1f}%", 
                ha='center', va='bottom', fontsize=8)
    if row['interest_interested'] > 0:
        ax2.text(i + width, row['interest_interested_pct'] + 1, f"{row['interest_interested_pct']:.1f}%", 
                ha='center', va='bottom', fontsize=8)

# График 3: Donation (Final Donation Outcome)
ax3 = axes[2]
no_donation_pct = [joint_stats_df[joint_stats_df['strategy'] == s]['donation_no_pct'].values[0] for s in SELECTED_STRATEGIES]
yes_donation_pct = [joint_stats_df[joint_stats_df['strategy'] == s]['donation_yes_pct'].values[0] for s in SELECTED_STRATEGIES]

bars7 = ax3.bar(x - width/2, no_donation_pct, width, label='No Donation', color='#d62728', alpha=0.8)
bars8 = ax3.bar(x + width/2, yes_donation_pct, width, label='Donation', color='#2ca02c', alpha=0.8)

ax3.set_xlabel('Strategy', fontsize=12, fontweight='bold')
ax3.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax3.set_title('Final Donation Outcome', fontsize=13, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels([s.replace(' ', '\n') for s in SELECTED_STRATEGIES], fontsize=9)
ax3.legend(loc='upper left')
ax3.set_ylim(0, 100)
ax3.grid(axis='y', alpha=0.3)

# Добавляем значения на столбцы
for i, strategy in enumerate(SELECTED_STRATEGIES):
    row = joint_stats_df[joint_stats_df['strategy'] == strategy].iloc[0]
    if row['donation_no'] > 0:
        ax3.text(i - width/2, row['donation_no_pct'] + 1, f"{row['donation_no_pct']:.1f}%", 
                ha='center', va='bottom', fontsize=8)
    if row['donation_yes'] > 0:
        ax3.text(i + width/2, row['donation_yes_pct'] + 1, f"{row['donation_yes_pct']:.1f}%", 
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig("joint_strategies_effect.png", dpi=300, bbox_inches='tight')
print(f"✅ Визуализация сохранена в: joint_strategies_effect.png")
plt.close()

# ========= 8. ВЫВОД СТАТИСТИКИ =========
print("\n" + "="*80)
print("ДЕТАЛЬНАЯ СТАТИСТИКА")
print("="*80)

for strategy in SELECTED_STRATEGIES:
    row = joint_stats_df[joint_stats_df['strategy'] == strategy].iloc[0]
    print(f"\n{strategy}:")
    print(f"  Sentiment (n={int(row['sentiment_total'])}):")
    print(f"    - Negative: {row['sentiment_negative_pct']:.1f}% ({int(row['sentiment_negative'])})")
    print(f"    - Neutral: {row['sentiment_neutral_pct']:.1f}% ({int(row['sentiment_neutral'])})")
    print(f"    - Positive: {row['sentiment_positive_pct']:.1f}% ({int(row['sentiment_positive'])})")
    print(f"  Interest (n={int(row['interest_total'])}):")
    print(f"    - Not Interested: {row['interest_not_interested_pct']:.1f}% ({int(row['interest_not_interested'])})")
    print(f"    - Neutral: {row['interest_neutral_pct']:.1f}% ({int(row['interest_neutral'])})")
    print(f"    - Interested: {row['interest_interested_pct']:.1f}% ({int(row['interest_interested'])})")
    print(f"  Donation (n={int(row['donation_total'])}):")
    print(f"    - No Donation: {row['donation_no_pct']:.1f}% ({int(row['donation_no'])})")
    print(f"    - Donation: {row['donation_yes_pct']:.1f}% ({int(row['donation_yes'])})")

print("\n" + "="*80)
print("✅ АНАЛИЗ ЗАВЕРШЕН")
print("="*80)
print("\nСозданные файлы:")
print("   - joint_strategies_stats.csv")
print("   - joint_strategies_effect.png")

