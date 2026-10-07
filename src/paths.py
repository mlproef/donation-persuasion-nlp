"""Central place for every file path used by the project.

All scripts resolve their inputs and outputs through this module, so they work
no matter which directory you launch them from.

    data/raw/        original PersuasionForGood tables (not committed, see data/README.md)
    data/interim/    raw LLM outputs produced by src/classification/*
    data/processed/  final merged dataset with all labels
    results/         summary tables and statistics (CSV / TXT)
    figures/         plots (PNG)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"

for _d in (INTERIM_DIR, PROCESSED_DIR, RESULTS_DIR, FIGURES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Raw dataset (PersuasionForGood)
FULL_DIALOG = RAW_DIR / "full_dialog.csv"  # one row per utterance: B2 dialog id, B4 role, Turn, Unit text
FULL_INFO = RAW_DIR / "full_info.csv"      # one row per participant: B2, B4, B6 donation amount

# LLM classification outputs
SENTIMENT_RESULTS = INTERIM_DIR / "test_batch_sentiment_results.csv"
INTEREST_RESULTS = INTERIM_DIR / "test_batch_interest_results.csv"
STRATEGY_RESULTS = INTERIM_DIR / "test_batch_results_single.csv"

# Final merged dataset
ALL_ANALYSIS = PROCESSED_DIR / "full_dialog_with_all_analysis.csv"


def result(name: str) -> Path:
    """Path for a summary table in results/."""
    return RESULTS_DIR / name


def figure(name: str) -> Path:
    """Path for a plot in figures/."""
    return FIGURES_DIR / name


def interim(name: str) -> Path:
    """Path for an intermediate file in data/interim/."""
    return INTERIM_DIR / name
