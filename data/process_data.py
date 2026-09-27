"""
Data Processing Pipeline
========================
Influencer Marketing ROI — Predictive Statistical Analysis
Author : Neema Sree

Pipeline
--------
  data/raw/influencer_marketing_roi_dataset.csv   (150,000 rows, Kaggle source)
        ↓  Step 1 – Load
        ↓  Step 2 – Clean
        ↓  Step 3 – Feature Engineering
        ↓  Step 4 – Select & Rename Final Columns
  data/processed/influencer_roi_analysis_dataset.csv

Engineered Variables
--------------------
  Engagement_Rate  = (Engagements / Estimated_Reach) × 100
  Campaign_Cost    = (Estimated_Reach × CPM) / 1000
                     CPM by platform (₹): Instagram=150, YouTube=120, TikTok=100, Twitter=80
  Revenue          = Product_Sales × Avg_Unit_Value
                     Avg unit value by category (₹): Beauty=1500, Tech=5000, Fashion=1200,
                     Food=300, Fitness=800, Travel=3000, Gaming=1000
  ROI              = (Revenue − Campaign_Cost) / Campaign_Cost   [Target Variable]
"""

import pandas as pd
import numpy as np
import os

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
RAW_PATH   = os.path.join(BASE_DIR, "raw",       "influencer_marketing_roi_dataset.csv")
OUT_PATH   = os.path.join(BASE_DIR, "processed", "influencer_roi_analysis_dataset.csv")

# ── Lookup Tables ────────────────────────────────────────────────────────────
CPM = {
    "Instagram": 150,
    "YouTube":   120,
    "TikTok":    100,
    "Twitter":    80,
}

AVG_UNIT_VALUE = {
    "Beauty":  1500,
    "Tech":    5000,
    "Fashion": 1200,
    "Food":     300,
    "Fitness":  800,
    "Travel":  3000,
    "Gaming":  1000,
}

# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — LOAD RAW DATASET
# ════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("STEP 1 — Loading raw dataset")
print("=" * 60)

df = pd.read_csv(RAW_PATH)
print(f"  Rows loaded : {len(df):,}")
print(f"  Columns     : {list(df.columns)}")

# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — DATA CLEANING
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 2 — Data Cleaning")
print("=" * 60)

initial_rows = len(df)

# 2a. Standardise string columns (strip leading/trailing whitespace only)
#     Do NOT apply .title() — it corrupts mixed-case names like TikTok → Tiktok
#     and YouTube → Youtube, which would break the CPM lookup.
str_cols = ["platform", "influencer_category", "campaign_type"]
for col in str_cols:
    df[col] = df[col].str.strip()

# 2b. Parse date columns
df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
df["end_date"]   = pd.to_datetime(df["end_date"],   errors="coerce")

# 2c. Drop rows with missing values (any column)
df.dropna(inplace=True)
print(f"  Rows after dropping NaN      : {len(df):,}  (removed {initial_rows - len(df):,})")

# 2d. Drop exact duplicate rows
before_dedup = len(df)
df.drop_duplicates(inplace=True)
print(f"  Rows after dropping dupes    : {len(df):,}  (removed {before_dedup - len(df):,})")

# 2e. Keep only known platforms and categories
valid_platforms   = set(CPM.keys())
valid_categories  = set(AVG_UNIT_VALUE.keys())
before_filter = len(df)
df = df[df["platform"].isin(valid_platforms) & df["influencer_category"].isin(valid_categories)]
print(f"  Rows after invalid-value drop: {len(df):,}  (removed {before_filter - len(df):,})")

# 2f. Remove rows where estimated_reach = 0 (would cause division by zero)
before_reach = len(df)
df = df[df["estimated_reach"] > 0]
print(f"  Rows after zero-reach drop   : {len(df):,}  (removed {before_reach - len(df):,})")

# 2g. Remove rows with negative numeric values
numeric_cols = ["engagements", "estimated_reach", "product_sales", "campaign_duration_days"]
for col in numeric_cols:
    before = len(df)
    df = df[df[col] >= 0]
    removed = before - len(df)
    if removed:
        print(f"  Removed {removed:,} rows with negative {col}")

# 2h. Verify campaign_duration_days is consistent with date range (tolerance ±2 days)
df["computed_duration"] = (df["end_date"] - df["start_date"]).dt.days
inconsistent = (df["computed_duration"] - df["campaign_duration_days"]).abs() > 2
removed_inconsistent = inconsistent.sum()
df = df[~inconsistent]
df.drop(columns=["computed_duration"], inplace=True)
print(f"  Rows after duration check    : {len(df):,}  (removed {removed_inconsistent:,})")

print(f"\n  ✔ Clean dataset: {len(df):,} rows retained from {initial_rows:,} original rows")

# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — FEATURE ENGINEERING
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 3 — Feature Engineering")
print("=" * 60)

# 3a. Engagement_Rate (%)
df["engagement_rate"] = (df["engagements"] / df["estimated_reach"]) * 100
print("  ✔ engagement_rate = (engagements / estimated_reach) × 100")

# 3b. Campaign_Cost (₹)  — CPM model: cost = reach × CPM / 1000
df["campaign_cost"] = df.apply(
    lambda r: (r["estimated_reach"] * CPM[r["platform"]]) / 1000,
    axis=1
)
print("  ✔ campaign_cost   = (estimated_reach × Platform_CPM) / 1000")
print(f"     CPMs used → Instagram: ₹150 | YouTube: ₹120 | TikTok: ₹100 | Twitter: ₹80")

# 3c. Revenue (₹) — product_sales × avg unit value for the category
df["revenue"] = df.apply(
    lambda r: r["product_sales"] * AVG_UNIT_VALUE[r["influencer_category"]],
    axis=1
)
print("  ✔ revenue         = product_sales × Category_Avg_Unit_Value")
print(f"     Values used → Beauty:₹1500 | Tech:₹5000 | Fashion:₹1200 | Food:₹300")
print(f"                    Fitness:₹800 | Travel:₹3000 | Gaming:₹1000")

# 3d. ROI — target variable
#     Remove rows where campaign_cost = 0 to avoid division by zero
before_roi = len(df)
df = df[df["campaign_cost"] > 0]
print(f"  Removed {before_roi - len(df):,} rows with zero campaign cost before ROI calculation")

df["roi"] = (df["revenue"] - df["campaign_cost"]) / df["campaign_cost"]
print("  ✔ roi             = (revenue − campaign_cost) / campaign_cost")

# 3e. Cap ROI at the 99th percentile to remove extreme outliers
#     These outliers arise from very low campaign costs combined with high product sales.
#     Capping preserves the distribution shape while making regression numerically stable.
roi_cap = df["roi"].quantile(0.99)
roi_floor = df["roi"].quantile(0.01)
before_cap = len(df)
df = df[(df["roi"] <= roi_cap) & (df["roi"] >= roi_floor)]
print(f"  ✔ roi outlier cap : 1st pct={roi_floor:.2f}, 99th pct={roi_cap:.2f}  → removed {before_cap - len(df):,} extreme rows")

# 3g. Extract Year and Month from start_date
df["year"]  = df["start_date"].dt.year
df["month"] = df["start_date"].dt.month

print(f"\n  ✔ Feature engineering complete. ROI range: {df['roi'].min():.2f} → {df['roi'].max():.2f}")

# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — SELECT & RENAME FINAL COLUMNS
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 4 — Selecting Final Columns")
print("=" * 60)

final_cols = [
    "campaign_id",
    "platform",
    "influencer_category",
    "campaign_type",
    "start_date",
    "end_date",
    "campaign_duration_days",
    "estimated_reach",
    "engagements",
    "product_sales",
    "engagement_rate",
    "campaign_cost",
    "revenue",
    "roi",
    "year",
    "month",
]

df_final = df[final_cols].copy()

# Rename to clean, title-case column names for the processed file
rename_map = {
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
df_final.rename(columns=rename_map, inplace=True)

# Round engineered floats to 4 decimal places
df_final["Engagement_Rate"] = df_final["Engagement_Rate"].round(4)
df_final["Campaign_Cost"]   = df_final["Campaign_Cost"].round(2)
df_final["Revenue"]         = df_final["Revenue"].round(2)
df_final["ROI"]             = df_final["ROI"].round(4)

# Sort by Start_Date then Campaign_ID
df_final.sort_values(["Start_Date", "Campaign_ID"], inplace=True)
df_final.reset_index(drop=True, inplace=True)

print(f"  Final columns : {list(df_final.columns)}")
print(f"  Final shape   : {df_final.shape}")

# ════════════════════════════════════════════════════════════════════════════
# STEP 5 — SAVE PROCESSED DATASET
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 5 — Saving Processed Dataset")
print("=" * 60)

df_final.to_csv(OUT_PATH, index=False)
print(f"  ✔ Saved to: {OUT_PATH}")

# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PIPELINE SUMMARY")
print("=" * 60)
print(f"  Source dataset       : data/raw/influencer_marketing_roi_dataset.csv")
print(f"  Raw rows             : {initial_rows:,}")
print(f"  Final processed rows : {len(df_final):,}")
print(f"  Final columns        : {len(df_final.columns)}")
print(f"  Output               : data/processed/influencer_roi_analysis_dataset.csv")
print()
print("  Numeric summary (engineered columns):")
print(df_final[["Engagement_Rate", "Campaign_Cost", "Revenue", "ROI"]].describe().round(4).to_string())
print("=" * 60)
