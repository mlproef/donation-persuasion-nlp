import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import FULL_DIALOG, FULL_INFO, figure  # noqa: E402

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Используем backend без GUI
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Настройка для красивого отображения
rcParams['figure.figsize'] = 12, 8
rcParams['font.size'] = 12

# Загружаем данные
print("Загружаем данные...")
info_df = pd.read_csv(str(FULL_INFO))
dialog_df = pd.read_csv(str(FULL_DIALOG))

print(f"Загружено {len(info_df)} записей в full_info.csv")
print(f"Загружено {len(dialog_df)} сообщений в full_dialog.csv")

# ========= ОСНОВНОЙ АНАЛИЗ =========
print("\n" + "="*70)
print("ОСНОВНОЙ АНАЛИЗ БАЗЫ ДАННЫХ")
print("="*70)

# 1. Общая статистика по донатам
total_donations = info_df["B6"].sum()
total_people = len(info_df)
avg_donation = info_df["B6"].mean()
median_donation = info_df["B6"].median()

print(f"\n1. ОБЩАЯ СТАТИСТИКА:")
print(f"   Всего людей в базе: {total_people}")
print(f"   Общая сумма донатов: ${total_donations:.2f}")
print(f"   Средняя сумма доната: ${avg_donation:.2f}")
print(f"   Медианная сумма доната: ${median_donation:.2f}")

# 2. Анализ по ролям
persuaders = info_df[info_df["B4"] == 0].copy()
targets = info_df[info_df["B4"] == 1].copy()

print(f"\n2. АНАЛИЗ ПО РОЛЯМ:")
print(f"   Убеждающих (B4=0): {len(persuaders)}")
print(f"   Убеждаемых (B4=1): {len(targets)}")

# Статистика для убеждаемых (targets)
targets_donated = targets[targets["B6"] > 0]
targets_donation_rate = (len(targets_donated) / len(targets)) * 100
targets_avg_donation = targets["B6"].mean()
targets_median_donation = targets["B6"].median()
targets_total = targets["B6"].sum()

print(f"\n3. УБЕЖДАЕМЫЕ (B4=1) - ТЕ, КОГО УБЕЖДАЮТ:")
print(f"   Всего убеждаемых: {len(targets)}")
print(f"   Задонатили: {len(targets_donated)} ({targets_donation_rate:.1f}%)")
print(f"   Не задонатили: {len(targets) - len(targets_donated)} ({100 - targets_donation_rate:.1f}%)")
print(f"   Средняя сумма доната: ${targets_avg_donation:.2f}")
print(f"   Медианная сумма доната: ${targets_median_donation:.2f}")
print(f"   Общая сумма от убеждаемых: ${targets_total:.2f}")
if len(targets_donated) > 0:
    print(f"   Средняя сумма среди тех, кто задонатил: ${targets_donated['B6'].mean():.2f}")

# Статистика для убеждающих (persuaders)
persuaders_donated = persuaders[persuaders["B6"] > 0]
persuaders_donation_rate = (len(persuaders_donated) / len(persuaders)) * 100
persuaders_avg_donation = persuaders["B6"].mean()
persuaders_median_donation = persuaders["B6"].median()
persuaders_total = persuaders["B6"].sum()

print(f"\n4. УБЕЖДАЮЩИЕ (B4=0) - ТЕ, КТО УБЕЖДАЕТ:")
print(f"   Всего убеждающих: {len(persuaders)}")
print(f"   Задонатили: {len(persuaders_donated)} ({persuaders_donation_rate:.1f}%)")
print(f"   Не задонатили: {len(persuaders) - len(persuaders_donated)} ({100 - persuaders_donation_rate:.1f}%)")
print(f"   Средняя сумма доната: ${persuaders_avg_donation:.2f}")
print(f"   Медианная сумма доната: ${persuaders_median_donation:.2f}")
print(f"   Общая сумма от убеждающих: ${persuaders_total:.2f}")
if len(persuaders_donated) > 0:
    print(f"   Средняя сумма среди тех, кто задонатил: ${persuaders_donated['B6'].mean():.2f}")

# 5. Статистика по диалогам
unique_dialogs = info_df["B2"].nunique()
dialogs_with_donation = info_df[info_df["B6"] > 0]["B2"].nunique()
dialog_donation_rate = (dialogs_with_donation / unique_dialogs) * 100

print(f"\n5. СТАТИСТИКА ПО ДИАЛОГАМ:")
print(f"   Всего уникальных диалогов: {unique_dialogs}")
print(f"   Диалогов с донатом: {dialogs_with_donation} ({dialog_donation_rate:.1f}%)")

# ========= СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ =========
print("\n" + "="*70)
print("СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ")
print("="*70)

# Создаём фигуру с несколькими графиками
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# 1. Распределение донатов (гистограмма)
ax1 = fig.add_subplot(gs[0, 0])
donations_positive = info_df[info_df["B6"] > 0]["B6"]
ax1.hist(donations_positive, bins=50, edgecolor='black', alpha=0.7)
ax1.set_xlabel('Сумма доната ($)', fontsize=12)
ax1.set_ylabel('Количество людей', fontsize=12)
ax1.set_title('Распределение сумм донатов (только положительные)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.axvline(donations_positive.mean(), color='red', linestyle='--', linewidth=2, label=f'Среднее: ${donations_positive.mean():.2f}')
ax1.axvline(donations_positive.median(), color='green', linestyle='--', linewidth=2, label=f'Медиана: ${donations_positive.median():.2f}')
ax1.legend()

# 2. Процент задонативших по ролям
ax2 = fig.add_subplot(gs[0, 1])
roles = ['Убеждающие\n(B4=0)', 'Убеждаемые\n(B4=1)']
donation_rates = [persuaders_donation_rate, targets_donation_rate]
colors = ['#FF6B6B', '#4ECDC4']
bars = ax2.bar(roles, donation_rates, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
ax2.set_ylabel('Процент задонативших (%)', fontsize=12)
ax2.set_title('Процент людей, которые задонатили', fontsize=14, fontweight='bold')
ax2.set_ylim(0, max(donation_rates) * 1.2)
ax2.grid(True, alpha=0.3, axis='y')

# Добавляем значения на столбцы
for bar, rate in zip(bars, donation_rates):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{rate:.1f}%',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

# 3. Сравнение средних сумм донатов
ax3 = fig.add_subplot(gs[1, 0])
avg_donations = [persuaders_avg_donation, targets_avg_donation]
bars3 = ax3.bar(roles, avg_donations, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
ax3.set_ylabel('Средняя сумма доната ($)', fontsize=12)
ax3.set_title('Средняя сумма доната по ролям', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

for bar, avg in zip(bars3, avg_donations):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'${avg:.2f}',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

# 4. Круговая диаграмма: задонатили vs не задонатили (убеждаемые)
ax4 = fig.add_subplot(gs[1, 1])
targets_donated_count = len(targets_donated)
targets_not_donated_count = len(targets) - targets_donated_count
labels = ['Задонатили', 'Не задонатили']
sizes = [targets_donated_count, targets_not_donated_count]
colors_pie = ['#4ECDC4', '#FFE66D']
explode = (0.05, 0)
ax4.pie(sizes, explode=explode, labels=labels, colors=colors_pie, autopct='%1.1f%%',
        shadow=True, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
ax4.set_title('Распределение убеждаемых:\nЗадонатили vs Не задонатили', 
              fontsize=14, fontweight='bold')

# 5. Box plot: распределение донатов по ролям
ax5 = fig.add_subplot(gs[2, 0])
donation_data = [
    persuaders[persuaders["B6"] > 0]["B6"].values if len(persuaders[persuaders["B6"] > 0]) > 0 else [0],
    targets[targets["B6"] > 0]["B6"].values if len(targets[targets["B6"] > 0]) > 0 else [0]
]
bp = ax5.boxplot(donation_data, tick_labels=['Убеждающие', 'Убеждаемые'], 
                 patch_artist=True, showmeans=True)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax5.set_ylabel('Сумма доната ($)', fontsize=12)
ax5.set_title('Распределение сумм донатов по ролям\n(только положительные донаты)', 
              fontsize=14, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')

# 6. Сводная статистика (текстовая панель)
ax6 = fig.add_subplot(gs[2, 1])
ax6.axis('off')
stats_text = f"""
ОСНОВНЫЕ СТАТИСТИКИ БАЗЫ ДАННЫХ

Общая статистика:
• Всего людей: {total_people}
• Общая сумма донатов: ${total_donations:.2f}
• Средняя сумма: ${avg_donation:.2f}
• Медианная сумма: ${median_donation:.2f}

Убеждаемые (B4=1):
• Всего: {len(targets)}
• Задонатили: {len(targets_donated)} ({targets_donation_rate:.1f}%)
• Средняя сумма: ${targets_avg_donation:.2f}
• Общая сумма: ${targets_total:.2f}

Убеждающие (B4=0):
• Всего: {len(persuaders)}
• Задонатили: {len(persuaders_donated)} ({persuaders_donation_rate:.1f}%)
• Средняя сумма: ${persuaders_avg_donation:.2f}
• Общая сумма: ${persuaders_total:.2f}

Диалоги:
• Всего диалогов: {unique_dialogs}
• С донатом: {dialogs_with_donation} ({dialog_donation_rate:.1f}%)
"""
ax6.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
         family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Общий заголовок
fig.suptitle('АНАЛИЗ БАЗЫ ДАННЫХ: СТАТИСТИКА ПО ДОНАТАМ', 
             fontsize=18, fontweight='bold', y=0.98)

# Сохраняем как изображение
output_file = str(figure("donation_analysis.png"))
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Визуализация сохранена в: {output_file}")

# Также создаём отдельный график с более детальной статистикой
fig2, axes = plt.subplots(2, 2, figsize=(16, 12))
fig2.suptitle('ДЕТАЛЬНЫЙ АНАЛИЗ ДОНАТОВ', fontsize=18, fontweight='bold', y=0.98)

# 1. Распределение донатов (логарифмическая шкала)
ax = axes[0, 0]
donations_positive = info_df[info_df["B6"] > 0]["B6"]
ax.hist(donations_positive, bins=50, edgecolor='black', alpha=0.7)
ax.set_xlabel('Сумма доната ($)', fontsize=12)
ax.set_ylabel('Количество людей', fontsize=12)
ax.set_title('Распределение сумм донатов (линейная шкала)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# 2. Распределение донатов (логарифмическая шкала)
ax = axes[0, 1]
ax.hist(donations_positive, bins=50, edgecolor='black', alpha=0.7)
ax.set_xlabel('Сумма доната ($)', fontsize=12)
ax.set_ylabel('Количество людей', fontsize=12)
ax.set_title('Распределение сумм донатов (логарифмическая шкала)', fontsize=14, fontweight='bold')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)

# 3. Сравнение сумм донатов (только те, кто задонатил)
ax = axes[1, 0]
if len(persuaders_donated) > 0 and len(targets_donated) > 0:
    comparison_data = [
        persuaders_donated["B6"].values,
        targets_donated["B6"].values
    ]
    bp = ax.boxplot(comparison_data, tick_labels=['Убеждающие', 'Убеждаемые'], 
                    patch_artist=True, showmeans=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel('Сумма доната ($)', fontsize=12)
    ax.set_title('Сравнение сумм донатов\n(только среди тех, кто задонатил)', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

# 4. Количество диалогов
ax = axes[1, 1]
dialog_stats = {
    'Всего диалогов': unique_dialogs,
    'С донатом': dialogs_with_donation,
    'Без доната': unique_dialogs - dialogs_with_donation
}
bars = ax.bar(dialog_stats.keys(), dialog_stats.values(), 
              color=['#95E1D3', '#F38181', '#AA96DA'], 
              edgecolor='black', linewidth=2, alpha=0.8)
ax.set_ylabel('Количество диалогов', fontsize=12)
ax.set_title('Статистика по диалогам', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

for bar, value in zip(bars, dialog_stats.values()):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{value}',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
output_file2 = str(figure("donation_analysis_detailed.png"))
plt.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Детальная визуализация сохранена в: {output_file2}")

print("\n" + "="*70)
print("АНАЛИЗ ЗАВЕРШЁН!")
print("="*70)
print(f"\nСозданы файлы:")
print(f"  1. {output_file} - основная визуализация")
print(f"  2. {output_file2} - детальная визуализация")
