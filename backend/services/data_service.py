"""
backend/services/data_service.py
=================================
All dataset aggregation logic for the API.

The processed DataFrame is loaded ONCE at app startup and passed in.
No CSV is read on a per-request basis.
"""

import math
import pandas as pd
import numpy as np


# ── helpers ───────────────────────────────────────────────────────────────────

def _safe(val):
    """Convert numpy/pandas scalars to plain Python types safe for JSON."""
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        if math.isnan(val) or math.isinf(val):
            return None
        return round(float(val), 4)
    return val


def _row_to_dict(row) -> dict:
    return {k: _safe(v) for k, v in row.items()}


# ── dashboard ─────────────────────────────────────────────────────────────────

def get_dashboard_stats(df: pd.DataFrame) -> dict:
    return {
        "total_campaigns":        int(len(df)),
        "average_roi":            round(float(df["ROI"].mean()), 4),
        "median_roi":             round(float(df["ROI"].median()), 4),
        "average_engagement_rate":round(float(df["Engagement_Rate"].mean()), 4),
        "average_campaign_cost":  round(float(df["Campaign_Cost"].mean()), 2),
        "total_product_sales":    int(df["Product_Sales"].sum()),
        "total_revenue":          round(float(df["Revenue"].sum()), 2),
        "platforms":              sorted(df["Platform"].unique().tolist()),
        "categories":             sorted(df["Influencer_Category"].unique().tolist()),
    }


# ── platform analytics ────────────────────────────────────────────────────────

def get_platform_analytics(df: pd.DataFrame) -> list:
    grp = df.groupby("Platform").agg(
        campaign_count        =("ROI", "count"),
        average_roi           =("ROI", "mean"),
        median_roi            =("ROI", "median"),
        average_engagement_rate=("Engagement_Rate", "mean"),
        average_campaign_cost =("Campaign_Cost", "mean"),
        total_product_sales   =("Product_Sales", "sum"),
        average_revenue       =("Revenue", "mean"),
    ).reset_index()

    result = []
    for _, row in grp.iterrows():
        result.append({
            "platform":               str(row["Platform"]),
            "campaign_count":         int(row["campaign_count"]),
            "average_roi":            round(float(row["average_roi"]), 4),
            "median_roi":             round(float(row["median_roi"]), 4),
            "average_engagement_rate":round(float(row["average_engagement_rate"]), 4),
            "average_campaign_cost":  round(float(row["average_campaign_cost"]), 2),
            "total_product_sales":    int(row["total_product_sales"]),
            "average_revenue":        round(float(row["average_revenue"]), 2),
        })
    return sorted(result, key=lambda x: x["average_roi"], reverse=True)


# ── category analytics ────────────────────────────────────────────────────────

def get_category_analytics(df: pd.DataFrame) -> list:
    grp = df.groupby("Influencer_Category").agg(
        campaign_count        =("ROI", "count"),
        average_roi           =("ROI", "mean"),
        median_roi            =("ROI", "median"),
        average_engagement_rate=("Engagement_Rate", "mean"),
        average_campaign_cost =("Campaign_Cost", "mean"),
        total_product_sales   =("Product_Sales", "sum"),
    ).reset_index()

    result = []
    for _, row in grp.iterrows():
        result.append({
            "category":               str(row["Influencer_Category"]),
            "campaign_count":         int(row["campaign_count"]),
            "average_roi":            round(float(row["average_roi"]), 4),
            "median_roi":             round(float(row["median_roi"]), 4),
            "average_engagement_rate":round(float(row["average_engagement_rate"]), 4),
            "average_campaign_cost":  round(float(row["average_campaign_cost"]), 2),
            "total_product_sales":    int(row["total_product_sales"]),
        })
    return sorted(result, key=lambda x: x["average_roi"], reverse=True)


# ── campaign type analytics ───────────────────────────────────────────────────

def get_campaign_type_analytics(df: pd.DataFrame) -> list:
    grp = df.groupby("Campaign_Type").agg(
        campaign_count        =("ROI", "count"),
        average_roi           =("ROI", "mean"),
        median_roi            =("ROI", "median"),
        average_engagement_rate=("Engagement_Rate", "mean"),
        average_campaign_cost =("Campaign_Cost", "mean"),
        total_product_sales   =("Product_Sales", "sum"),
    ).reset_index()

    result = []
    for _, row in grp.iterrows():
        result.append({
            "campaign_type":          str(row["Campaign_Type"]),
            "campaign_count":         int(row["campaign_count"]),
            "average_roi":            round(float(row["average_roi"]), 4),
            "median_roi":             round(float(row["median_roi"]), 4),
            "average_engagement_rate":round(float(row["average_engagement_rate"]), 4),
            "average_campaign_cost":  round(float(row["average_campaign_cost"]), 2),
            "total_product_sales":    int(row["total_product_sales"]),
        })
    return sorted(result, key=lambda x: x["average_roi"], reverse=True)


# ── monthly trend ─────────────────────────────────────────────────────────────

def get_monthly_analytics(df: pd.DataFrame) -> list:
    grp = df.groupby("Month").agg(
        campaign_count  =("ROI", "count"),
        average_roi     =("ROI", "mean"),
        median_roi      =("ROI", "median"),
        average_engagement_rate=("Engagement_Rate", "mean"),
        total_product_sales   =("Product_Sales", "sum"),
    ).reset_index()

    month_names = {
        1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun",
        7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec",
    }
    result = []
    for _, row in grp.iterrows():
        m = int(row["Month"])
        result.append({
            "month":           m,
            "month_name":      month_names[m],
            "campaign_count":  int(row["campaign_count"]),
            "average_roi":     round(float(row["average_roi"]), 4),
            "median_roi":      round(float(row["median_roi"]), 4),
            "average_engagement_rate": round(float(row["average_engagement_rate"]), 4),
            "total_product_sales": int(row["total_product_sales"]),
        })
    return sorted(result, key=lambda x: x["month"])


# ── correlation ───────────────────────────────────────────────────────────────

def get_correlation_data(df: pd.DataFrame) -> dict:
    cols = ["ROI", "Engagement_Rate", "Campaign_Cost",
            "Product_Sales", "Campaign_Duration_Days", "Estimated_Reach", "Revenue"]
    corr = df[cols].corr().round(4)

    matrix = []
    for row_var in cols:
        for col_var in cols:
            matrix.append({
                "x": row_var,
                "y": col_var,
                "value": round(float(corr.loc[row_var, col_var]), 4),
            })

    roi_correlations = {
        col: round(float(corr.loc["ROI", col]), 4)
        for col in cols if col != "ROI"
    }

    return {
        "variables": cols,
        "matrix":    matrix,
        "roi_correlations": roi_correlations,
    }


# ── scatter data (sampled for performance) ────────────────────────────────────

def get_scatter_data(df: pd.DataFrame, x_col: str, y_col: str = "ROI",
                     sample_n: int = 3000) -> list:
    """Return a random sample for scatter charts — never send 147k points to browser."""
    valid_cols = list(df.columns)
    if x_col not in valid_cols or y_col not in valid_cols:
        return []
    # Use a deterministic but column-specific seed so each chart shows different points
    seed = abs(hash(x_col)) % (2**31)
    sample = df[[x_col, y_col]].sample(
        n=min(sample_n, len(df)), random_state=seed
    )
    # ROI is already capped at 1st-99th percentile in the dataset; no additional clipping needed
    # Use to_dict for performance — iterrows() on large frames is O(n) Python overhead
    return [
        {"x": _safe(row[x_col]), "y": _safe(row[y_col])}
        for row in sample.to_dict("records")
    ]


# ── ROI distribution histogram bins ──────────────────────────────────────────

def get_roi_histogram(df: pd.DataFrame, bins: int = 50) -> list:
    # ROI is already capped at 1st-99th percentile during data processing
    # Use 99th percentile here to be consistent with that cap
    clipped = df["ROI"].clip(upper=float(df["ROI"].quantile(0.99)))
    counts, edges = np.histogram(clipped, bins=bins)
    result = []
    for i in range(len(counts)):
        result.append({
            "bin_start": round(float(edges[i]), 2),
            "bin_end":   round(float(edges[i + 1]), 2),
            "count":     int(counts[i]),
            "label":     f"{edges[i]:.0f}–{edges[i+1]:.0f}",
        })
    return result


# ── paginated campaign table ──────────────────────────────────────────────────

def get_campaigns(df: pd.DataFrame,
                  platform: str = None,
                  category: str = None,
                  campaign_type: str = None,
                  year: int = None,
                  month: int = None,
                  search: str = None,
                  sort_by: str = "ROI",
                  sort_dir: str = "desc",
                  page: int = 1,
                  limit: int = 25) -> dict:

    limit = min(limit, 100)
    # Build a boolean mask instead of copying the full 147k-row frame on every request
    mask = pd.Series(True, index=df.index)
    if platform:
        mask &= df["Platform"] == platform
    if category:
        mask &= df["Influencer_Category"] == category
    if campaign_type:
        mask &= df["Campaign_Type"] == campaign_type
    if year:
        mask &= df["Year"] == int(year)
    if month:
        mask &= df["Month"] == int(month)
    if search:
        s = search.lower()
        mask &= (
            df["Campaign_ID"].str.lower().str.contains(s, na=False) |
            df["Platform"].str.lower().str.contains(s, na=False) |
            df["Influencer_Category"].str.lower().str.contains(s, na=False) |
            df["Campaign_Type"].str.lower().str.contains(s, na=False)
        )
    filtered = df[mask]

    # sort
    valid_sort = list(df.columns)
    if sort_by not in valid_sort:
        sort_by = "ROI"
    ascending = sort_dir.lower() != "desc"
    filtered = filtered.sort_values(sort_by, ascending=ascending)

    total = len(filtered)
    total_pages = max(1, math.ceil(total / limit))
    page = max(1, min(page, total_pages))
    start = (page - 1) * limit
    end = start + limit

    display_cols = [
        "Campaign_ID", "Platform", "Influencer_Category", "Campaign_Type",
        "Campaign_Duration_Days", "Estimated_Reach", "Engagements",
        "Product_Sales", "Engagement_Rate", "Campaign_Cost", "Revenue", "ROI",
        "Year", "Month",
    ]
    page_df = filtered[display_cols].iloc[start:end]

    rows = [_row_to_dict(row) for _, row in page_df.iterrows()]

    return {
        "data":        rows,
        "total":       total,
        "page":        page,
        "limit":       limit,
        "total_pages": total_pages,
    }


# ── filter values ─────────────────────────────────────────────────────────────

def get_filter_values(df: pd.DataFrame) -> dict:
    return {
        "platforms":       sorted(df["Platform"].unique().tolist()),
        "categories":      sorted(df["Influencer_Category"].unique().tolist()),
        "campaign_types":  sorted(df["Campaign_Type"].unique().tolist()),
        "years":           sorted([int(y) for y in df["Year"].unique().tolist()]),
        "months":          sorted([int(m) for m in df["Month"].unique().tolist()]),
    }
