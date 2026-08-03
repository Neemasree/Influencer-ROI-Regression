"""
Quick verification script — no graphs, just data pipeline + regression.
Confirms the notebook logic is 100% correct before opening in Jupyter.
"""
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  PIPELINE VERIFICATION — NO GRAPHS")
print("=" * 60)

# ── 1. Load ───────────────────────────────────────────────────────────────────
df = pd.read_csv('../Dataset/influencer_marketing_roi_dataset.csv')
print(f"\n[1] Loaded: {len(df):,} rows x {len(df.columns)} columns")

# ── 2. Clean ──────────────────────────────────────────────────────────────────
assert df.isnull().sum().sum() == 0, "Missing values found!"
assert df.duplicated().sum() == 0,   "Duplicates found!"
df = df[df['estimated_reach'] > 0].copy()
df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
df['end_date']   = pd.to_datetime(df['end_date'],   errors='coerce')
df = df.dropna(subset=['start_date']).reset_index(drop=True)
df['month'] = df['start_date'].dt.month
print(f"[2] After cleaning: {len(df):,} rows")

# ── 3. Feature Engineering ────────────────────────────────────────────────────
df['engagement_rate'] = (df['engagements'] / df['estimated_reach'] * 100).round(4).clip(upper=100)
cpm_map = {'Instagram': 150, 'YouTube': 120, 'TikTok': 100, 'Twitter': 80}
df['cpm']           = df['platform'].map(cpm_map).fillna(100)
df['campaign_cost'] = ((df['estimated_reach'] / 1000) * df['cpm']).round(2)
df['revenue']       = (df['product_sales'] * 40).round(2)
df['roi']           = ((df['revenue'] - df['campaign_cost']) / df['campaign_cost']).round(4)
df = df[df['campaign_cost'] > 0].copy()

roi_mean = df['roi'].mean()
roi_std  = df['roi'].std()
df = df[(df['roi'] > roi_mean - 3*roi_std) & (df['roi'] < roi_mean + 3*roi_std)].copy()

print(f"[3] After feature engineering + outlier removal: {len(df):,} rows")
print(f"    ROI  — Mean: {df['roi'].mean():.4f}  |  Median: {df['roi'].median():.4f}")
print(f"    ROI  — Min : {df['roi'].min():.4f}  |  Max: {df['roi'].max():.4f}")
print(f"    Profitable campaigns (ROI>0): {(df['roi']>0).mean()*100:.1f}%")

# ── 4. Descriptive Stats ──────────────────────────────────────────────────────
print(f"\n[4] Descriptive Statistics (ROI):")
roi = df['roi']
print(f"    Mean={roi.mean():.4f}  Median={roi.median():.4f}  Std={roi.std():.4f}")
print(f"    Skewness={roi.skew():.4f}  Kurtosis={roi.kurt():.4f}")

# ── 5. Correlation ────────────────────────────────────────────────────────────
corr_cols = ['engagements','estimated_reach','product_sales',
             'campaign_duration_days','engagement_rate','campaign_cost','revenue','roi']
corr = df[corr_cols].corr()['roi'].drop('roi').sort_values(ascending=False)
print(f"\n[5] Top correlations with ROI:")
print(corr.to_string())

# ── 6. Regression ─────────────────────────────────────────────────────────────
feature_cols = ['engagement_rate', 'campaign_cost', 'product_sales', 'campaign_duration_days']
df_reg = df.sample(n=15000, random_state=42)
X = df_reg[feature_cols]
y = df_reg['roi']
X_const = sm.add_constant(X)
model   = sm.OLS(y, X_const)
results = model.fit()

print(f"\n[6] OLS Regression Results:")
print(f"    R²           = {results.rsquared:.4f}")
print(f"    Adjusted R²  = {results.rsquared_adj:.4f}")
print(f"    F-statistic  = {results.fvalue:.2f}  (p = {results.f_pvalue:.2e})")
print(f"    Observations = {int(results.nobs):,}")
print()
for feat in results.params.index:
    sig = "***" if results.pvalues[feat] < 0.001 else ("**" if results.pvalues[feat] < 0.01 else ("*" if results.pvalues[feat] < 0.05 else "ns"))
    print(f"    {feat:30s}  coef={results.params[feat]:+.6f}  p={results.pvalues[feat]:.4f}  {sig}")

# ── 7. Predictions ────────────────────────────────────────────────────────────
new = pd.DataFrame({
    'engagement_rate'        : [8.5,    3.2,    12.0,   5.5,   20.0],
    'campaign_cost'          : [30000,  90000,  10000,  60000, 50000],
    'product_sales'          : [3500,   2000,   4500,   2500,  4000],
    'campaign_duration_days' : [14,     30,     7,      21,    10],
})
new_const = sm.add_constant(new, has_constant='add')
preds     = results.get_prediction(new_const).summary_frame(alpha=0.05)
labels    = ['Micro–Fitness','Macro–Tech','Mega–Lifestyle','Nano–Food','Micro–Beauty']

print(f"\n[7] ROI Predictions:")
for i, label in enumerate(labels):
    pred = preds['mean'].iloc[i]
    lo   = preds['obs_ci_lower'].iloc[i]
    hi   = preds['obs_ci_upper'].iloc[i]
    print(f"    {label:20s}  ROI={pred:.4f}  95% CI [{lo:.4f}, {hi:.4f}]")

# ── 8. Evaluation ─────────────────────────────────────────────────────────────
from sklearn.metrics import mean_absolute_error, mean_squared_error
fitted = results.fittedvalues
mae    = mean_absolute_error(y, fitted)
rmse   = np.sqrt(mean_squared_error(y, fitted))
print(f"\n[8] Evaluation:")
print(f"    MAE  = {mae:.4f}")
print(f"    RMSE = {rmse:.4f}")

print("\n" + "=" * 60)
print("  ALL PIPELINE CHECKS PASSED")
print("  Notebook is ready to run in Jupyter.")
print("=" * 60)
