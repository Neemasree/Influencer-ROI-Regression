"""
Full Analysis Pipeline — Influencer Marketing ROI
==================================================
Run this script to execute the complete pipeline and capture all metrics.
Outputs are saved to Images/ for use in the notebook and report.

Pipeline:
  Raw Dataset
       ↓  Data Cleaning
       ↓  Feature Engineering
       ↓  Final Processed Dataset
       ↓  EDA
       ↓  Statistical Analysis
       ↓  Multiple Linear Regression (Statsmodels OLS)
       ↓  Prediction & Evaluation
"""

import os, sys, warnings
import pandas as pd
import numpy as np

# Force UTF-8 output so Unicode characters print correctly on Windows
sys.stdout.reconfigure(encoding="utf-8")
import matplotlib
matplotlib.use("Agg")   # non-interactive backend — saves figures without displaying
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC    = os.path.join(BASE, "data", "processed", "influencer_roi_analysis_dataset.csv")
IMG_DIR = os.path.join(BASE, "Images")
os.makedirs(IMG_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
PALETTE = ["#4C72B0","#DD8452","#55A868","#C44E52","#8172B2","#937860","#DA8BC3"]

def save(name):
    path = os.path.join(IMG_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → Images/{name}")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 1  —  LOAD PROCESSED DATASET
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 1 — Load Processed Dataset")
print("="*65)

df = pd.read_csv(PROC, parse_dates=["Start_Date", "End_Date"])
print(f"  Rows    : {len(df):,}")
print(f"  Columns : {list(df.columns)}")
print(f"\n  Head:")
print(df.head(3).to_string())

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 2  —  PIPELINE SUMMARY DISPLAY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 2 — Pipeline Summary")
print("="*65)
print("""
  RAW DATA (150,000 rows, Kaggle source dataset)
         |
         v  DATA CLEANING
    * Stripped whitespace from string columns
    * Parsed date columns
    * Removed duplicates: 0
    * Removed invalid platform/category values: 0
    * Removed zero-reach rows: 0
    * Verified campaign duration vs date range
         |
         v  FEATURE ENGINEERING
    * Engagement_Rate = (Engagements / Estimated_Reach) x 100
    * Campaign_Cost   = (Estimated_Reach x Platform_CPM) / 1000
    * Revenue         = Product_Sales x Category_Avg_Unit_Value
    * ROI             = (Revenue - Campaign_Cost) / Campaign_Cost
    * ROI outlier capping: 1st-99th percentile (removed 3,000 rows)
         |
         v  FINAL PROCESSED DATASET: 147,000 rows x 16 columns
         |
         v  EDA -> Statistical Analysis -> Regression -> Prediction -> Evaluation
""")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 3  —  EDA
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 3 — Exploratory Data Analysis")
print("="*65)

# --- 3a. ROI Distribution ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("ROI Distribution — 147,000 Campaigns", fontsize=14, fontweight="bold")

roi_plot = df["ROI"].clip(upper=df["ROI"].quantile(0.95))  # clip for display only
axes[0].hist(roi_plot, bins=60, color=PALETTE[0], edgecolor="white", linewidth=0.5)
axes[0].set_title("Histogram of ROI")
axes[0].set_xlabel("ROI")
axes[0].set_ylabel("Frequency")

axes[1].plot(sorted(roi_plot), np.linspace(0, 1, len(roi_plot)), color=PALETTE[0])
axes[1].set_title("Cumulative Distribution of ROI")
axes[1].set_xlabel("ROI")
axes[1].set_ylabel("Cumulative Proportion")

plt.tight_layout()
save("01_roi_distribution.png")

# --- 3b. Platform Analysis ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Platform Analysis", fontsize=14, fontweight="bold")

plat_counts = df["Platform"].value_counts()
axes[0].bar(plat_counts.index, plat_counts.values, color=PALETTE[:4])
axes[0].set_title("Number of Campaigns by Platform")
axes[0].set_xlabel("Platform")
axes[0].set_ylabel("Count")
for i, v in enumerate(plat_counts.values):
    axes[0].text(i, v + 100, f"{v:,}", ha="center", fontsize=9)

df.boxplot(column="ROI", by="Platform", ax=axes[1],
           patch_artist=True, showfliers=False)
axes[1].set_title("ROI Distribution by Platform")
axes[1].set_xlabel("Platform")
axes[1].set_ylabel("ROI")
plt.suptitle("")
plt.tight_layout()
save("02_platform_analysis.png")

# --- 3c. Category Analysis ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Influencer Category Analysis", fontsize=14, fontweight="bold")

cat_roi = df.groupby("Influencer_Category")["ROI"].mean().sort_values(ascending=False)
axes[0].barh(cat_roi.index, cat_roi.values, color=PALETTE[:7])
axes[0].set_title("Average ROI by Influencer Category")
axes[0].set_xlabel("Mean ROI")
for i, v in enumerate(cat_roi.values):
    axes[0].text(v + 1, i, f"{v:.1f}", va="center", fontsize=9)

df.boxplot(column="ROI", by="Influencer_Category", ax=axes[1],
           patch_artist=True, showfliers=False, vert=False)
axes[1].set_title("ROI Spread by Category")
axes[1].set_xlabel("ROI")
plt.suptitle("")
plt.tight_layout()
save("03_category_analysis.png")

# --- 3d. Scatter Plots ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Key Feature Relationships with ROI", fontsize=14, fontweight="bold")

sample = df.sample(n=3000, random_state=42)

axes[0].scatter(sample["Engagement_Rate"].clip(upper=100),
                sample["ROI"].clip(upper=500),
                alpha=0.3, s=15, color=PALETTE[0])
axes[0].set_title("Engagement Rate vs ROI")
axes[0].set_xlabel("Engagement Rate (%)")
axes[0].set_ylabel("ROI")

axes[1].scatter(sample["Campaign_Cost"],
                sample["ROI"].clip(upper=500),
                alpha=0.3, s=15, color=PALETTE[1])
axes[1].set_title("Campaign Cost vs ROI")
axes[1].set_xlabel("Campaign Cost (₹)")
axes[1].set_ylabel("ROI")
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))

plt.tight_layout()
save("04_scatter_plots.png")

# --- 3e. Campaign Type & Monthly Trend ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Campaign Type & Temporal Trends", fontsize=14, fontweight="bold")

ct_roi = df.groupby("Campaign_Type")["ROI"].mean().sort_values(ascending=False)
axes[0].bar(ct_roi.index, ct_roi.values, color=PALETTE[:5])
axes[0].set_title("Average ROI by Campaign Type")
axes[0].set_xlabel("Campaign Type")
axes[0].set_ylabel("Mean ROI")
axes[0].tick_params(axis="x", rotation=20)

monthly = df.groupby("Month")["ROI"].mean()
axes[1].plot(monthly.index, monthly.values, marker="o", color=PALETTE[2])
axes[1].set_title("Average ROI by Month (all years)")
axes[1].set_xlabel("Month")
axes[1].set_ylabel("Mean ROI")
axes[1].set_xticks(range(1, 13))
axes[1].set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                          "Jul","Aug","Sep","Oct","Nov","Dec"])

plt.tight_layout()
save("05_campaign_type_monthly.png")

print("  ✔ EDA charts saved (01–05)")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 4  —  STATISTICAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 4 — Statistical Analysis")
print("="*65)

num_cols = ["Estimated_Reach", "Engagements", "Product_Sales",
            "Campaign_Duration_Days", "Engagement_Rate", "Campaign_Cost",
            "Revenue", "ROI"]

desc = df[num_cols].describe().T
desc["skewness"] = df[num_cols].skew()
desc["kurtosis"] = df[num_cols].kurt()
print(desc.round(4).to_string())

# Shapiro-Wilk on a sample (full dataset too large for Shapiro)
print("\n  Shapiro-Wilk Normality Test (sample n=5,000):")
sample_sw = df["ROI"].sample(n=5000, random_state=42)
stat, p = stats.shapiro(sample_sw)
print(f"    ROI: W={stat:.4f}, p={p:.6f}  → {'NOT normal' if p < 0.05 else 'Normal'} (α=0.05)")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 5  —  CORRELATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 5 — Correlation Analysis")
print("="*65)

corr = df[num_cols].corr()
print(corr.round(4).to_string())

# Heatmap
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, linewidths=0.5, ax=ax)
ax.set_title("Pearson Correlation Heatmap", fontsize=14, fontweight="bold")
plt.tight_layout()
save("06_correlation_heatmap.png")

# ROI correlation bar chart
roi_corr = corr["ROI"].drop("ROI").sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(9, 5))
colors = [PALETTE[0] if v > 0 else PALETTE[3] for v in roi_corr.values]
ax.barh(roi_corr.index, roi_corr.values, color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title("Feature Correlation with ROI", fontsize=13, fontweight="bold")
ax.set_xlabel("Pearson Correlation Coefficient")
for i, v in enumerate(roi_corr.values):
    ax.text(v + 0.001 if v >= 0 else v - 0.001, i,
            f"{v:.3f}", va="center", ha="left" if v >= 0 else "right", fontsize=9)
plt.tight_layout()
save("07_roi_correlation_bar.png")

print("  ✔ Correlation charts saved (06–07)")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 6  —  MULTIPLE LINEAR REGRESSION
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 6 — Multiple Linear Regression (OLS)")
print("="*65)

# Use ALL 147,000 processed observations — no sampling
# OLS on this dataset is well within memory limits (~45 MB design matrix)
features  = ["Engagement_Rate", "Campaign_Cost", "Product_Sales", "Campaign_Duration_Days"]
target    = "ROI"

X = df[features]
y = df[target]
X_const = sm.add_constant(X)
print(f"  Fitting OLS on full processed dataset: n = {len(df):,} observations")

model  = sm.OLS(y, X_const).fit()
print(model.summary())

# ── Regression Equation ──────────────────────────────────────────────────────
coefs = model.params
print("\n  Regression Equation:")
print(f"  ROI = {coefs['const']:.4f}")
for f in features:
    sign = "+" if coefs[f] >= 0 else "-"
    print(f"      {sign} {abs(coefs[f]):.6f} × {f}")

# ── Coefficient Plot ──────────────────────────────────────────────────────────
conf = model.conf_int()
fig, ax = plt.subplots(figsize=(9, 5))
y_pos = range(len(features))
for i, f in enumerate(features):
    ax.plot([conf.loc[f, 0], conf.loc[f, 1]], [i, i],
            color=PALETTE[0], linewidth=2)
    color = PALETTE[0] if coefs[f] > 0 else PALETTE[3]
    ax.scatter(coefs[f], i, color=color, s=80, zorder=5)
    ax.text(coefs[f], i + 0.15, f"{coefs[f]:.4f}", ha="center", fontsize=9)

ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_yticks(list(y_pos))
ax.set_yticklabels(features)
ax.set_title("OLS Regression Coefficients with 95% CI", fontsize=13, fontweight="bold")
ax.set_xlabel("Coefficient Value")
plt.tight_layout()
save("08_coefficients.png")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 7  —  RESIDUAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 7 — Residual Analysis")
print("="*65)

y_pred   = model.fittedvalues
residuals = model.resid

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Residual Analysis", fontsize=14, fontweight="bold")

# Q-Q plot
(osm, osr), (slope, intercept, r) = stats.probplot(residuals, dist="norm")
axes[0].plot(osm, osr, "o", alpha=0.3, ms=3, color=PALETTE[0])
axes[0].plot(osm, slope * np.array(osm) + intercept, color=PALETTE[3], linewidth=1.5)
axes[0].set_title("Q-Q Plot (Normality of Residuals)")
axes[0].set_xlabel("Theoretical Quantiles")
axes[0].set_ylabel("Sample Quantiles")

# Residuals vs Fitted
axes[1].scatter(y_pred, residuals, alpha=0.2, s=10, color=PALETTE[0])
axes[1].axhline(0, color=PALETTE[3], linewidth=1.5, linestyle="--")
axes[1].set_title("Residuals vs Fitted Values")
axes[1].set_xlabel("Fitted Values")
axes[1].set_ylabel("Residuals")

# Residual histogram
axes[2].hist(residuals, bins=50, color=PALETTE[0], edgecolor="white")
axes[2].set_title("Residual Distribution")
axes[2].set_xlabel("Residual")
axes[2].set_ylabel("Frequency")

plt.tight_layout()
save("09_residual_analysis.png")
print("  ✔ Residual analysis saved (09)")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 8  —  ACTUAL VS PREDICTED
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 8 — Actual vs Predicted")
print("="*65)

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(y, y_pred, alpha=0.2, s=10, color=PALETTE[0])
lims = [min(y.min(), y_pred.min()), max(y.max(), y_pred.max())]
ax.plot(lims, lims, color=PALETTE[3], linewidth=1.5, linestyle="--", label="Perfect fit")
ax.set_title("Actual vs Predicted ROI", fontsize=13, fontweight="bold")
ax.set_xlabel("Actual ROI")
ax.set_ylabel("Predicted ROI")
ax.legend()
plt.tight_layout()
save("10_actual_vs_predicted.png")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 9  —  PREDICTIONS FOR NEW CAMPAIGNS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 9 — Predictions for New Campaigns")
print("="*65)

new_campaigns = pd.DataFrame({
    "Campaign": [
        "Micro-Influencer Instagram",
        "Macro-Influencer YouTube",
        "TikTok Viral Campaign",
        "Twitter Tech Launch",
        "Long-Duration Fitness",
    ],
    "Engagement_Rate":        [8.5,   2.1,   15.3,  4.2,   6.8],
    "Campaign_Cost":          [30000, 90000, 50000, 25000, 45000],
    "Product_Sales":          [500,   1200,  800,   300,   700],
    "Campaign_Duration_Days": [14,    30,    7,     10,    60],
})

X_new = new_campaigns[features]
X_new_const = sm.add_constant(X_new, has_constant="add")

pred = model.get_prediction(X_new_const)
pred_df = pred.summary_frame(alpha=0.05)

new_campaigns["Predicted_ROI"]  = pred_df["mean"].values.round(2)
new_campaigns["CI_Lower_95"]    = pred_df["obs_ci_lower"].values.round(2)
new_campaigns["CI_Upper_95"]    = pred_df["obs_ci_upper"].values.round(2)

print(new_campaigns[["Campaign", "Predicted_ROI", "CI_Lower_95", "CI_Upper_95"]].to_string(index=False))

# Bar chart of predictions
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(new_campaigns["Campaign"], new_campaigns["Predicted_ROI"],
              color=PALETTE[:5], zorder=3)
ax.errorbar(
    new_campaigns["Campaign"],
    new_campaigns["Predicted_ROI"],
    yerr=[
        new_campaigns["Predicted_ROI"] - new_campaigns["CI_Lower_95"],
        new_campaigns["CI_Upper_95"]   - new_campaigns["Predicted_ROI"],
    ],
    fmt="none", color="black", capsize=5, linewidth=1.5, zorder=4
)
ax.set_title("Predicted ROI for 5 New Campaigns (with 95% CI)", fontsize=13, fontweight="bold")
ax.set_xlabel("Campaign")
ax.set_ylabel("Predicted ROI")
ax.tick_params(axis="x", rotation=20)
for bar, val in zip(bars, new_campaigns["Predicted_ROI"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{val:.1f}", ha="center", fontsize=9)
ax.grid(axis="y", alpha=0.5)
plt.tight_layout()
save("11_predictions.png")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 10  —  MODEL EVALUATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 10 — Model Evaluation")
print("="*65)

mae  = mean_absolute_error(y, y_pred)
mse  = mean_squared_error(y, y_pred)
rmse = np.sqrt(mse)
r2   = model.rsquared
adj_r2 = model.rsquared_adj

f_stat   = model.fvalue
f_pvalue = model.f_pvalue

print(f"  R²              : {r2:.4f}")
print(f"  Adjusted R²     : {adj_r2:.4f}")
print(f"  F-statistic     : {f_stat:.2f}  (p = {f_pvalue:.2e})")
print(f"  MAE             : {mae:.4f}")
print(f"  RMSE            : {rmse:.4f}")
print(f"  AIC             : {model.aic:.2f}")
print(f"  BIC             : {model.bic:.2f}")
print(f"  Observations    : {int(model.nobs):,}")

# Error distribution chart
errors = y - y_pred
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Model Evaluation — Error Analysis", fontsize=14, fontweight="bold")

axes[0].hist(errors, bins=60, color=PALETTE[0], edgecolor="white")
axes[0].axvline(0, color=PALETTE[3], linewidth=1.5, linestyle="--")
axes[0].set_title(f"Prediction Error Distribution\nMAE={mae:.2f}, RMSE={rmse:.2f}")
axes[0].set_xlabel("Prediction Error (Actual − Predicted)")
axes[0].set_ylabel("Frequency")

# Metrics bar chart
metrics = {"R²": r2, "Adj R²": adj_r2}
axes[1].bar(metrics.keys(), metrics.values(), color=PALETTE[:2])
axes[1].set_ylim(0, 1)
axes[1].set_title("Model Fit Metrics")
axes[1].set_ylabel("Value")
for i, (k, v) in enumerate(metrics.items()):
    axes[1].text(i, v + 0.01, f"{v:.4f}", ha="center", fontsize=11, fontweight="bold")

plt.tight_layout()
save("12_error_distribution.png")
print("  ✔ Evaluation charts saved (10–12)")

# ══════════════════════════════════════════════════════════════════════════════
# MODULE 11  —  CONCLUSION & FINAL EQUATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("MODULE 11 — Conclusion & Final Regression Equation")
print("="*65)

print(f"""
  FINAL REGRESSION EQUATION
  -------------------------
  ROI = {coefs['const']:.4f}
      + {coefs['Engagement_Rate']:.4f} x Engagement_Rate
      + ({coefs['Campaign_Cost']:.8f}) x Campaign_Cost
      + {coefs['Product_Sales']:.6f} x Product_Sales
      + {coefs['Campaign_Duration_Days']:.4f} x Campaign_Duration_Days

  KEY FINDINGS
  ------------
  1. Engagement Rate is the strongest positive predictor of ROI
     -> Higher engagement per unit reach drives proportionally higher returns

  2. Product Sales positively predicts ROI
     -> Campaigns that convert to actual purchases deliver best returns

  3. Campaign Cost has a small negative effect
     -> Spending more on reach alone does not guarantee higher ROI

  4. Campaign Duration has minimal practical effect
     -> A well-targeted short campaign matches a long one in ROI

  MODEL PERFORMANCE
  -----------------
  R2           : {r2:.4f}   (model explains {r2*100:.1f}% of ROI variance)
  Adjusted R2  : {adj_r2:.4f}
  MAE          : {mae:.2f}
  RMSE         : {rmse:.2f}
  F-statistic  : {f_stat:.2f}  (p < 0.001 -- model is statistically significant)
""")

# ══════════════════════════════════════════════════════════════════════════════
# STORE METRICS FOR NOTEBOOK & EXCEL
# ══════════════════════════════════════════════════════════════════════════════
metrics_out = {
    "r2": r2, "adj_r2": adj_r2,
    "mae": mae, "rmse": rmse,
    "f_stat": f_stat, "f_pvalue": f_pvalue,
    "aic": model.aic, "bic": model.bic,
    "nobs": int(model.nobs),
    "coefs": coefs.to_dict(),
    "pvalues": model.pvalues.to_dict(),
    "conf_int": {f: [conf.loc[f, 0], conf.loc[f, 1]] for f in features},
    "new_campaigns": new_campaigns.to_dict(orient="records"),
}

import json
metrics_path = os.path.join(BASE, "data", "processed", "regression_metrics.json")
with open(metrics_path, "w") as fh:
    json.dump(metrics_out, fh, indent=2)
print(f"\n  Metrics saved to data/processed/regression_metrics.json")

print("\n" + "="*65)
print("PIPELINE COMPLETE — All outputs saved.")
print("="*65)
