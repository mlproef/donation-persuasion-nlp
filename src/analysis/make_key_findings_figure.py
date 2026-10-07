"""
Builds figures/key_findings.png, the headline figure shown in the README.

For each dialog it summarises the persuadee's LLM labels and compares the
donation rate across groups:
  1. highest interest level the persuadee reached in the dialog
  2. dominant (most frequent) sentiment of the persuadee's messages
  3. whether the persuadee refused at least once

Inputs:  data/processed/full_dialog_with_all_analysis.csv
         results/donation_dataset_stats.csv  (made by analyze_donation_dataset.py)
Outputs: figures/key_findings.png, results/key_findings.csv
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # make src/ importable
from paths import ALL_ANALYSIS, figure, result  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BAR = "#2a78d6"
TEXT = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"

df = pd.read_csv(ALL_ANALYSIS)
donations = pd.read_csv(result("donation_dataset_stats.csv"))[["B2", "has_donation"]]

target = df[df["B4"] == 1]
by_dialog = target.groupby("B2")
dialogs = pd.DataFrame({
    "max_interest": by_dialog["interest_label_ollama_v2"].max(),
    "dominant_sentiment": by_dialog["sentiment_ollama_v2"].agg(lambda s: s.value_counts().idxmax()),
    "any_refusal": by_dialog["interest_label_ollama_v2"].apply(lambda s: (s == 0).any()),
}).reset_index().merge(donations, on="B2", how="left")

overall = dialogs["has_donation"].mean() * 100

panels = [
    ("Highest interest reached", "max_interest",
     [(1.0, "Neutral"), (2.0, "Interested")]),
    ("Dominant sentiment", "dominant_sentiment",
     [("negative", "Negative"), ("neutral", "Neutral"), ("positive", "Positive")]),
    ("Persuadee refused at least once", "any_refusal",
     [(True, "Yes"), (False, "No")]),
]

rows = []
fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharey=True)
for ax, (title, col, levels) in zip(axes, panels):
    labels, rates, ns = [], [], []
    for value, label in levels:
        group = dialogs[dialogs[col] == value]
        rate = group["has_donation"].mean() * 100
        labels.append(label); rates.append(rate); ns.append(len(group))
        rows.append({"grouping": title, "group": label, "dialogs": len(group),
                     "donation_rate_pct": round(rate, 1)})
    bars = ax.bar(labels, rates, color=BAR, width=0.6, zorder=3)
    for bar, rate, n in zip(bars, rates, ns):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 2, f"{rate:.0f}%",
                ha="center", va="bottom", fontsize=12, fontweight="bold", color=TEXT, zorder=5,
                bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none"))
        ax.text(bar.get_x() + bar.get_width() / 2, 3, f"n={n}",
                ha="center", va="bottom", fontsize=9, color="white")
    ax.axhline(overall, color=MUTED, linestyle="--", linewidth=1, zorder=2)
    ax.set_title(title, fontsize=12, color=TEXT, pad=10)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", color=GRID, zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, length=0)
    ax.tick_params(axis="x", labelsize=11, labelcolor=TEXT)

axes[0].set_ylabel("Dialogs ending in a donation (%)", color=MUTED)
axes[0].text(-0.45, overall + 1.5, f"all dialogs: {overall:.0f}%", ha="left",
             va="bottom", fontsize=9, color=MUTED)
fig.suptitle("Donation rate by persuadee reaction (1,017 dialogs, labels from LLM)",
             fontsize=13, fontweight="bold", color=TEXT)
fig.tight_layout()
fig.savefig(figure("key_findings.png"), dpi=150, facecolor="white")
pd.DataFrame(rows).to_csv(result("key_findings.csv"), index=False)
print(pd.DataFrame(rows).to_string(index=False))
print(f"Saved {figure('key_findings.png')}")
