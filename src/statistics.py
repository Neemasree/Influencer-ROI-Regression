"""
src/statistics.py
=================
Descriptive statistics and normality testing.

Usage:
    from src.statistics import compute_descriptive_stats, run_normality_test
"""

import pandas as pd
import numpy as np
from scipy import stats


NUMERIC_COLS = [
    "Estimated_Reach",
    "Engagements",
    "Product_Sales",
    "Campaign_Duration_Days",
    "Engagement_Rate",
    "Campaign_Cost",
    "Revenue",
    "ROI",
]


def compute_descriptive_stats(df: pd.DataFrame,
                               cols: list = None) -> pd.DataFrame:
    """
    Compute mean, median, mode, std, variance, min, max, skewness, kurtosis
    for each numeric column.

    Returns a tidy DataFrame with one row per variable.
    """
    if cols is None:
        cols = [c for c in NUMERIC_COLS if c in df.columns]

    records = []
    for col in cols:
        s = df[col].dropna()
        try:
            mode_val = float(s.mode().iloc[0])
        except Exception:
            mode_val = float("nan")

        records.append({
            "Variable":  col,
            "Count":     len(s),
            "Mean":      s.mean(),
            "Median":    s.median(),
            "Mode":      mode_val,
            "Std_Dev":   s.std(),
            "Variance":  s.var(),
            "Min":       s.min(),
            "Max":       s.max(),
            "Skewness":  s.skew(),
            "Kurtosis":  s.kurt(),
        })

    return pd.DataFrame(records).set_index("Variable")


def run_normality_test(series: pd.Series,
                       sample_n: int = 5000,
                       random_state: int = 42) -> dict:
    """
    Run Shapiro-Wilk normality test on a random sample.
    (Full dataset is too large for Shapiro-Wilk; n=5,000 is standard practice.)

    Returns dict with statistic, p_value, and interpretation.
    """
    if len(series) > sample_n:
        sample = series.sample(n=sample_n, random_state=random_state)
    else:
        sample = series

    stat, p = stats.shapiro(sample)
    normal  = p >= 0.05
    return {
        "test":        "Shapiro-Wilk",
        "sample_n":    len(sample),
        "statistic":   round(stat, 4),
        "p_value":     round(p, 6),
        "is_normal":   normal,
        "conclusion":  "Normal (alpha=0.05)" if normal else "NOT normal (alpha=0.05)",
    }


def print_stats_summary(df: pd.DataFrame) -> None:
    """Print a formatted descriptive statistics table."""
    desc = compute_descriptive_stats(df)
    print("\nDESCRIPTIVE STATISTICS")
    print("=" * 80)
    print(desc.round(4).to_string())

    print("\nNORMALITY TEST — ROI")
    result = run_normality_test(df["ROI"])
    for k, v in result.items():
        print(f"  {k:12s}: {v}")
