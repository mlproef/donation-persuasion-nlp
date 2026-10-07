import pandas as pd
import numpy as np
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Загружаем данные
print("Загружаем данные...")
clustered = pd.read_csv("clustered_messages.csv")
labeled = pd.read_csv("reaction_annotation_labeled1.csv", sep=";")
full_info = pd.read_csv("full_info.csv")

# Объединяем кластеры с размеченными данными
print("\nОбъединяем данные...")
merged = clustered.merge(
    labeled[["B2", "Turn", "label"]], 
    on=["B2", "Turn"], 
    how="left"
)

# Добавляем информацию о донатах
full_info_target = full_info[full_info["B4"] == 1][["B2", "B6"]].copy()
full_info_target["donated"] = (full_info_target["B6"] > 0).astype(int)
merged = merged.merge(full_info_target[["B2", "donated"]], on="B2", how="left")

print(f"Всего сообщений в кластерах: {len(clustered)}")
print(f"Размеченных сообщений: {merged['label'].notna().sum()}")
print(f"Сообщений с информацией о донате: {merged['donated'].notna().sum()}")

# ========= 1. АНАЛИЗ КЛАСТЕРОВ =========
print("\n" + "="*70)
print("АНАЛИЗ КЛАСТЕРОВ")
print("="*70)

for cluster_id in sorted(merged["cluster"].unique()):
    cluster_data = merged[merged["cluster"] == cluster_id]
    labeled_in_cluster = cluster_data[cluster_data["label"].notna()]
    
    print(f"\n{'='*70}")
    print(f"КЛАСТЕР {cluster_id}")
    print(f"{'='*70}")
    print(f"Всего сообщений: {len(cluster_data)}")
    print(f"Размеченных сообщений: {len(labeled_in_cluster)}")
    
    if len(labeled_in_cluster) > 0:
        label_dist = labeled_in_cluster["label"].value_counts().sort_index()
        print(f"\nРаспределение меток (0=отказ, 1=нейтрально, 2=заинтересован):")
        for label, count in label_dist.items():
            pct = count / len(labeled_in_cluster) * 100
            label_name = {0: "отказ", 1: "нейтрально", 2: "заинтересован"}.get(label, "?")
            print(f"  {label} ({label_name}): {count} ({pct:.1f}%)")
        
        # Доминирующая метка
        dominant_label = label_dist.idxmax()
        dominant_pct = label_dist.max() / len(labeled_in_cluster) * 100
        print(f"\nДоминирующая метка: {dominant_label} ({dominant_pct:.1f}%)")
    
    # Информация о донатах
    donated_data = cluster_data[cluster_data["donated"].notna()]
    if len(donated_data) > 0:
        donation_rate = donated_data["donated"].mean() * 100
        print(f"\nПроцент донатов (среди уникальных диалогов): {donation_rate:.1f}%")
    
    # Примеры сообщений
    print(f"\nПримеры сообщений (первые 5):")
    for idx, row in cluster_data.head(5).iterrows():
        label_str = ""
        if pd.notna(row["label"]):
            label_str = f" [метка: {int(row['label'])}]"
        print(f"  - {row['Unit'][:100]}{label_str}")

# ========= 2. СРАВНЕНИЕ КЛАСТЕРОВ С МЕТКАМИ =========
print("\n" + "="*70)
print("СРАВНЕНИЕ КЛАСТЕРОВ С РУЧНЫМИ МЕТКАМИ")
print("="*70)

# Матрица соответствия кластер-метка
labeled_only = merged[merged["label"].notna()].copy()
confusion_data = []

for cluster_id in sorted(labeled_only["cluster"].unique()):
    for label_id in sorted(labeled_only["label"].unique()):
        count = len(labeled_only[
            (labeled_only["cluster"] == cluster_id) & 
            (labeled_only["label"] == label_id)
        ])
        confusion_data.append({
            "cluster": cluster_id,
            "label": int(label_id),
            "count": count
        })

confusion_df = pd.DataFrame(confusion_data)
confusion_matrix = confusion_df.pivot(index="cluster", columns="label", values="count").fillna(0)

print("\nМатрица соответствия (кластер × метка):")
print(confusion_matrix)

# Точность соответствия (если кластер соответствует одной метке)
print("\nТочность соответствия кластеров меткам:")
for cluster_id in confusion_matrix.index:
    total = confusion_matrix.loc[cluster_id].sum()
    if total > 0:
        max_label = confusion_matrix.loc[cluster_id].idxmax()
        max_count = confusion_matrix.loc[cluster_id, max_label]
        accuracy = max_count / total * 100
        print(f"  Кластер {cluster_id}: {accuracy:.1f}% соответствуют метке {max_label}")

# ========= 3. АНАЛИЗ ПО ДОНАТАМ =========
print("\n" + "="*70)
print("АНАЛИЗ КЛАСТЕРОВ ПО ДОНАТАМ")
print("="*70)

# Берем только уникальные диалоги для анализа донатов
unique_dialogs = merged.drop_duplicates(subset=["B2", "cluster"])
donated_analysis = unique_dialogs[unique_dialogs["donated"].notna()]

print("\nРаспределение донатов по кластерам:")
for cluster_id in sorted(donated_analysis["cluster"].unique()):
    cluster_dialogs = donated_analysis[donated_analysis["cluster"] == cluster_id]
    donation_rate = cluster_dialogs["donated"].mean() * 100
    total = len(cluster_dialogs)
    donated_count = cluster_dialogs["donated"].sum()
    print(f"  Кластер {cluster_id}: {donated_count}/{total} ({donation_rate:.1f}%)")

# ========= 4. ВИЗУАЛИЗАЦИЯ =========
print("\nСоздаем визуализации...")

fig = plt.figure(figsize=(16, 12))

# График 1: Распределение меток по кластерам
ax1 = plt.subplot(2, 3, 1)
confusion_matrix_plot = confusion_matrix.div(confusion_matrix.sum(axis=1), axis=0) * 100
# Заменяем sns.heatmap на matplotlib
im = ax1.imshow(confusion_matrix_plot.values, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
ax1.set_xticks(range(len(confusion_matrix_plot.columns)))
ax1.set_yticks(range(len(confusion_matrix_plot.index)))
ax1.set_xticklabels(confusion_matrix_plot.columns)
ax1.set_yticklabels(confusion_matrix_plot.index)
plt.colorbar(im, ax=ax1, label='%')
# Добавляем аннотации с процентами
for i in range(len(confusion_matrix_plot.index)):
    for j in range(len(confusion_matrix_plot.columns)):
        value = confusion_matrix_plot.iloc[i, j]
        if not np.isnan(value):
            ax1.text(j, i, f'{value:.1f}',
                    ha="center", va="center", color="black", fontweight='bold')
ax1.set_title('Распределение меток по кластерам (%)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Метка (0=отказ, 1=нейтрально, 2=заинтересован)')
ax1.set_ylabel('Кластер')

# График 2: Количество сообщений по кластерам
ax2 = plt.subplot(2, 3, 2)
cluster_counts = merged["cluster"].value_counts().sort_index()
ax2.bar(cluster_counts.index, cluster_counts.values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax2.set_title('Количество сообщений по кластерам', fontsize=12, fontweight='bold')
ax2.set_xlabel('Кластер')
ax2.set_ylabel('Количество сообщений')
for i, v in enumerate(cluster_counts.values):
    ax2.text(i, v, str(v), ha='center', va='bottom')

# График 3: Процент донатов по кластерам
ax3 = plt.subplot(2, 3, 3)
donation_by_cluster = []
for cluster_id in sorted(donated_analysis["cluster"].unique()):
    cluster_dialogs = donated_analysis[donated_analysis["cluster"] == cluster_id]
    donation_rate = cluster_dialogs["donated"].mean() * 100
    donation_by_cluster.append(donation_rate)
ax3.bar(range(len(donation_by_cluster)), donation_by_cluster, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax3.set_title('Процент донатов по кластерам', fontsize=12, fontweight='bold')
ax3.set_xlabel('Кластер')
ax3.set_ylabel('Процент донатов (%)')
ax3.set_xticks(range(len(donation_by_cluster)))
ax3.set_xticklabels(range(len(donation_by_cluster)))
for i, v in enumerate(donation_by_cluster):
    ax3.text(i, v, f'{v:.1f}%', ha='center', va='bottom')

# График 4: Распределение меток в каждом кластере (столбчатая диаграмма)
ax4 = plt.subplot(2, 3, 4)
if len(labeled_only) > 0:
    cluster_label_counts = labeled_only.groupby(["cluster", "label"]).size().unstack(fill_value=0)
    cluster_label_counts.plot(kind='bar', stacked=True, ax=ax4, 
                              color=['#d62728', '#ff7f0e', '#2ca02c'])
    ax4.set_title('Распределение меток по кластерам', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Кластер')
    ax4.set_ylabel('Количество сообщений')
    ax4.legend(['Отказ (0)', 'Нейтрально (1)', 'Заинтересован (2)'])
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=0)

# График 5: Средняя длина сообщений по кластерам
ax5 = plt.subplot(2, 3, 5)
avg_lengths = merged.groupby("cluster")["Unit"].apply(lambda x: x.astype(str).str.len().mean())
ax5.bar(avg_lengths.index, avg_lengths.values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax5.set_title('Средняя длина сообщений по кластерам', fontsize=12, fontweight='bold')
ax5.set_xlabel('Кластер')
ax5.set_ylabel('Средняя длина (символов)')
for i, v in enumerate(avg_lengths.values):
    ax5.text(i, v, f'{v:.0f}', ha='center', va='bottom')

# График 6: Соотношение размеченных/неразмеченных
ax6 = plt.subplot(2, 3, 6)
labeled_counts = merged.groupby("cluster")["label"].apply(lambda x: x.notna().sum())
total_counts = merged.groupby("cluster").size()
unlabeled_counts = total_counts - labeled_counts
x = np.arange(len(labeled_counts))
ax6.bar(x, labeled_counts.values, label='Размеченные', color='#2ca02c')
ax6.bar(x, unlabeled_counts.values, bottom=labeled_counts.values, label='Неразмеченные', color='#d62728')
ax6.set_title('Размеченные vs неразмеченные сообщения', fontsize=12, fontweight='bold')
ax6.set_xlabel('Кластер')
ax6.set_ylabel('Количество сообщений')
ax6.set_xticks(x)
ax6.set_xticklabels(labeled_counts.index)
ax6.legend()

plt.tight_layout()
plt.savefig('cluster_analysis_detailed.png', dpi=300, bbox_inches='tight')
print("График сохранен: cluster_analysis_detailed.png")
plt.close()

# ========= 5. ВЫВОДЫ И РЕКОМЕНДАЦИИ =========
print("\n" + "="*70)
print("ВЫВОДЫ И РЕКОМЕНДАЦИИ")
print("="*70)

# Определяем, какой кластер соответствует какой метке
cluster_to_label = {}
for cluster_id in confusion_matrix.index:
    dominant_label = confusion_matrix.loc[cluster_id].idxmax()
    accuracy = confusion_matrix.loc[cluster_id, dominant_label] / confusion_matrix.loc[cluster_id].sum() * 100
    cluster_to_label[cluster_id] = (dominant_label, accuracy)

print("\nИнтерпретация кластеров:")
for cluster_id, (label, acc) in sorted(cluster_to_label.items()):
    label_name = {0: "ОТКАЗ", 1: "НЕЙТРАЛЬНО", 2: "ЗАИНТЕРЕСОВАН"}.get(label, "?")
    print(f"  Кластер {cluster_id} → {label_name} (точность: {acc:.1f}%)")

print("\nРекомендации:")
print("  1. Если кластеры хорошо соответствуют меткам, можно использовать их для:")
print("     - Автоматической разметки новых данных")
print("     - Поиска проблемных мест в классификаторе")
print("     - Балансировки датасета для fine-tuning")
print("  2. Если соответствие слабое, рассмотрите:")
print("     - Изменение количества кластеров (k)")
print(" - Использование других эмбеддингов (например, с контекстом)")
print("     - Комбинирование кластеризации с вашими метками")

print("\n" + "="*70)
print("АНАЛИЗ ЗАВЕРШЕН")
print("="*70)