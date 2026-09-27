"""
src/visualization.py
====================
All chart generation for the project.
Saves figures to outputs/figures/.

Usage:
    from src.visualization import generate_all_charts
    generate_all_charts(df, model)
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

_HERE    = os.path.dirname(os.path.abspath(__file__))
_ROOT    = os.path.dirname(_HERE)
FIG_DIR  = os.path.join(_ROOT, "outputs", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
PALETTE  = ["#4C72B0", "#DD8452", "#55A868", "#C44E52",
            "#8172B2", "#937860", "#DA8BC3"]


def _save(name: str) -> None:
    path = os.path.join(FIG_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [fig] {name}")


# ── EDA Charts ────────────────────────────────────────────────────────────────

def plot_roi_distribution(df: pd.DataFrame) -> None:
    """01 — ROI Distribution (histogram + CDF)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("ROI Distribution — 147,000 Campaigns", fontsize=14, fontweight="bold")
    roi_clip = df["ROI"].clip(upper=df["ROI"].quantile(0.95))
    axes[0].hist(roi_clip, bins=60, color=PALETTE[0], edgecolor="white", linewidth=0.5)
    axes[0].set(title="Histogram of ROI", xlabel="ROI", ylabel="Frequency")
    axes[1].plot(sorted(roi_clip), np.linspace(0, 1, len(roi_clip)), color=PALETTE[0])
    axes[1].set(title="Cumulative Distribution of ROI",
                xlabel="ROI", ylabel="Cumulative Proportion")
    plt.tight_layout()
    _save("01_roi_distribution.png")


def plot_engagement_rate_distribution(df: pd.DataFrame) -> None:
    """02 — Engagement Rate Distribution."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Engagement Rate Distribution", fontsize=14, fontweight="bold")
    er_clip = df["Engagement_Rate"].clip(upper=df["Engagement_Rate"].quantile(0.95))
    axes[0].hist(er_clip, bins=60, color=PALETTE[1], edgecolor="white", linewidth=0.5)
    axes[0].set(title="Histogram of Engagement Rate",
                xlabel="Engagement Rate (%)", ylabel="Frequency")
    axes[1].boxplot(er_clip, vert=False, patch_artist=True,
                    boxprops=dict(facecolor=PALETTE[1], alpha=0.7))
    axes[1].set(title="Boxplot of Engagement Rate",
                xlabel="Engagement Rate (%)")
    plt.tight_layout()
    _save("02_engagement_rate_distribution.png")


def plot_campaign_cost_distribution(df: pd.DataFrame) -> None:
    """03 — Campaign Cost Distribution."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Campaign Cost Distribution", fontsize=14, fontweight="bold")
    axes[0].hist(df["Campaign_Cost"], bins=60, color=PALETTE[2],
                 edgecolor="white", linewidth=0.5)
    axes[0].set(title="Histogram of Campaign Cost",
                xlabel="Campaign Cost (INR)", ylabel="Frequency")
    axes[0].xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
    axes[1].boxplot(df["Campaign_Cost"], vert=False, patch_artist=True,
                    boxprops=dict(facecolor=PALETTE[2], alpha=0.7))
    axes[1].set(title="Boxplot of Campaign Cost", xlabel="Campaign Cost (INR)")
    axes[1].xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
    plt.tight_layout()
    _save("03_campaign_cost_distribution.png")


def plot_product_sales_distribution(df: pd.DataFrame) -> None:
    """04 — Product Sales Distribution."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Product Sales Distribution", fontsize=14, fontweight="bold")
    axes[0].hist(df["Product_Sales"], bins=60, color=PALETTE[3],
                 edgecolor="white", linewidth=0.5)
    axes[0].set(title="Histogram of Product Sales",
                xlabel="Units Sold", ylabel="Frequency")
    axes[1].boxplot(df["Product_Sales"], vert=False, patch_artist=True,
                    boxprops=dict(facecolor=PALETTE[3], alpha=0.7))
    axes[1].set(title="Boxplot of Product Sales", xlabel="Units Sold")
    plt.tight_layout()
    _save("04_product_sales_distribution.png")


def plot_cost_vs_revenue(df: pd.DataFrame) -> None:
    """05 — Campaign Cost vs Revenue scatter."""
    sample = df.sample(n=5000, random_state=42)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(sample["Campaign_Cost"], sample["Revenue"],
               alpha=0.25, s=12, color=PALETTE[0])
    ax.set(title="Campaign Cost vs Revenue",
           xlabel="Campaign Cost (INR)", ylabel="Revenue (INR)")
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    plt.tight_layout()
    _save("05_cost_vs_revenue.png")


def plot_engagement_vs_roi(df: pd.DataFrame) -> None:
    """06 — Engagement Rate vs ROI scatter."""
    sample = df.sample(n=5000, random_state=42)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(sample["Engagement_Rate"].clip(upper=100),
               sample["ROI"].clip(upper=500),
               alpha=0.25, s=12, color=PALETTE[1])
    ax.set(title="Engagement Rate vs ROI",
           xlabel="Engagement Rate (%)", ylabel="ROI")
    plt.tight_layout()
    _save("06_engagement_vs_roi.png")


def plot_roi_by_platform(df: pd.DataFrame) -> None:
    """07 — ROI by Platform (boxplot + bar)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("ROI by Platform", fontsize=14, fontweight="bold")
    plat_counts = df["Platform"].value_counts()
    axes[0].bar(plat_counts.index, plat_counts.values, color=PALETTE[:4])
    axes[0].set(title="Campaign Count by Platform",
                xlabel="Platform", ylabel="Count")
    for i, v in enumerate(plat_counts.values):
        axes[0].text(i, v + 200, f"{v:,}", ha="center", fontsize=9)
    df.boxplot(column="ROI", by="Platform", ax=axes[1],
               patch_artist=True, showfliers=False)
    axes[1].set(title="ROI Distribution by Platform",
                xlabel="Platform", ylabel="ROI")
    plt.suptitle("")
    plt.tight_layout()
    _save("07_roi_by_platform.png")


def plot_roi_by_category(df: pd.DataFrame) -> None:
    """08 — ROI by Influencer Category."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("ROI by Influencer Category", fontsize=14, fontweight="bold")
    cat_roi = (df.groupby("Influencer_Category")["ROI"]
               .mean().sort_values(ascending=False))
    axes[0].barh(cat_roi.index, cat_roi.values, color=PALETTE[:7])
    axes[0].set(title="Average ROI by Category", xlabel="Mean ROI")
    for i, v in enumerate(cat_roi.values):
        axes[0].text(v + 0.5, i, f"{v:.1f}", va="center", fontsize=9)
    df.boxplot(column="ROI", by="Influencer_Category",
               ax=axes[1], patch_artist=True, showfliers=False, vert=False)
    axes[1].set(title="ROI Spread by Category", xlabel="ROI")
    plt.suptitle("")
    plt.tight_layout()
    _save("08_roi_by_category.png")


def plot_roi_by_campaign_type(df: pd.DataFrame) -> None:
    """09 — ROI by Campaign Type."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("ROI by Campaign Type", fontsize=14, fontweight="bold")
    ct_roi = (df.groupby("Campaign_Type")["ROI"]
              .mean().sort_values(ascending=False))
    axes[0].bar(ct_roi.index, ct_roi.values, color=PALETTE[:5])
    axes[0].set(title="Average ROI by Campaign Type",
                xlabel="Campaign Type", ylabel="Mean ROI")
    axes[0].tick_params(axis="x", rotation=15)
    monthly = df.groupby("Month")["ROI"].mean()
    axes[1].plot(monthly.index, monthly.values, marker="o", color=PALETTE[2])
    axes[1].set(title="Average ROI by Month",
                xlabel="Month", ylabel="Mean ROI")
    axes[1].set_xticks(range(1, 13))
    axes[1].set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    plt.tight_layout()
    _save("09_roi_by_campaign_type.png")


def plot_correlation_heatmap(df: pd.DataFrame,
                              num_cols: list = None) -> None:
    """10 — Pearson Correlation Heatmap."""
    if num_cols is None:
        num_cols = ["Estimated_Reach", "Engagements", "Product_Sales",
                    "Campaign_Duration_Days", "Engagement_Rate",
                    "Campaign_Cost", "Revenue", "ROI"]
    corr = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(11, 9))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
                cmap="coolwarm", center=0, linewidths=0.5, ax=ax)
    ax.set_title("Pearson Correlation Heatmap", fontsize=14, fontweight="bold")
    plt.tight_layout()
    _save("10_correlation_heatmap.png")


# ── Regression Charts ─────────────────────────────────────────────────────────

def plot_roi_correlation_bar(df: pd.DataFrame,
                              num_cols: list = None) -> None:
    """11 — Feature Correlation with ROI bar chart."""
    if num_cols is None:
        num_cols = ["Estimated_Reach", "Engagements", "Product_Sales",
                    "Campaign_Duration_Days", "Engagement_Rate",
                    "Campaign_Cost", "Revenue", "ROI"]
    corr = df[num_cols].corr()
    roi_corr = corr["ROI"].drop("ROI").sort_values(ascending=False)
    colors = [PALETTE[0] if v > 0 else PALETTE[3] for v in roi_corr.values]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(roi_corr.index, roi_corr.values, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set(title="Feature Correlation with ROI", xlabel="Pearson r")
    for i, v in enumerate(roi_corr.values):
        ax.text(v + 0.002 if v >= 0 else v - 0.002, i,
                f"{v:.3f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=9)
    plt.tight_layout()
    _save("11_roi_correlation_bar.png")


def plot_coefficients(model) -> None:
    """12 — Regression Coefficients with 95% CI."""
    features = ["Engagement_Rate", "Campaign_Cost",
                "Product_Sales", "Campaign_Duration_Days"]
    coefs = model.params
    conf  = model.conf_int()
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, f in enumerate(features):
        ax.plot([conf.loc[f, 0], conf.loc[f, 1]], [i, i],
                color=PALETTE[0], linewidth=2)
        color = PALETTE[0] if coefs[f] > 0 else PALETTE[3]
        ax.scatter(coefs[f], i, color=color, s=80, zorder=5)
        ax.text(coefs[f], i + 0.15, f"{coefs[f]:.4f}",
                ha="center", fontsize=9)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features)
    ax.set(title="OLS Coefficients with 95% Confidence Intervals",
           xlabel="Coefficient Value")
    plt.tight_layout()
    _save("12_coefficients.png")


def plot_residual_analysis(model) -> None:
    """13 — Q-Q plot, Residuals vs Fitted, Residual histogram."""
    residuals = model.resid
    y_pred    = model.fittedvalues
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Residual Analysis", fontsize=14, fontweight="bold")

    (osm, osr), (slope, intercept, _) = stats.probplot(residuals, dist="norm")
    axes[0].plot(osm, osr, "o", alpha=0.3, ms=3, color=PALETTE[0])
    axes[0].plot(osm, slope * np.array(osm) + intercept,
                 color=PALETTE[3], linewidth=1.5)
    axes[0].set(title="Q-Q Plot", xlabel="Theoretical Quantiles",
                ylabel="Sample Quantiles")

    axes[1].scatter(y_pred, residuals, alpha=0.15, s=8, color=PALETTE[0])
    axes[1].axhline(0, color=PALETTE[3], linewidth=1.5, linestyle="--")
    axes[1].set(title="Residuals vs Fitted",
                xlabel="Fitted Values", ylabel="Residuals")

    axes[2].hist(residuals, bins=60, color=PALETTE[0], edgecolor="white")
    axes[2].set(title="Residual Distribution",
                xlabel="Residual", ylabel="Frequency")

    plt.tight_layout()
    _save("13_residual_analysis.png")


def plot_actual_vs_predicted(y_actual, y_pred) -> None:
    """14 — Actual vs Predicted ROI scatter."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_actual, y_pred, alpha=0.15, s=8, color=PALETTE[0])
    lims = [min(float(y_actual.min()), float(y_pred.min())),
            max(float(y_actual.max()), float(y_pred.max()))]
    ax.plot(lims, lims, color=PALETTE[3], linewidth=1.5,
            linestyle="--", label="Perfect fit")
    ax.set(title="Actual vs Predicted ROI", xlabel="Actual ROI",
           ylabel="Predicted ROI")
    ax.legend()
    plt.tight_layout()
    _save("14_actual_vs_predicted.png")


def plot_error_distribution(y_actual, y_pred, mae: float, rmse: float) -> None:
    """15 — Prediction Error Distribution."""
    errors = y_actual - y_pred
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Model Evaluation", fontsize=14, fontweight="bold")

    axes[0].hist(errors, bins=60, color=PALETTE[0], edgecolor="white")
    axes[0].axvline(0, color=PALETTE[3], linewidth=1.5, linestyle="--")
    axes[0].set(title=f"Error Distribution  (MAE={mae:.2f}, RMSE={rmse:.2f})",
                xlabel="Actual - Predicted", ylabel="Frequency")

    metrics = {"R2": float(1 - (errors**2).sum() / ((y_actual - y_actual.mean())**2).sum())}
    axes[1].bar(["MAE", "RMSE"], [mae, rmse], color=PALETTE[:2])
    axes[1].set(title="Error Metrics", ylabel="Value")
    for i, (label, val) in enumerate(zip(["MAE", "RMSE"], [mae, rmse])):
        axes[1].text(i, val + 0.5, f"{val:.2f}", ha="center",
                     fontsize=11, fontweight="bold")
    plt.tight_layout()
    _save("15_error_distribution.png")


def plot_predictions(pred_df: pd.DataFrame) -> None:
    """16 — Predicted ROI bar chart for new campaigns."""
    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(pred_df["Campaign"], pred_df["Predicted_ROI"],
                  color=PALETTE[:len(pred_df)], zorder=3)
    ax.errorbar(
        pred_df["Campaign"], pred_df["Predicted_ROI"],
        yerr=[pred_df["Predicted_ROI"] - pred_df["CI_Lower_95"],
              pred_df["CI_Upper_95"]   - pred_df["Predicted_ROI"]],
        fmt="none", color="black", capsize=5, linewidth=1.5, zorder=4
    )
    ax.set(title="Predicted ROI for New Campaigns (95% Prediction Interval)",
           ylabel="Predicted ROI")
    ax.tick_params(axis="x", rotation=18)
    for bar, val in zip(bars, pred_df["Predicted_ROI"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{val:.1f}", ha="center", fontsize=9)
    ax.grid(axis="y", alpha=0.4)
    plt.tight_layout()
    _save("16_predictions.png")


# ── Master function ────────────────────────────────────────────────────────────

def generate_eda_charts(df: pd.DataFrame) -> None:
    """Generate all 10 EDA charts."""
    print("\n[viz] Generating EDA charts...")
    plot_roi_distribution(df)
    plot_engagement_rate_distribution(df)
    plot_campaign_cost_distribution(df)
    plot_product_sales_distribution(df)
    plot_cost_vs_revenue(df)
    plot_engagement_vs_roi(df)
    plot_roi_by_platform(df)
    plot_roi_by_category(df)
    plot_roi_by_campaign_type(df)
    plot_correlation_heatmap(df)
    print("[viz] EDA charts done (01-10).")


def generate_regression_charts(df: pd.DataFrame, model,
                                y_actual, y_pred,
                                mae: float, rmse: float,
                                pred_df: pd.DataFrame) -> None:
    """Generate all regression / evaluation charts."""
    print("\n[viz] Generating regression charts...")
    plot_roi_correlation_bar(df)
    plot_coefficients(model)
    plot_residual_analysis(model)
    plot_actual_vs_predicted(y_actual, y_pred)
    plot_error_distribution(y_actual, y_pred, mae, rmse)
    plot_predictions(pred_df)
    print("[viz] Regression charts done (11-16).")
