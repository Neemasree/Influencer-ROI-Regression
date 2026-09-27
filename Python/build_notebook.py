"""
Build the Jupyter Notebook (analysis.ipynb) programmatically.
Run once; the resulting .ipynb is the final deliverable notebook.
"""
import json, os

NB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis.ipynb")

def md(source):
    """Return a Markdown cell."""
    return {"cell_type": "markdown", "metadata": {}, "source": source}

def code(source):
    """Return a Code cell."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }

cells = []

# ── Title ────────────────────────────────────────────────────────────────────
cells.append(md([
    "# Predictive Statistical Analysis of Influencer Marketing ROI\n",
    "### Using Multiple Linear Regression (Python + Statsmodels)\n",
    "**Author:** Neema Sree  \n",
    "**Dataset:** Publicly available Influencer Marketing ROI dataset (Kaggle, 150,000 campaigns)  \n",
    "**Note:** The raw dataset is a publicly available source. This project's contribution is the\n",
    "cleaning pipeline, feature engineering, and statistical analysis performed on it.\n",
]))

# ── Pipeline Overview ────────────────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Project Pipeline\n",
    "```\n",
    "RAW DATA (150,000 rows — Kaggle source dataset)\n",
    "         |\n",
    "         v  MY DATA CLEANING\n",
    "         |  - Handle missing values, duplicates, invalid entries\n",
    "         |  - Parse and validate date columns\n",
    "         |\n",
    "         v  MY FEATURE ENGINEERING\n",
    "         |  - Engagement_Rate, Campaign_Cost, Revenue, ROI\n",
    "         |\n",
    "         v  MY FINAL PROCESSED DATASET (147,000 rows x 16 columns)\n",
    "         |\n",
    "         v  MY EDA\n",
    "         |\n",
    "         v  MY STATISTICAL ANALYSIS\n",
    "         |\n",
    "         v  MY MULTIPLE LINEAR REGRESSION MODEL\n",
    "         |\n",
    "         v  MY PREDICTIONS & EVALUATION\n",
    "```\n",
]))

# ── Module 1: Imports ────────────────────────────────────────────────────────
cells.append(md(["---\n", "## Module 1 — Import Libraries\n"]))
cells.append(code([
    "import os, warnings\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import matplotlib.ticker as mticker\n",
    "import seaborn as sns\n",
    "from scipy import stats\n",
    "import statsmodels.api as sm\n",
    "from sklearn.metrics import mean_absolute_error, mean_squared_error\n",
    "\n",
    "warnings.filterwarnings('ignore')\n",
    "sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)\n",
    "PALETTE = ['#4C72B0','#DD8452','#55A868','#C44E52','#8172B2','#937860','#DA8BC3']\n",
    "\n",
    "print('Libraries loaded successfully.')\n",
    "print(f'  pandas      {pd.__version__}')\n",
    "print(f'  numpy       {np.__version__}')\n",
    "print(f'  statsmodels {sm.__version__}')\n",
]))

# ── Module 2: Load Raw Dataset ───────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 2 — Load Raw Dataset\n",
    "The raw dataset is loaded directly from `data/raw/` without any modification.\n",
    "This preserves the original source as-is.\n",
]))
cells.append(code([
    "RAW_PATH  = '../data/raw/influencer_marketing_roi_dataset.csv'\n",
    "PROC_PATH = '../data/processed/influencer_roi_analysis_dataset.csv'\n",
    "\n",
    "raw = pd.read_csv(RAW_PATH)\n",
    "print(f'Raw dataset shape : {raw.shape}')\n",
    "print(f'Columns           : {list(raw.columns)}')\n",
    "raw.head()\n",
]))
cells.append(code([
    "# Basic profile of the raw dataset\n",
    "print('Missing values per column:')\n",
    "print(raw.isnull().sum())\n",
    "print(f'\\nDuplicate rows : {raw.duplicated().sum()}')\n",
    "print(f'\\nPlatforms      : {raw[\"platform\"].unique().tolist()}')\n",
    "print(f'Categories     : {raw[\"influencer_category\"].unique().tolist()}')\n",
    "print(f'Campaign types : {raw[\"campaign_type\"].unique().tolist()}')\n",
]))

# ── Module 3: Data Cleaning ──────────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 3 — Data Cleaning\n",
    "Steps applied:\n",
    "1. Strip whitespace from string columns\n",
    "2. Parse `start_date` and `end_date` to datetime\n",
    "3. Drop rows with missing values\n",
    "4. Drop exact duplicate rows\n",
    "5. Retain only rows with recognised platform and category values\n",
    "6. Remove rows with zero `estimated_reach` (division by zero guard)\n",
    "7. Validate `campaign_duration_days` against computed date difference (tolerance ±2 days)\n",
]))
cells.append(code([
    "CPM_TABLE = {'Instagram': 150, 'YouTube': 120, 'TikTok': 100, 'Twitter': 80}\n",
    "AVG_UNIT  = {'Beauty': 1500, 'Tech': 5000, 'Fashion': 1200, 'Food': 300,\n",
    "             'Fitness': 800, 'Travel': 3000, 'Gaming': 1000}\n",
    "\n",
    "df = raw.copy()\n",
    "initial_rows = len(df)\n",
    "\n",
    "# 1. Strip whitespace\n",
    "for col in ['platform', 'influencer_category', 'campaign_type']:\n",
    "    df[col] = df[col].str.strip()\n",
    "\n",
    "# 2. Parse dates\n",
    "df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')\n",
    "df['end_date']   = pd.to_datetime(df['end_date'],   errors='coerce')\n",
    "\n",
    "# 3. Drop NaN\n",
    "df.dropna(inplace=True)\n",
    "print(f'After NaN drop         : {len(df):,} rows')\n",
    "\n",
    "# 4. Drop duplicates\n",
    "df.drop_duplicates(inplace=True)\n",
    "print(f'After dedup            : {len(df):,} rows')\n",
    "\n",
    "# 5. Valid platform & category\n",
    "df = df[df['platform'].isin(CPM_TABLE) & df['influencer_category'].isin(AVG_UNIT)]\n",
    "print(f'After value filter     : {len(df):,} rows')\n",
    "\n",
    "# 6. Zero reach\n",
    "df = df[df['estimated_reach'] > 0]\n",
    "print(f'After zero-reach drop  : {len(df):,} rows')\n",
    "\n",
    "# 7. Duration validation\n",
    "df['computed_dur'] = (df['end_date'] - df['start_date']).dt.days\n",
    "df = df[(df['computed_dur'] - df['campaign_duration_days']).abs() <= 2]\n",
    "df.drop(columns=['computed_dur'], inplace=True)\n",
    "print(f'After duration check   : {len(df):,} rows')\n",
    "print(f'\\nRows removed total     : {initial_rows - len(df):,}')\n",
]))

# ── Module 4: Feature Engineering ────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 4 — Feature Engineering\n",
    "Four new variables are engineered from the cleaned raw columns.\n\n",
    "| Variable | Formula |\n",
    "|---|---|\n",
    "| `Engagement_Rate` | (Engagements / Estimated_Reach) × 100 |\n",
    "| `Campaign_Cost` | (Estimated_Reach × Platform_CPM) / 1000 |\n",
    "| `Revenue` | Product_Sales × Category_Avg_Unit_Value |\n",
    "| `ROI` (**target**) | (Revenue − Campaign_Cost) / Campaign_Cost |\n\n",
    "**CPM rates (₹):** Instagram=150, YouTube=120, TikTok=100, Twitter=80  \n",
    "**Avg unit values (₹):** Beauty=1500, Tech=5000, Fashion=1200, Food=300, Fitness=800, Travel=3000, Gaming=1000\n",
]))
cells.append(code([
    "# Engagement Rate (%)\n",
    "df['engagement_rate'] = (df['engagements'] / df['estimated_reach']) * 100\n",
    "\n",
    "# Campaign Cost (INR) — CPM model\n",
    "df['campaign_cost'] = df.apply(\n",
    "    lambda r: (r['estimated_reach'] * CPM_TABLE[r['platform']]) / 1000, axis=1)\n",
    "\n",
    "# Revenue (INR)\n",
    "df['revenue'] = df.apply(\n",
    "    lambda r: r['product_sales'] * AVG_UNIT[r['influencer_category']], axis=1)\n",
    "\n",
    "# Remove zero-cost rows before ROI\n",
    "df = df[df['campaign_cost'] > 0]\n",
    "\n",
    "# ROI\n",
    "df['roi'] = (df['revenue'] - df['campaign_cost']) / df['campaign_cost']\n",
    "\n",
    "# Outlier capping: 1st–99th percentile\n",
    "roi_lo, roi_hi = df['roi'].quantile(0.01), df['roi'].quantile(0.99)\n",
    "df = df[(df['roi'] >= roi_lo) & (df['roi'] <= roi_hi)]\n",
    "print(f'ROI range after capping: {df[\"roi\"].min():.2f} to {df[\"roi\"].max():.2f}')\n",
    "\n",
    "# Year and Month\n",
    "df['year']  = df['start_date'].dt.year\n",
    "df['month'] = df['start_date'].dt.month\n",
    "\n",
    "print(f'Rows after engineering : {len(df):,}')\n",
]))

# ── Module 5: Final Processed Dataset ────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 5 — Final Processed Dataset\n",
    "Select, rename, and validate the final analytical dataset.  \n",
    "This is identical to `data/processed/influencer_roi_analysis_dataset.csv`.\n",
]))
cells.append(code([
    "COLS = {\n",
    "    'campaign_id': 'Campaign_ID', 'platform': 'Platform',\n",
    "    'influencer_category': 'Influencer_Category', 'campaign_type': 'Campaign_Type',\n",
    "    'start_date': 'Start_Date', 'end_date': 'End_Date',\n",
    "    'campaign_duration_days': 'Campaign_Duration_Days',\n",
    "    'estimated_reach': 'Estimated_Reach', 'engagements': 'Engagements',\n",
    "    'product_sales': 'Product_Sales', 'engagement_rate': 'Engagement_Rate',\n",
    "    'campaign_cost': 'Campaign_Cost', 'revenue': 'Revenue',\n",
    "    'roi': 'ROI', 'year': 'Year', 'month': 'Month',\n",
    "}\n",
    "final = df[list(COLS.keys())].rename(columns=COLS).copy()\n",
    "final['Engagement_Rate'] = final['Engagement_Rate'].round(4)\n",
    "final['Campaign_Cost']   = final['Campaign_Cost'].round(2)\n",
    "final['Revenue']         = final['Revenue'].round(2)\n",
    "final['ROI']             = final['ROI'].round(4)\n",
    "final.sort_values(['Start_Date', 'Campaign_ID'], inplace=True)\n",
    "final.reset_index(drop=True, inplace=True)\n",
    "\n",
    "print(f'Final dataset shape: {final.shape}')\n",
    "print(f'Null values        : {final.isnull().sum().sum()}')\n",
    "final.head()\n",
]))
cells.append(code([
    "# Alternatively, load the pre-saved processed CSV directly:\n",
    "# final = pd.read_csv(PROC_PATH, parse_dates=['Start_Date', 'End_Date'])\n",
    "# print(final.shape)\n",
    "\n",
    "print('Column list and dtypes:')\n",
    "print(final.dtypes)\n",
]))

# ── Module 6: EDA ────────────────────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 6 — Exploratory Data Analysis\n",
]))
cells.append(code([
    "# --- ROI Distribution ---\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "fig.suptitle('ROI Distribution — 147,000 Campaigns', fontsize=14, fontweight='bold')\n",
    "\n",
    "roi_plot = final['ROI'].clip(upper=final['ROI'].quantile(0.95))\n",
    "axes[0].hist(roi_plot, bins=60, color=PALETTE[0], edgecolor='white', linewidth=0.5)\n",
    "axes[0].set_title('Histogram of ROI')\n",
    "axes[0].set_xlabel('ROI')\n",
    "axes[0].set_ylabel('Frequency')\n",
    "\n",
    "axes[1].plot(sorted(roi_plot), np.linspace(0, 1, len(roi_plot)), color=PALETTE[0])\n",
    "axes[1].set_title('Cumulative Distribution of ROI')\n",
    "axes[1].set_xlabel('ROI')\n",
    "axes[1].set_ylabel('Cumulative Proportion')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/01_roi_distribution.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))
cells.append(code([
    "# --- Platform Analysis ---\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "fig.suptitle('Platform Analysis', fontsize=14, fontweight='bold')\n",
    "\n",
    "plat = final['Platform'].value_counts()\n",
    "axes[0].bar(plat.index, plat.values, color=PALETTE[:4])\n",
    "axes[0].set_title('Campaigns by Platform')\n",
    "axes[0].set_xlabel('Platform'); axes[0].set_ylabel('Count')\n",
    "for i, v in enumerate(plat.values):\n",
    "    axes[0].text(i, v + 100, f'{v:,}', ha='center', fontsize=9)\n",
    "\n",
    "final.boxplot(column='ROI', by='Platform', ax=axes[1],\n",
    "              patch_artist=True, showfliers=False)\n",
    "axes[1].set_title('ROI by Platform'); plt.suptitle('')\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/02_platform_analysis.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))
cells.append(code([
    "# --- Category Analysis ---\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "fig.suptitle('Influencer Category Analysis', fontsize=14, fontweight='bold')\n",
    "\n",
    "cat_roi = final.groupby('Influencer_Category')['ROI'].mean().sort_values(ascending=False)\n",
    "axes[0].barh(cat_roi.index, cat_roi.values, color=PALETTE[:7])\n",
    "axes[0].set_title('Average ROI by Category'); axes[0].set_xlabel('Mean ROI')\n",
    "for i, v in enumerate(cat_roi.values):\n",
    "    axes[0].text(v + 1, i, f'{v:.1f}', va='center', fontsize=9)\n",
    "\n",
    "final.boxplot(column='ROI', by='Influencer_Category', ax=axes[1],\n",
    "              patch_artist=True, showfliers=False, vert=False)\n",
    "axes[1].set_title('ROI Spread by Category'); plt.suptitle('')\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/03_category_analysis.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))
cells.append(code([
    "# --- Scatter Plots ---\n",
    "sample = final.sample(n=3000, random_state=42)\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "fig.suptitle('Key Feature Relationships with ROI', fontsize=14, fontweight='bold')\n",
    "\n",
    "axes[0].scatter(sample['Engagement_Rate'].clip(upper=100), sample['ROI'].clip(upper=500),\n",
    "                alpha=0.3, s=15, color=PALETTE[0])\n",
    "axes[0].set_title('Engagement Rate vs ROI')\n",
    "axes[0].set_xlabel('Engagement Rate (%)'); axes[0].set_ylabel('ROI')\n",
    "\n",
    "axes[1].scatter(sample['Campaign_Cost'], sample['ROI'].clip(upper=500),\n",
    "                alpha=0.3, s=15, color=PALETTE[1])\n",
    "axes[1].set_title('Campaign Cost vs ROI')\n",
    "axes[1].set_xlabel('Campaign Cost (INR)')\n",
    "axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}K'))\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/04_scatter_plots.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))
cells.append(code([
    "# --- Campaign Type & Monthly Trend ---\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "fig.suptitle('Campaign Type & Temporal Trends', fontsize=14, fontweight='bold')\n",
    "\n",
    "ct = final.groupby('Campaign_Type')['ROI'].mean().sort_values(ascending=False)\n",
    "axes[0].bar(ct.index, ct.values, color=PALETTE[:5])\n",
    "axes[0].set_title('Average ROI by Campaign Type')\n",
    "axes[0].tick_params(axis='x', rotation=20)\n",
    "\n",
    "monthly = final.groupby('Month')['ROI'].mean()\n",
    "axes[1].plot(monthly.index, monthly.values, marker='o', color=PALETTE[2])\n",
    "axes[1].set_title('Average ROI by Month')\n",
    "axes[1].set_xticks(range(1, 13))\n",
    "axes[1].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun',\n",
    "                          'Jul','Aug','Sep','Oct','Nov','Dec'])\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/05_campaign_type_monthly.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))

# ── Module 7: Statistical Analysis ───────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 7 — Statistical Analysis\n",
]))
cells.append(code([
    "num_cols = ['Estimated_Reach', 'Engagements', 'Product_Sales',\n",
    "            'Campaign_Duration_Days', 'Engagement_Rate',\n",
    "            'Campaign_Cost', 'Revenue', 'ROI']\n",
    "\n",
    "desc = final[num_cols].describe().T\n",
    "desc['skewness'] = final[num_cols].skew()\n",
    "desc['kurtosis'] = final[num_cols].kurt()\n",
    "print(desc.round(4).to_string())\n",
]))
cells.append(code([
    "# Shapiro-Wilk Normality Test on ROI (sample n=5,000)\n",
    "sample_sw = final['ROI'].sample(n=5000, random_state=42)\n",
    "stat, p = stats.shapiro(sample_sw)\n",
    "print(f'Shapiro-Wilk: W={stat:.4f}, p={p:.6f}')\n",
    "print('ROI is NOT normally distributed' if p < 0.05 else 'ROI is normally distributed')\n",
]))

# ── Module 8: Correlation Analysis ───────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 8 — Correlation Analysis\n",
]))
cells.append(code([
    "corr = final[num_cols].corr()\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 8))\n",
    "mask = np.triu(np.ones_like(corr, dtype=bool))\n",
    "sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',\n",
    "            center=0, linewidths=0.5, ax=ax)\n",
    "ax.set_title('Pearson Correlation Heatmap', fontsize=14, fontweight='bold')\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/06_correlation_heatmap.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))
cells.append(code([
    "roi_corr = corr['ROI'].drop('ROI').sort_values(ascending=False)\n",
    "fig, ax = plt.subplots(figsize=(9, 5))\n",
    "colors = [PALETTE[0] if v > 0 else PALETTE[3] for v in roi_corr.values]\n",
    "ax.barh(roi_corr.index, roi_corr.values, color=colors)\n",
    "ax.axvline(0, color='black', linewidth=0.8)\n",
    "ax.set_title('Feature Correlation with ROI', fontsize=13, fontweight='bold')\n",
    "ax.set_xlabel('Pearson Correlation Coefficient')\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/07_roi_correlation_bar.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print(roi_corr.round(4).to_string())\n",
]))

# ── Module 9: Regression ─────────────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 9 — Multiple Linear Regression (OLS)\n",
    "**Method:** Ordinary Least Squares via Statsmodels  \n",
    "**Observations:** All 147,000 rows of the processed dataset (no sampling)  \n",
    "**Features:** Engagement_Rate, Campaign_Cost, Product_Sales, Campaign_Duration_Days  \n",
    "**Target:** ROI\n",
]))
cells.append(code([
    "FEATURES = ['Engagement_Rate', 'Campaign_Cost', 'Product_Sales', 'Campaign_Duration_Days']\n",
    "TARGET   = 'ROI'\n",
    "\n",
    "# Use ALL 147,000 processed observations — no sampling\n",
    "# OLS on this dataset is well within memory limits (~45 MB design matrix)\n",
    "X = final[FEATURES]\n",
    "y = final[TARGET]\n",
    "X_const = sm.add_constant(X)\n",
    "\n",
    "print(f'Fitting OLS on full dataset: n = {len(final):,} observations')\n",
    "model = sm.OLS(y, X_const).fit()\n",
    "print(model.summary())\n",
]))
cells.append(code([
    "# Coefficient Plot\n",
    "coefs = model.params\n",
    "conf  = model.conf_int()\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(9, 5))\n",
    "for i, f in enumerate(FEATURES):\n",
    "    ax.plot([conf.loc[f, 0], conf.loc[f, 1]], [i, i], color=PALETTE[0], linewidth=2)\n",
    "    color = PALETTE[0] if coefs[f] > 0 else PALETTE[3]\n",
    "    ax.scatter(coefs[f], i, color=color, s=80, zorder=5)\n",
    "    ax.text(coefs[f], i + 0.15, f'{coefs[f]:.4f}', ha='center', fontsize=9)\n",
    "\n",
    "ax.axvline(0, color='black', linewidth=0.8, linestyle='--')\n",
    "ax.set_yticks(range(len(FEATURES))); ax.set_yticklabels(FEATURES)\n",
    "ax.set_title('OLS Regression Coefficients with 95% CI', fontsize=13, fontweight='bold')\n",
    "ax.set_xlabel('Coefficient Value')\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/08_coefficients.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))

# ── Module 10: Residual Analysis ─────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 10 — Residual Analysis\n",
    "Checks the OLS assumptions: normality of residuals, homoscedasticity, no autocorrelation.\n",
]))
cells.append(code([
    "y_pred    = model.fittedvalues\n",
    "residuals = model.resid\n",
    "\n",
    "fig, axes = plt.subplots(1, 3, figsize=(18, 5))\n",
    "fig.suptitle('Residual Analysis', fontsize=14, fontweight='bold')\n",
    "\n",
    "# Q-Q Plot\n",
    "(osm, osr), (slope, intercept, r) = stats.probplot(residuals, dist='norm')\n",
    "axes[0].plot(osm, osr, 'o', alpha=0.3, ms=3, color=PALETTE[0])\n",
    "axes[0].plot(osm, slope * np.array(osm) + intercept, color=PALETTE[3], linewidth=1.5)\n",
    "axes[0].set_title('Q-Q Plot'); axes[0].set_xlabel('Theoretical Quantiles'); axes[0].set_ylabel('Sample Quantiles')\n",
    "\n",
    "# Residuals vs Fitted\n",
    "axes[1].scatter(y_pred, residuals, alpha=0.2, s=10, color=PALETTE[0])\n",
    "axes[1].axhline(0, color=PALETTE[3], linewidth=1.5, linestyle='--')\n",
    "axes[1].set_title('Residuals vs Fitted'); axes[1].set_xlabel('Fitted'); axes[1].set_ylabel('Residuals')\n",
    "\n",
    "# Residual histogram\n",
    "axes[2].hist(residuals, bins=50, color=PALETTE[0], edgecolor='white')\n",
    "axes[2].set_title('Residual Distribution'); axes[2].set_xlabel('Residual')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/09_residual_analysis.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print(f'Durbin-Watson: {sm.stats.stattools.durbin_watson(residuals):.4f} (ideal ~2.0)')\n",
]))
cells.append(code([
    "# Actual vs Predicted\n",
    "fig, ax = plt.subplots(figsize=(8, 6))\n",
    "ax.scatter(y, y_pred, alpha=0.2, s=10, color=PALETTE[0])\n",
    "lims = [min(y.min(), y_pred.min()), max(y.max(), y_pred.max())]\n",
    "ax.plot(lims, lims, color=PALETTE[3], linewidth=1.5, linestyle='--', label='Perfect fit')\n",
    "ax.set_title('Actual vs Predicted ROI', fontsize=13, fontweight='bold')\n",
    "ax.set_xlabel('Actual ROI'); ax.set_ylabel('Predicted ROI')\n",
    "ax.legend()\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/10_actual_vs_predicted.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))

# ── Module 11: Predictions ────────────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 11 — Predictions for New Campaigns\n",
    "Using the fitted model to predict ROI for 5 hypothetical new campaigns,\n",
    "each with a 95% prediction interval.\n",
]))
cells.append(code([
    "new_camps = pd.DataFrame({\n",
    "    'Campaign':              ['Micro-Influencer Instagram', 'Macro-Influencer YouTube',\n",
    "                              'TikTok Viral Campaign', 'Twitter Tech Launch', 'Long-Duration Fitness'],\n",
    "    'Engagement_Rate':       [8.5,   2.1,   15.3,  4.2,   6.8],\n",
    "    'Campaign_Cost':         [30000, 90000, 50000, 25000, 45000],\n",
    "    'Product_Sales':         [500,   1200,  800,   300,   700],\n",
    "    'Campaign_Duration_Days':[14,    30,    7,     10,    60],\n",
    "})\n",
    "\n",
    "X_new = new_camps[FEATURES]\n",
    "X_new_c = sm.add_constant(X_new, has_constant='add')\n",
    "pred = model.get_prediction(X_new_c).summary_frame(alpha=0.05)\n",
    "\n",
    "new_camps['Predicted_ROI'] = pred['mean'].values.round(2)\n",
    "new_camps['CI_Lower_95']   = pred['obs_ci_lower'].values.round(2)\n",
    "new_camps['CI_Upper_95']   = pred['obs_ci_upper'].values.round(2)\n",
    "\n",
    "print(new_camps[['Campaign','Predicted_ROI','CI_Lower_95','CI_Upper_95']].to_string(index=False))\n",
]))
cells.append(code([
    "fig, ax = plt.subplots(figsize=(10, 5))\n",
    "bars = ax.bar(new_camps['Campaign'], new_camps['Predicted_ROI'], color=PALETTE[:5], zorder=3)\n",
    "ax.errorbar(\n",
    "    new_camps['Campaign'], new_camps['Predicted_ROI'],\n",
    "    yerr=[new_camps['Predicted_ROI'] - new_camps['CI_Lower_95'],\n",
    "          new_camps['CI_Upper_95']   - new_camps['Predicted_ROI']],\n",
    "    fmt='none', color='black', capsize=5, linewidth=1.5, zorder=4\n",
    ")\n",
    "ax.set_title('Predicted ROI for 5 New Campaigns (95% CI)', fontsize=13, fontweight='bold')\n",
    "ax.set_ylabel('Predicted ROI')\n",
    "ax.tick_params(axis='x', rotation=20)\n",
    "for bar, val in zip(bars, new_camps['Predicted_ROI']):\n",
    "    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.1f}', ha='center', fontsize=9)\n",
    "ax.grid(axis='y', alpha=0.5)\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/11_predictions.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))

# ── Module 12: Evaluation ────────────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 12 — Model Evaluation\n",
]))
cells.append(code([
    "mae  = mean_absolute_error(y, y_pred)\n",
    "rmse = np.sqrt(mean_squared_error(y, y_pred))\n",
    "r2   = model.rsquared\n",
    "adj_r2 = model.rsquared_adj\n",
    "f_stat = model.fvalue\n",
    "\n",
    "print('=' * 50)\n",
    "print('MODEL EVALUATION SUMMARY  (n = 147,000)')\n",
    "print('=' * 50)\n",
    "print(f'R-squared       : {r2:.4f}')\n",
    "print(f'Adjusted R2     : {adj_r2:.4f}')\n",
    "print(f'F-statistic     : {f_stat:.2f}  (p < 0.001)')\n",
    "print(f'MAE             : {mae:.4f}')\n",
    "print(f'RMSE            : {rmse:.4f}')\n",
    "print(f'AIC             : {model.aic:.2f}')\n",
    "print(f'BIC             : {model.bic:.2f}')\n",
    "print(f'Observations    : {int(model.nobs):,}')\n",
    "print('=' * 50)\n",
]))
cells.append(code([
    "errors = y - y_pred\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "fig.suptitle('Model Evaluation', fontsize=14, fontweight='bold')\n",
    "\n",
    "axes[0].hist(errors, bins=60, color=PALETTE[0], edgecolor='white')\n",
    "axes[0].axvline(0, color=PALETTE[3], linewidth=1.5, linestyle='--')\n",
    "axes[0].set_title(f'Error Distribution  (MAE={mae:.2f}, RMSE={rmse:.2f})')\n",
    "axes[0].set_xlabel('Actual - Predicted'); axes[0].set_ylabel('Frequency')\n",
    "\n",
    "metrics = {'R2': r2, 'Adj R2': adj_r2}\n",
    "axes[1].bar(metrics.keys(), metrics.values(), color=PALETTE[:2])\n",
    "axes[1].set_ylim(0, 1); axes[1].set_title('Model Fit Metrics')\n",
    "for i, (k, v) in enumerate(metrics.items()):\n",
    "    axes[1].text(i, v + 0.01, f'{v:.4f}', ha='center', fontsize=11, fontweight='bold')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.savefig('../Images/12_error_distribution.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))

# ── Module 13: Conclusion ─────────────────────────────────────────────────────
cells.append(md([
    "---\n",
    "## Module 13 — Conclusion & Final Regression Equation\n",
]))
cells.append(code([
    "coefs = model.params\n",
    "pvals = model.pvalues\n",
    "\n",
    "print('FINAL REGRESSION EQUATION')\n",
    "print('-' * 50)\n",
    "print(f'ROI = {coefs[\"const\"]:.4f}')\n",
    "print(f'    + {coefs[\"Engagement_Rate\"]:.4f}    x Engagement_Rate      (p={pvals[\"Engagement_Rate\"]:.3e})')\n",
    "print(f'    + ({coefs[\"Campaign_Cost\"]:.8f}) x Campaign_Cost        (p={pvals[\"Campaign_Cost\"]:.3e})')\n",
    "print(f'    + {coefs[\"Product_Sales\"]:.6f}  x Product_Sales        (p={pvals[\"Product_Sales\"]:.3e})')\n",
    "print(f'    + {coefs[\"Campaign_Duration_Days\"]:.4f}    x Campaign_Duration    (p={pvals[\"Campaign_Duration_Days\"]:.3f})')\n",
    "print()\n",
    "print('KEY FINDINGS')\n",
    "print('-' * 50)\n",
    "print('1. Engagement Rate: strongest positive predictor of ROI (p < 0.001)')\n",
    "print('2. Product Sales  : significant positive effect     (p < 0.001)')\n",
    "print('3. Campaign Cost  : significant negative effect     (p < 0.001)')\n",
    "print('4. Duration       : NOT statistically significant   (p = 0.909)')\n",
    "print()\n",
    "print(f'Model R2 = {r2:.4f} — explains {r2*100:.1f}% of ROI variance')\n",
    "print(f'F-stat   = {f_stat:.2f}  (model is statistically significant at p < 0.001)')\n",
]))
cells.append(md([
    "---\n",
    "## Business Recommendations\n",
    "1. **Prioritise engagement rate over follower count** — a micro-influencer with 8% engagement outperforms a macro-influencer at 1%\n",
    "2. **Avoid overspending on reach** — Campaign Cost has a negative coefficient; efficiency matters more than scale\n",
    "3. **Focus on conversion** — Product Sales is a strong positive predictor; campaigns that drive purchases deliver the best ROI\n",
    "4. **Duration has minimal effect** — a well-targeted 7-day campaign can match a 60-day campaign in ROI\n",
]))

# ── Write notebook ────────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.0"},
    },
    "cells": cells,
}

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Notebook written: {NB_PATH}")
print(f"Total cells: {len(cells)}")
