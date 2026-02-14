import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("ANALYZING RESULTS FROM test_batch_sentiment_results.csv")
print("="*80)

# Load data
print("\n1. Loading data...")
df = pd.read_csv("test_batch_sentiment_results.csv")

print(f"   - Total rows: {len(df):,}")
print(f"   - Target messages (B4=1): {len(df[df['B4'] == 1]):,}")
print(f"   - Persuader messages (B4=0): {len(df[df['B4'] == 0]):,}")

# Analyze sentiment
target_messages = df[df['B4'] == 1].copy()

sentiment_filled = target_messages[
    target_messages['sentiment_ollama'].notna() & 
    (target_messages['sentiment_ollama'].astype(str).str.strip() != '')
]

print(f"\n2. Sentiment statistics:")
print(f"   - Total target messages: {len(target_messages):,}")
print(f"   - Messages with sentiment: {len(sentiment_filled):,}")
print(f"   - Analysis coverage: {len(sentiment_filled)/len(target_messages)*100:.1f}%")
print(f"   - Messages without sentiment: {len(target_messages) - len(sentiment_filled):,}")

# ========= 1. SENTIMENT DISTRIBUTION =========
print("\n" + "="*80)
print("SENTIMENT DISTRIBUTION")
print("="*80)

if len(sentiment_filled) > 0:
    sentiment_counts = sentiment_filled['sentiment_ollama'].value_counts()
    print(f"\nTotal unique sentiments: {len(sentiment_counts)}")
    print(f"\nDistribution:")
    
    total = len(sentiment_filled)
    for sentiment, count in sentiment_counts.items():
        pct = count / total * 100
        print(f"   {sentiment:10s}: {count:5d} ({pct:5.2f}%)")
else:
    print("\n⚠️ No analyzed messages found!")
    sentiment_counts = pd.Series()

# ========= 2. DIALOG ANALYSIS =========
print("\n" + "="*80)
print("DIALOG ANALYSIS")
print("="*80)

dialog_stats = []
for dialog_id in target_messages['B2'].unique():
    dialog_data = target_messages[target_messages['B2'] == dialog_id]
    dialog_sentiment = sentiment_filled[sentiment_filled['B2'] == dialog_id]
    
    dialog_stats.append({
        'B2': dialog_id,
        'total_messages': len(dialog_data),
        'messages_with_sentiment': len(dialog_sentiment),
        'coverage_pct': len(dialog_sentiment) / len(dialog_data) * 100 if len(dialog_data) > 0 else 0,
        'unique_sentiments': dialog_sentiment['sentiment_ollama'].nunique() if len(dialog_sentiment) > 0 else 0,
    })

dialog_df = pd.DataFrame(dialog_stats)

print(f"\nTotal unique dialogs: {len(dialog_df)}")
print(f"Dialogs with at least one sentiment: {(dialog_df['messages_with_sentiment'] > 0).sum()}")
print(f"Average coverage percentage: {dialog_df['coverage_pct'].mean():.1f}%")
print(f"Median coverage percentage: {dialog_df['coverage_pct'].median():.1f}%")

# Coverage distribution
coverage_bins = [0, 25, 50, 75, 100]
coverage_labels = ['0-25%', '25-50%', '50-75%', '75-100%']
dialog_df['coverage_group'] = pd.cut(dialog_df['coverage_pct'], bins=coverage_bins, labels=coverage_labels)
print(f"\nDialog coverage distribution:")
for label in coverage_labels:
    count = (dialog_df['coverage_group'] == label).sum()
    if count > 0:
        print(f"   {label}: {count} dialogs")

# ========= 3. SENTIMENT BY POSITION IN DIALOG =========
print("\n" + "="*80)
print("SENTIMENT BY POSITION IN DIALOG")
print("="*80)

if len(sentiment_filled) > 0:
    # Determine message position in dialog
    sentiment_filled = sentiment_filled.copy()
    sentiment_filled['turn_rank'] = sentiment_filled.groupby('B2')['Turn'].rank(method='first')
    sentiment_filled['position'] = pd.cut(
        sentiment_filled['turn_rank'],
        bins=[0, 1, 3, 6, 100],
        labels=['First', 'Early (2-3)', 'Middle (4-6)', 'Late (7+)']
    )
    
    print("\nSentiment distribution by position in dialog:")
    for position in ['First', 'Early (2-3)', 'Middle (4-6)', 'Late (7+)']:
        pos_data = sentiment_filled[sentiment_filled['position'] == position]
        if len(pos_data) > 0:
            sentiment_dist = pos_data['sentiment_ollama'].value_counts()
            print(f"\n   {position}:")
            for sentiment, count in sentiment_dist.items():
                pct = count / len(pos_data) * 100
                print(f"      {sentiment:10s}: {count:4d} ({pct:5.2f}%)")

# ========= 4. VISUALIZATION =========
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

if len(sentiment_filled) > 0:
    fig = plt.figure(figsize=(16, 10))
    
    # График 1: Распределение sentiment
    ax1 = plt.subplot(2, 3, 1)
    colors = {'negative': '#d62728', 'neutral': '#ff7f0e', 'positive': '#2ca02c'}
    sentiment_order = ['negative', 'neutral', 'positive']
    sentiment_counts_plot = sentiment_counts.reindex([s for s in sentiment_order if s in sentiment_counts.index])
    bars = ax1.bar(sentiment_counts_plot.index, sentiment_counts_plot.values, 
                   color=[colors.get(s, 'gray') for s in sentiment_counts_plot.index])
    ax1.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Messages')
    ax1.tick_params(axis='x', rotation=45)
    for bar in bars:
        height = bar.get_height()
        pct = height / len(sentiment_filled) * 100
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'{int(height)}\n({pct:.1f}%)',
                 ha='center', va='bottom')
    
    # График 2: Покрытие диалогов
    ax2 = plt.subplot(2, 3, 2)
    coverage_counts = dialog_df['coverage_group'].value_counts().sort_index()
    bars2 = ax2.bar(range(len(coverage_counts)), coverage_counts.values, color='steelblue')
    ax2.set_xticks(range(len(coverage_counts)))
    ax2.set_xticklabels(coverage_counts.index, rotation=45, ha='right')
    ax2.set_ylabel('Number of Dialogs')
    ax2.set_title('Dialog Coverage Distribution', fontweight='bold')
    for i, (label, val) in enumerate(coverage_counts.items()):
        ax2.text(i, val, f' {val}', va='bottom', fontsize=8)
    
    # График 3: Круговая диаграмма sentiment
    ax3 = plt.subplot(2, 3, 3)
    colors_pie = [colors.get(s, 'gray') for s in sentiment_counts_plot.index]
    wedges, texts, autotexts = ax3.pie(sentiment_counts_plot.values, 
                                       labels=sentiment_counts_plot.index,
                                       autopct='%1.1f%%', 
                                       colors=colors_pie, 
                                       startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax3.set_title('Sentiment Distribution (Pie Chart)', fontweight='bold')
    
    # График 4: Sentiment по позиции в диалоге
    if len(sentiment_filled) > 0:
        ax4 = plt.subplot(2, 3, 4)
        position_sentiment = pd.crosstab(sentiment_filled['position'], sentiment_filled['sentiment_ollama'])
        position_sentiment.plot(kind='bar', ax=ax4, color=[colors.get(c, 'gray') for c in position_sentiment.columns], width=0.8)
        ax4.set_xlabel('Position in Dialog')
        ax4.set_ylabel('Count')
        ax4.set_title('Sentiment by Position in Dialog', fontweight='bold')
        ax4.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.tick_params(axis='x', rotation=45)
    
    # График 5: Средний sentiment по диалогам
    ax5 = plt.subplot(2, 3, 5)
    # Считаем средний sentiment для каждого диалога (negative=-1, neutral=0, positive=1)
    dialog_sentiment_scores = []
    for dialog_id in dialog_df['B2']:
        dialog_sentiment = sentiment_filled[sentiment_filled['B2'] == dialog_id]['sentiment_ollama']
        if len(dialog_sentiment) > 0:
            score = (dialog_sentiment == 'positive').sum() - (dialog_sentiment == 'negative').sum()
            dialog_sentiment_scores.append(score / len(dialog_sentiment))
        else:
            dialog_sentiment_scores.append(0)
    
    dialog_df['avg_sentiment_score'] = dialog_sentiment_scores
    ax5.hist(dialog_df['avg_sentiment_score'], bins=20, color='coral', edgecolor='black')
    ax5.set_xlabel('Average Sentiment Score (-1 to +1)')
    ax5.set_ylabel('Number of Dialogs')
    ax5.set_title('Average Sentiment Score per Dialog', fontweight='bold')
    ax5.axvline(x=0, color='red', linestyle='--', alpha=0.5)
    
    # График 6: Процент покрытия vs количество сообщений
    ax6 = plt.subplot(2, 3, 6)
    ax6.scatter(dialog_df['total_messages'], dialog_df['coverage_pct'], alpha=0.5, color='steelblue')
    ax6.set_xlabel('Total Messages in Dialog')
    ax6.set_ylabel('Coverage Percentage (%)')
    ax6.set_title('Coverage vs Dialog Length', fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = "sentiment_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nChart saved: {output_file}")
else:
    print("\n⚠️ No data for visualization!")

# ========= 5. SAVING RESULTS =========
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Detailed sentiment statistics
if len(sentiment_filled) > 0:
    sentiment_details = []
    for sentiment in sentiment_counts.index:
        sentiment_data = sentiment_filled[sentiment_filled['sentiment_ollama'] == sentiment]
        sentiment_details.append({
            'sentiment': sentiment,
            'count': len(sentiment_data),
            'percentage': len(sentiment_data) / len(sentiment_filled) * 100,
            'dialogs_with_sentiment': sentiment_data['B2'].nunique(),
            'avg_per_dialog': len(sentiment_data) / sentiment_data['B2'].nunique() if sentiment_data['B2'].nunique() > 0 else 0,
        })
    
    sentiment_details_df = pd.DataFrame(sentiment_details).sort_values('count', ascending=False)
    sentiment_details_df.to_csv('sentiment_details.csv', index=False)
    print(f"Sentiment details saved: sentiment_details.csv")

# Dialog statistics
dialog_df.to_csv('sentiment_dialog_stats.csv', index=False)
print(f"Dialog statistics saved: sentiment_dialog_stats.csv")

# Сводная статистика
summary = {
    'Metric': [
        'Total target messages',
        'Messages with sentiment',
        'Coverage percentage',
        'Messages without sentiment',
        'Unique sentiments found',
        'Total dialogs',
        'Dialogs with at least one sentiment',
        'Average coverage per dialog',
    ],
    'Value': [
        len(target_messages),
        len(sentiment_filled),
        f"{len(sentiment_filled)/len(target_messages)*100:.1f}%",
        len(target_messages) - len(sentiment_filled),
        len(sentiment_counts) if len(sentiment_filled) > 0 else 0,
        len(dialog_df),
        (dialog_df['messages_with_sentiment'] > 0).sum(),
        f"{dialog_df['coverage_pct'].mean():.1f}%",
    ]
}

# Add sentiment distribution
if len(sentiment_filled) > 0:
    for sentiment in sentiment_counts.index:
        summary['Metric'].append(f'{sentiment} count')
        summary['Value'].append(int(sentiment_counts[sentiment]))
        summary['Metric'].append(f'{sentiment} percentage')
        summary['Value'].append(f"{sentiment_counts[sentiment]/len(sentiment_filled)*100:.2f}%")

summary_df = pd.DataFrame(summary)
summary_df.to_csv('sentiment_summary.csv', index=False)
print(f"Summary statistics saved: sentiment_summary.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETED")
print("="*80)

