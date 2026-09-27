"""
src/process_data.py
===================
Data loading, cleaning, and feature engineering pipeline.

Usage (standalone):
    python src/process_data.py

Or import the main function:
    from src.process_data import build_processed_dataset
    df = build_processed_dataset()
"""

import os
import pandas as pd
import numpy as np

# ── Lookup tables (documented assumptions) ────────────────────────────────────
CPM = {
    "Instagram": 150,   # Cost-per-thousand impressions in INR
    "YouTube":   120,
    "TikTok":    100,
    "Twitter":    80,
}

AVG_UNIT_VALUE = {
    "Beauty":  1500,    # Average product unit value in INR per category
    "Tech":    5000,
    "Fashion": 1200,
    "Food":     300,
    "Fitness":  800,
    "Travel":  3000,
    "Gaming":  1000,
}

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE    = os.path.dirname(os.path.abspath(__file__))
_ROOT    = os.path.dirname(_HERE)
RAW_PATH = os.path.join(_ROOT, "data", "raw",
                        "influencer_marketing_roi_dataset.csv")
OUT_PATH = os.path.join(_ROOT, "data", "processed",
                        "influencer_roi_analysis_dataset.csv")


def load_raw(path: str = RAW_PATH) -> pd.DataFrame:
    """Load the raw Kaggle dataset without modification."""
    df = pd.read_csv(path)
    print(f"[load]    Raw dataset loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply data cleaning steps.
    Returns a cleaned copy; the input is never modified.
    """
    df = df.copy()
    initial = len(df)

    # 1. Strip whitespace from string columns
    for col in ["platform", "influencer_category", "campaign_type"]:
        df[col] = df[col].str.strip()

    # 2. Parse date columns
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"]   = pd.to_datetime(df["end_date"],   errors="coerce")

    # 3. Drop rows with any missing values
    before = len(df)
    df.dropna(inplace=True)
    print(f"[clean]   Missing-value rows removed : {before - len(df):,}")

    # 4. Drop exact duplicate rows
    before = len(df)
    df.drop_duplicates(inplace=True)
    print(f"[clean]   Duplicate rows removed     : {before - len(df):,}")

    # 5. Keep only recognised platforms and categories
    before = len(df)
    df = df[df["platform"].isin(CPM) & df["influencer_category"].isin(AVG_UNIT_VALUE)]
    print(f"[clean]   Invalid-value rows removed : {before - len(df):,}")

    # 6. Remove rows where estimated_reach = 0 (prevents division by zero)
    before = len(df)
    df = df[df["estimated_reach"] > 0]
    print(f"[clean]   Zero-reach rows removed    : {before - len(df):,}")

    # 7. Remove rows with any negative numeric values
    for col in ["engagements", "product_sales", "campaign_duration_days"]:
        before = len(df)
        df = df[df[col] >= 0]
        removed = before - len(df)
        if removed:
            print(f"[clean]   Negative {col}: {removed:,} removed")

    # 8. Validate campaign_duration_days against computed date range (±2 day tolerance)
    before = len(df)
    computed = (df["end_date"] - df["start_date"]).dt.days
    df = df[(computed - df["campaign_duration_days"]).abs() <= 2]
    print(f"[clean]   Duration-mismatch rows     : {before - len(df):,}")

    print(f"[clean]   Rows retained: {len(df):,} of {initial:,}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive the four engineered variables and extract Year / Month.

    Formulas
    --------
    Engagement_Rate = (Engagements / Estimated_Reach) * 100
    Campaign_Cost   = (Estimated_Reach * Platform_CPM) / 1000
    Revenue         = Product_Sales * Category_Avg_Unit_Value
    ROI             = (Revenue - Campaign_Cost) / Campaign_Cost
    """
    df = df.copy()

    # Engagement Rate (%)
    df["engagement_rate"] = (df["engagements"] / df["estimated_reach"]) * 100

    # Campaign Cost (INR) — CPM model
    df["campaign_cost"] = df.apply(
        lambda r: (r["estimated_reach"] * CPM[r["platform"]]) / 1000, axis=1
    )

    # Revenue (INR)
    df["revenue"] = df.apply(
        lambda r: r["product_sales"] * AVG_UNIT_VALUE[r["influencer_category"]], axis=1
    )

    # Guard: remove any rows where campaign_cost = 0 before ROI calculation
    df = df[df["campaign_cost"] > 0]

    # ROI (dimensionless ratio)
    df["roi"] = (df["revenue"] - df["campaign_cost"]) / df["campaign_cost"]

    # Outlier capping: clip ROI at 1st–99th percentile to remove extremes
    lo, hi = df["roi"].quantile(0.01), df["roi"].quantile(0.99)
    before = len(df)
    df = df[(df["roi"] >= lo) & (df["roi"] <= hi)]
    print(f"[engineer] ROI outliers removed (1st-99th pct): {before - len(df):,}")
    print(f"[engineer] ROI range after capping: {df['roi'].min():.4f} to {df['roi'].max():.4f}")

    # Temporal features
    df["year"]  = df["start_date"].dt.year
    df["month"] = df["start_date"].dt.month

    return df


def select_and_rename(df: pd.DataFrame) -> pd.DataFrame:
    """Select final columns, rename to title-case, sort, and round floats."""
    col_map = {
        "campaign_id":            "Campaign_ID",
        "platform":               "Platform",
        "influencer_category":    "Influencer_Category",
        "campaign_type":          "Campaign_Type",
        "start_date":             "Start_Date",
        "end_date":               "End_Date",
        "campaign_duration_days": "Campaign_Duration_Days",
        "estimated_reach":        "Estimated_Reach",
        "engagements":            "Engagements",
        "product_sales":          "Product_Sales",
        "engagement_rate":        "Engagement_Rate",
        "campaign_cost":          "Campaign_Cost",
        "revenue":                "Revenue",
        "roi":                    "ROI",
        "year":                   "Year",
        "month":                  "Month",
    }
    final = df[list(col_map.keys())].rename(columns=col_map).copy()
    final["Engagement_Rate"] = final["Engagement_Rate"].round(4)
    final["Campaign_Cost"]   = final["Campaign_Cost"].round(2)
    final["Revenue"]         = final["Revenue"].round(2)
    final["ROI"]             = final["ROI"].round(4)
    final.sort_values(["Start_Date", "Campaign_ID"], inplace=True)
    final.reset_index(drop=True, inplace=True)
    return final


def build_processed_dataset(raw_path: str = RAW_PATH,
                            out_path: str = OUT_PATH,
                            save: bool = True) -> pd.DataFrame:
    """
    Full pipeline: load -> clean -> engineer -> select -> save.
    Returns the final processed DataFrame.
    """
    print("=" * 60)
    print("DATA PROCESSING PIPELINE")
    print("=" * 60)

    raw   = load_raw(raw_path)
    clean_df = clean(raw)
    eng_df   = engineer_features(clean_df)
    final    = select_and_rename(eng_df)

    print(f"\n[done]    Final dataset: {final.shape[0]:,} rows x {final.shape[1]} columns")
    print(f"          Columns: {list(final.columns)}")

    if save:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        final.to_csv(out_path, index=False)
        print(f"[saved]   {out_path}")

    return final


if __name__ == "__main__":
    build_processed_dataset()
