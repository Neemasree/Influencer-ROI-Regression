# Predictive Statistical Analysis of Influencer Marketing ROI
### Using Multiple Linear Regression (Python + Statsmodels)

**Author:** Neema Sree  
**Type:** Final Year Project — Statistical Analysis and Predictive Modelling

---

## Project Overview

This project builds a **multiple linear regression model** to predict the **Return on Investment (ROI)** of influencer marketing campaigns.

The raw data is a publicly available source dataset (150,000 campaigns, Kaggle). The project's contribution is the **data cleaning pipeline**, **feature engineering**, and **statistical analysis** performed on it to produce a final analytical dataset and regression model.

```
RAW DATA (150,000 rows — Kaggle source dataset)
         |
         v  MY DATA CLEANING
         |  Strip whitespace · Parse dates · Remove duplicates
         |  Validate duration · Filter invalid values
         |
         v  MY FEATURE ENGINEERING
         |  Engagement_Rate · Campaign_Cost · Revenue · ROI
         |
         v  MY FINAL PROCESSED DATASET  (147,000 rows × 16 columns)
         |
         v  MY EDA  (12 charts)
         |
         v  MY STATISTICAL ANALYSIS  (descriptive stats · normality test)
         |
         v  MY MULTIPLE LINEAR REGRESSION MODEL  (OLS · Statsmodels)
         |
         v  MY RESULTS  (R²=0.3030 · MAE=135.93 · RMSE=261.47)
```

---

## Problem Statement

> *"Can we predict whether an influencer campaign will give us a good ROI before spending money?"*

Most companies rely on intuition when choosing influencers, leading to wasted budgets. A regression model built on measurable campaign features provides a data-driven alternative.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3** | Core programming language |
| **Pandas** | Data loading, cleaning, manipulation |
| **NumPy** | Numerical operations |
| **Matplotlib / Seaborn** | Data visualisation (12 charts) |
| **Statsmodels** | OLS regression · p-values · R² · confidence intervals |
| **SciPy** | Shapiro-Wilk normality test |
| **scikit-learn** | MAE and RMSE evaluation metrics |
| **Excel (openpyxl)** | Formatted 6-sheet workbook |
| **Jupyter Notebook** | Interactive project environment (13 modules) |

> No ML frameworks used for modelling. Pure statistical approach via Statsmodels OLS.

---

## Dataset

**Source:** Kaggle — Influencer Marketing ROI Dataset (publicly available)

| Property | Value |
|---|---|
| Raw rows | 150,000 |
| Final processed rows | 147,000 |
| Raw columns | 10 |
| Final columns | 16 (10 original + 4 engineered + Year + Month) |
| Platforms | Instagram, YouTube, TikTok, Twitter |

### Raw Columns
`campaign_id`, `platform`, `influencer_category`, `campaign_type`, `start_date`,
`engagements`, `estimated_reach`, `product_sales`, `campaign_duration_days`, `end_date`

### Engineered Columns

| Column | Formula | Notes |
|---|---|---|
| `Engagement_Rate` | `(Engagements / Estimated_Reach) × 100` | % engagement per unit reach |
| `Campaign_Cost` | `(Estimated_Reach × CPM) / 1000` | CPM by platform (see below) |
| `Revenue` | `Product_Sales × Avg_Unit_Value` | Unit value by category (see below) |
| `ROI` | `(Revenue − Campaign_Cost) / Campaign_Cost` | **Target variable** |

**CPM rates (₹):** Instagram = 150 · YouTube = 120 · TikTok = 100 · Twitter = 80

**Avg unit values (₹):** Beauty = 1,500 · Tech = 5,000 · Fashion = 1,200 · Food = 300 · Fitness = 800 · Travel = 3,000 · Gaming = 1,000

### Cleaning Steps Applied
1. Stripped leading/trailing whitespace from string columns
2. Parsed `start_date` and `end_date` to datetime
3. Removed rows with missing values — 0 removed
4. Removed exact duplicate rows — 0 removed
5. Retained only valid platform and category values — 0 removed
6. Removed rows with zero `estimated_reach` — 0 removed
7. Validated `campaign_duration_days` against computed date difference (±2 day tolerance)
8. Capped ROI at 1st–99th percentile to remove extreme outliers — 3,000 removed

---

## Folder Structure

```
Influencer-ROI-Regression/
│
├── data/
│   ├── raw/
│   │   └── influencer_marketing_roi_dataset.csv   ← Original Kaggle dataset (150K rows, unchanged)
│   ├── processed/
│   │   ├── influencer_roi_analysis_dataset.csv    ← Final analytical dataset (147K rows × 16 cols)
│   │   └── regression_metrics.json                ← Saved model metrics and predictions
│   └── process_data.py                            ← Full cleaning + engineering pipeline script
│
├── Python/
│   ├── analysis.ipynb                             ← Main project notebook (13 modules, 41 cells)
│   ├── run_pipeline.py                            ← Run full pipeline, generate all images + metrics
│   └── build_notebook.py                          ← Builds analysis.ipynb programmatically
│
├── Excel/
│   ├── influencer_marketing.xlsx                  ← 6-sheet formatted workbook
│   └── create_excel.py                            ← Script that builds the workbook
│
├── Images/
│   ├── 01_roi_distribution.png
│   ├── 02_platform_analysis.png
│   ├── 03_category_analysis.png
│   ├── 04_scatter_plots.png
│   ├── 05_campaign_type_monthly.png
│   ├── 06_correlation_heatmap.png
│   ├── 07_roi_correlation_bar.png
│   ├── 08_coefficients.png
│   ├── 09_residual_analysis.png
│   ├── 10_actual_vs_predicted.png
│   ├── 11_predictions.png
│   └── 12_error_distribution.png
│
├── archive/                                       ← Old synthetic dataset + legacy scripts (not used)
│   ├── influencer_marketing_synthetic_200rows.csv
│   ├── generate_dataset.py
│   └── ...
│
├── Dataset/                                       ← Legacy folder (kept for reference)
│
├── .gitignore
└── README.md
```

---

## Notebook Structure (13 Modules)

| Module | Content |
|---|---|
| 1 | Import Libraries |
| 2 | Load Raw Dataset — profile shape, columns, missing values |
| 3 | Data Cleaning — 8 steps documented |
| 4 | Feature Engineering — 4 engineered variables with formulas |
| 5 | Final Processed Dataset — select, rename, validate 16 columns |
| 6 | EDA — 5 chart sets (ROI distribution, platform, category, scatter, trends) |
| 7 | Statistical Analysis — descriptive stats, skewness, normality test |
| 8 | Correlation Analysis — heatmap + ROI correlation bar chart |
| 9 | Multiple Linear Regression — OLS model fitted on all 147,000 observations, full summary, coefficient plot |
| 10 | Residual Analysis — Q-Q plot, residuals vs fitted, actual vs predicted |
| 11 | Predictions — 5 new campaigns with 95% prediction intervals |
| 12 | Model Evaluation — MAE, RMSE, error distribution |
| 13 | Conclusion — final equation, key findings, business recommendations |

---

## Excel Workbook (6 Sheets)

| Sheet | Content |
|---|---|
| Processed_Dataset | First 5,000 rows of the analytical dataset with conditional ROI formatting |
| Summary_Statistics | Descriptive stats (count, mean, std, min/max, skewness, kurtosis) for all numeric columns |
| Correlation_Analysis | Full Pearson correlation matrix + ROI correlation summary table |
| Regression_Results | Model fit metrics, coefficient table with p-values and CIs, final equation — fitted on all 147,000 observations |
| Predictions | 5 new campaign predictions with 95% prediction intervals |
| Data_Dictionary | Every column defined — source (raw vs engineered), formula, example value |

---

## Regression Model

**Method:** Ordinary Least Squares (OLS) — Statsmodels  
**Observations:** All 147,000 rows of the processed dataset (no sampling)  
**Features:** `Engagement_Rate`, `Campaign_Cost`, `Product_Sales`, `Campaign_Duration_Days`  
**Target:** `ROI`

### Final Regression Equation

```
ROI = 161.8977
    + 1.0914  × Engagement_Rate
    − 0.00286 × Campaign_Cost
    + 0.0567  × Product_Sales
    − 0.0088  × Campaign_Duration_Days
```

### Model Results

| Metric | Value |
|---|---|
| R² | 0.3190 |
| Adjusted R² | 0.3190 |
| F-statistic | 17,218.03 |
| Prob (F-statistic) | < 0.001 |
| Observations | 147,000 |
| MAE | 139.42 |
| RMSE | 267.18 |
| AIC | 2,060,022.5 |
| BIC | 2,060,071.9 |

### Key Findings

| Feature | Coefficient | p-value | Significant? |
|---|---|---|---|
| Engagement_Rate | +1.0914 | < 0.001 | Yes *** |
| Campaign_Cost | −0.00286 | < 0.001 | Yes *** |
| Product_Sales | +0.0567 | < 0.001 | Yes *** |
| Campaign_Duration_Days | −0.0088 | 0.916 | **No** |

1. **Engagement Rate** is the strongest positive predictor — higher engagement per unit reach drives ROI up
2. **Product Sales** has a significant positive effect — campaigns that convert to actual purchases deliver better returns
3. **Campaign Cost** has a significant negative effect — spending more on reach alone does not guarantee higher ROI
4. **Campaign Duration** is not statistically significant (p = 0.909)

---

## Charts Generated

| # | Chart | Description |
|---|---|---|
| 01 | ROI Distribution | Histogram + cumulative distribution of ROI |
| 02 | Platform Analysis | Campaign counts + ROI boxplot by platform |
| 03 | Category Analysis | Average ROI + spread by influencer category |
| 04 | Scatter Plots | Engagement Rate vs ROI · Campaign Cost vs ROI |
| 05 | Campaign Type & Monthly | ROI by campaign type + monthly trend |
| 06 | Correlation Heatmap | Pearson correlations between all numeric features |
| 07 | ROI Correlation Bar | Features ranked by correlation with ROI |
| 08 | Coefficients Plot | OLS coefficients with 95% confidence intervals |
| 09 | Residual Analysis | Q-Q plot · residuals vs fitted · residual histogram |
| 10 | Actual vs Predicted | Model fit scatter plot |
| 11 | Predictions | Bar chart with 95% PI for 5 new campaigns |
| 12 | Error Distribution | MAE/RMSE · prediction error histogram |

---

## How to Run

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn statsmodels scipy openpyxl scikit-learn
```

### Step 1 — Generate the processed dataset
```bash
python data/process_data.py
```

### Step 2 — Run the full analysis pipeline (generates all images + metrics JSON)
```bash
python Python/run_pipeline.py
```

### Step 3 — Open the notebook
```bash
jupyter notebook Python/analysis.ipynb
```
Then: **Kernel → Restart & Run All**

### Rebuild the Excel workbook
```bash
python Excel/create_excel.py
```

### Rebuild the notebook programmatically
```bash
python Python/build_notebook.py
```

---

## Business Recommendations

Based on the regression results:

- **Prioritise engagement rate over follower count** — a micro-influencer with 8% engagement outperforms a mega-influencer with 1% engagement
- **Avoid overspending on reach** — campaign cost has a negative coefficient; efficiency matters more than scale
- **Focus on conversion** — product sales is a strong positive predictor; campaigns that drive actual purchases deliver the best ROI
- **Campaign duration has minimal effect** — a well-targeted 7-day campaign can match a 60-day campaign in ROI

---

## Limitations

- CPM and average unit value figures are estimated; actual invoice data would improve cost precision
- Categorical variables (platform, category, campaign type) used in EDA but not in regression — one-hot encoding could improve R²
- ROI outliers capped at 1st–99th percentile; the full distribution is right-skewed (skewness = 5.1)
- R² of 0.30 indicates the four numeric features explain 30% of ROI variance; unobserved factors (seasonality, brand strength, creative quality) account for the rest

---

## Data Source Note

The raw dataset (`data/raw/influencer_marketing_roi_dataset.csv`) is a **publicly available source dataset** obtained from Kaggle. It was not collected by the author. The project's analytical contribution is the cleaning pipeline, feature engineering, and statistical modelling applied to derive the final processed dataset and regression results.

---

## License

Academic project. Raw dataset sourced from Kaggle (publicly available).
