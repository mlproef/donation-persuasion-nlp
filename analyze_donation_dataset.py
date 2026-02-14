import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("="*80)
print("DONATION DATASET ANALYSIS")
print("="*80)

# Load data
print("\n1. Loading data...")
info_df = pd.read_csv("full_info.csv")

print(f"   - Loaded {len(info_df)} rows from full_info.csv")
print(f"   - Columns: {list(info_df.columns)}")

# Analyze donations
print("\n2. Analyzing donations...")

# Check B6 column (donation amount)
info_df['donated'] = (info_df['B6'] > 0).astype(int)
info_df['donation_amount'] = info_df['B6'].fillna(0)

# Analysis by role (B4: 0 = persuader, 1 = target)
print("\n" + "="*80)
print("DONATION STATISTICS BY ROLE")
print("="*80)

# Overall statistics
total_people = len(info_df)
total_donated = info_df['donated'].sum()
donation_rate = (total_donated / total_people * 100) if total_people > 0 else 0

print(f"\nOverall Statistics:")
print(f"   Total people: {total_people:,}")
print(f"   People who donated: {total_donated:,}")
print(f"   Donation rate: {donation_rate:.2f}%")
print(f"   People who did not donate: {total_people - total_donated:,} ({(100 - donation_rate):.2f}%)")

# Statistics by role
for role in [0, 1]:
    role_name = "Persuader" if role == 0 else "Target"
    role_data = info_df[info_df['B4'] == role]
    role_total = len(role_data)
    role_donated = role_data['donated'].sum()
    role_rate = (role_donated / role_total * 100) if role_total > 0 else 0
    
    print(f"\n{role_name} (B4={role}):")
    print(f"   Total: {role_total:,}")
    print(f"   Donated: {role_donated:,} ({role_rate:.2f}%)")
    print(f"   Did not donate: {role_total - role_donated:,} ({(100 - role_rate):.2f}%)")

# Analysis by dialog
print("\n" + "="*80)
print("DONATION STATISTICS BY DIALOG")
print("="*80)

dialog_stats = info_df.groupby('B2').agg({
    'donated': ['sum', 'count'],
    'donation_amount': ['sum', 'max', 'mean']
}).reset_index()

dialog_stats.columns = ['B2', 'n_donated', 'n_people', 'total_donation', 'max_donation', 'avg_donation']
dialog_stats['has_donation'] = (dialog_stats['n_donated'] > 0).astype(int)
dialog_stats['donation_rate'] = (dialog_stats['n_donated'] / dialog_stats['n_people'] * 100)

total_dialogs = len(dialog_stats)
dialogs_with_donation = dialog_stats['has_donation'].sum()
dialog_donation_rate = (dialogs_with_donation / total_dialogs * 100) if total_dialogs > 0 else 0

print(f"\nDialog-level Statistics:")
print(f"   Total dialogs: {total_dialogs:,}")
print(f"   Dialogs with at least one donation: {dialogs_with_donation:,} ({dialog_donation_rate:.2f}%)")
print(f"   Dialogs with no donations: {total_dialogs - dialogs_with_donation:,} ({(100 - dialog_donation_rate):.2f}%)")

# Donation amounts statistics
donation_amounts = info_df[info_df['donated'] == 1]['donation_amount']
if len(donation_amounts) > 0:
    print(f"\nDonation Amount Statistics (for people who donated):")
    print(f"   Mean: ${donation_amounts.mean():.2f}")
    print(f"   Median: ${donation_amounts.median():.2f}")
    print(f"   Min: ${donation_amounts.min():.2f}")
    print(f"   Max: ${donation_amounts.max():.2f}")
    print(f"   Standard deviation: ${donation_amounts.std():.2f}")
    print(f"   Total amount donated: ${donation_amounts.sum():.2f}")

# Save statistics
dialog_stats.to_csv('donation_dataset_stats.csv', index=False)
print(f"\n✅ Dialog statistics saved to: donation_dataset_stats.csv")

# ========= 3. VISUALIZATION =========
print("\n3. Creating visualizations...")

# Figure 1: Overall donation rate
fig1, ax1 = plt.subplots(figsize=(8, 6))
donation_counts = [total_people - total_donated, total_donated]
labels = ['No Donation', 'Donation']
colors = ['#d62728', '#2ca02c']
explode = (0, 0.1)

wedges, texts, autotexts = ax1.pie(donation_counts, labels=labels, autopct='%1.1f%%', 
                                     colors=colors, explode=explode, startangle=90,
                                     textprops={'fontsize': 12, 'fontweight': 'bold'})
ax1.set_title('Overall Donation Rate', fontsize=16, fontweight='bold', pad=20)
ax1.text(0, -1.3, f'Total: {total_people:,} people', ha='center', fontsize=11, 
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig("donation_overall_rate.png", dpi=300, bbox_inches='tight')
print(f"✅ Graph 1 saved: donation_overall_rate.png")
plt.close(fig1)

# Figure 2: Donation rate by role
fig2, ax2 = plt.subplots(figsize=(10, 6))
roles = ['Persuader', 'Target']
role_donated = [info_df[info_df['B4'] == 0]['donated'].sum(), 
                info_df[info_df['B4'] == 1]['donated'].sum()]
role_total = [len(info_df[info_df['B4'] == 0]), 
              len(info_df[info_df['B4'] == 1])]
role_rates = [(role_donated[i] / role_total[i] * 100) if role_total[i] > 0 else 0 
              for i in range(len(roles))]

x = np.arange(len(roles))
width = 0.6
bars = ax2.bar(x, role_rates, width, color=['#ff7f0e', '#2ca02c'], alpha=0.8)

ax2.set_ylabel('Donation Rate (%)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Role', fontsize=12, fontweight='bold')
ax2.set_title('Donation Rate by Role', fontsize=14, fontweight='bold', pad=20)
ax2.set_xticks(x)
ax2.set_xticklabels(roles)
ax2.set_ylim(0, max(role_rates) * 1.2 if role_rates else 100)
ax2.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, rate, total, donated) in enumerate(zip(bars, role_rates, role_total, role_donated)):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{rate:.1f}%\n({donated:,}/{total:,})',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig("donation_by_role.png", dpi=300, bbox_inches='tight')
print(f"✅ Graph 2 saved: donation_by_role.png")
plt.close(fig2)

# Figure 3: Dialog donation rate distribution
fig3, ax3 = plt.subplots(figsize=(10, 6))
has_donation_counts = dialog_stats['has_donation'].value_counts().sort_index()
labels_dialog = ['No Donation', 'Has Donation']
colors_dialog = ['#d62728', '#2ca02c']
explode_dialog = (0, 0.1)

wedges, texts, autotexts = ax3.pie(has_donation_counts.values, labels=labels_dialog, 
                                     autopct='%1.1f%%', colors=colors_dialog, 
                                     explode=explode_dialog, startangle=90,
                                     textprops={'fontsize': 12, 'fontweight': 'bold'})
ax3.set_title('Dialog Donation Rate', fontsize=16, fontweight='bold', pad=20)
ax3.text(0, -1.3, f'Total: {total_dialogs:,} dialogs', ha='center', fontsize=11,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig("donation_dialog_rate.png", dpi=300, bbox_inches='tight')
print(f"✅ Graph 3 saved: donation_dialog_rate.png")
plt.close(fig3)

# Figure 4: Donation amount distribution (if there are donations)
if len(donation_amounts) > 0:
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    ax4.hist(donation_amounts, bins=50, color='#2ca02c', alpha=0.7, edgecolor='black')
    ax4.axvline(donation_amounts.mean(), color='red', linestyle='--', linewidth=2, 
                label=f'Mean: ${donation_amounts.mean():.2f}')
    ax4.axvline(donation_amounts.median(), color='blue', linestyle='--', linewidth=2, 
                label=f'Median: ${donation_amounts.median():.2f}')
    ax4.set_xlabel('Donation Amount ($)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax4.set_title('Distribution of Donation Amounts', fontsize=14, fontweight='bold', pad=20)
    ax4.legend(fontsize=10)
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("donation_amount_distribution.png", dpi=300, bbox_inches='tight')
    print(f"✅ Graph 4 saved: donation_amount_distribution.png")
    plt.close(fig4)

# ========= 4. SUMMARY REPORT =========
print("\n" + "="*80)
print("SUMMARY REPORT")
print("="*80)

print(f"\nDataset Overview:")
print(f"   Total people in dataset: {total_people:,}")
print(f"   Total dialogs: {total_dialogs:,}")

print(f"\nDonation Statistics:")
print(f"   People who donated: {total_donated:,} ({donation_rate:.2f}%)")
print(f"   People who did not donate: {total_people - total_donated:,} ({(100 - donation_rate):.2f}%)")

if len(donation_amounts) > 0:
    print(f"\nDonation Amounts:")
    print(f"   Total amount donated: ${donation_amounts.sum():.2f}")
    print(f"   Average donation: ${donation_amounts.mean():.2f}")
    print(f"   Median donation: ${donation_amounts.median():.2f}")
    print(f"   Minimum donation: ${donation_amounts.min():.2f}")
    print(f"   Maximum donation: ${donation_amounts.max():.2f}")

print(f"\nDialog-level Statistics:")
print(f"   Dialogs with donations: {dialogs_with_donation:,} ({dialog_donation_rate:.2f}%)")
print(f"   Dialogs without donations: {total_dialogs - dialogs_with_donation:,} ({(100 - dialog_donation_rate):.2f}%)")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETED")
print("="*80)
print("\nCreated files:")
print("   - donation_dataset_stats.csv")
print("   - donation_overall_rate.png (Pie chart)")
print("   - donation_by_role.png (Bar chart)")
print("   - donation_dialog_rate.png (Pie chart)")
if len(donation_amounts) > 0:
    print("   - donation_amount_distribution.png (Histogram)")

