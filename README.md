# Predictive Statistical Analysis of Influencer Marketing ROI
### Using Multiple Linear Regression — Python + Statsmodels

**Author:** Neema Sree  
**Type:** Final Year Academic Project — Statistical Analysis and Predictive Modelling

---

## Project Overview

This project builds a multiple linear regression model to predict the Return on Investment (ROI) of influencer marketing campaigns.

The raw data is a publicly available dataset from Kaggle (150,000 campaigns). The project's contribution is the **data cleaning pipeline**, **feature engineering**, and **statistical modelling** applied to it.

> **Transparency note:** `Campaign_Cost`, `Revenue`, and `ROI` are **derived variables** calculated by this project's feature engineering. They were **not** provided by the original Kaggle dataset.

---

## Problem Statement

> *"Can we predict whether an influencer marketing campaign will deliver good ROI before spending money?"*

Most budget allocation decisions rely on follower count and intuition. This project builds a data-driven regression model using measurable campaign characteristics to predict ROI.

---

## Aim and Objectives

**Aim:** Build a statistically sound multiple linear regression model to predict influencer campaign ROI.

**Objectives:**
1. Load, inspect, and clean the raw Kaggle dataset
2. Engineer the key financial variables (Engagement Rate, Campaign Cost, Revenue, ROI)
3. Perform exploratory data analysis and descriptive statistics
4. Analyse feature correlations and identify predictors of ROI
5. Build and interpret an OLS regression model using Statsmodels
6. Diagnose model assumptions and evaluate model performance
7. Generate ROI predictions with confidence intervals for new campaigns

---

## Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.x | Core programming language |
| Pandas | 2.x | Data loading, cleaning, manipulation |
| NumPy | 1.26+ | Numerical operations |
| Matplotlib + Seaborn | 3.7+ | Data visualisation (16 charts) |
| Statsmodels | 0.14+ | OLS regression, p-values, R2, CIs |
| SciPy | 1.10+ | Shapiro-Wilk normality test |
| scikit-learn | 1.2+ | MAE and RMSE evaluation metrics only |
| openpyxl | 3.1+ | Excel workbook generation |
| Jupyter | 1.0+ | Interactive notebook environment |

> No machine learning frameworks, web frameworks, databases, or frontend technologies are used.

---

## Dataset

**Source:** Publicly available Influencer Marketing ROI dataset — Kaggle  
**Note:** The raw dataset was not collected by the author. It is a publicly available source dataset.

| Property | Value |
|---|---|
| Raw rows | 150,000 |
| Final processed rows | **147,000** |
| Rows removed in cleaning | 3,000 (ROI outlier capping) |
| Raw columns | 10 |
| Final columns | **16** (10 original + 4 engineered + Year + Month) |
| Platforms | Instagram, YouTube, TikTok, Twitter |
| Categories | Beauty, Tech, Fashion, Food, Fitness, Travel, Gaming |

---

## Feature Engineering Methodology

These four variables are **not present in the raw dataset**. They are calculated by this project.

### Engagement Rate
```
Engagement_Rate = (Engagements / Estimated_Reach) × 100
```
Measures how effectively the audience interacted with the campaign. Unit: %.

### Campaign Cost
```
Campaign_Cost = (Estimated_Reach × Platform_CPM) / 1000
```
Estimated cost of the campaign based on a CPM (cost-per-thousand impressions) model. Unit: INR.

**CPM assumptions:**
| Platform | CPM (INR) |
|---|---|
| Instagram | 150 |
| YouTube | 120 |
| TikTok | 100 |
| Twitter | 80 |

### Revenue
```
Revenue = Product_Sales × Category_Avg_Unit_Value
```
Estimated revenue attributed to the campaign. Unit: INR.

**Average unit value assumptions:**
| Category | Value (INR) |
|---|---|
| Beauty | 1,500 |
| Tech | 5,000 |
| Fashion | 1,200 |
| Food | 300 |
| Fitness | 800 |
| Travel | 3,000 |
| Gaming | 1,000 |

### ROI (Target Variable)
```
ROI = (Revenue − Campaign_Cost) / Campaign_Cost
```
Dimensionless ratio. Capped at 1st–99th percentile to remove extreme outliers.

---

## Statistical Methodology

- Descriptive statistics: mean, median, mode, std dev, variance, min, max, skewness, kurtosis
- Normality testing: Shapiro-Wilk test (sample n=5,000; full dataset too large for Shapiro-Wilk)
- Correlation: Pearson correlation matrix and heatmap
- Regression: Ordinary Least Squares (OLS) via Statsmodels

---

## Regression Methodology

**Algorithm:** Ordinary Least Squares (OLS) — `statsmodels.api.OLS`  
**Observations:** All **147,000** processed rows (no random sampling)  
**Target:** ROI  
**Predictors:** Engagement_Rate, Campaign_Cost, Product_Sales, Campaign_Duration_Days  
**Constant:** Added via `sm.add_constant()`

---

## Final Model Results

### Regression Equation
```
ROI = 161.8977
    + 1.0914  × Engagement_Rate
    − 0.00286 × Campaign_Cost
    + 0.0567  × Product_Sales
    − 0.0088  × Campaign_Duration_Days
```

### Model Metrics

| Metric | Value |
|---|---|
| R-squared (R2) | **0.3190** |
| Adjusted R2 | **0.3190** |
| F-statistic | **17,218.03** (p < 0.001) |
| MAE | **139.42** |
| RMSE | **267.18** |
| AIC | 2,060,022.5 |
| BIC | 2,060,071.9 |
| Observations | **147,000** |

### Coefficients

| Predictor | Coefficient | p-value | Significant? |
|---|---|---|---|
| Engagement_Rate | +1.0914 | < 0.001 | Yes *** |
| Campaign_Cost | −0.00286 | < 0.001 | Yes *** |
| Product_Sales | +0.0567 | < 0.001 | Yes *** |
| Campaign_Duration_Days | −0.0088 | 0.916 | **No** |

---

## Key Findings

1. **Engagement Rate** is the strongest positive predictor — higher engagement per unit reach drives ROI up
2. **Product Sales** has a significant positive effect — campaigns that convert to purchases deliver better ROI
3. **Campaign Cost** has a significant negative effect — spending more on reach alone reduces ROI
4. **Campaign Duration** is not statistically significant — duration alone does not predict ROI

> These are statistical associations, not causal claims.

---

## Project Structure

```
Influencer-ROI-Regression/
│
├── data/
│   ├── raw/
│   │   └── influencer_marketing_roi_dataset.csv   <- Original Kaggle dataset (150,000 rows, UNCHANGED)
│   └── processed/
│       └── influencer_roi_analysis_dataset.csv    <- Final analytical dataset (147,000 rows x 16 cols)
│
├── notebooks/
│   ├── analysis.ipynb                             <- Main project notebook (14 modules, 55 cells)
│   └── build_notebook.py                          <- Script that generates analysis.ipynb
│
├── src/
│   ├── __init__.py
│   ├── process_data.py    <- Data cleaning and feature engineering pipeline
│   ├── statistics.py      <- Descriptive stats and normality testing
│   ├── regression.py      <- OLS model fitting, saving, loading
│   ├── visualization.py   <- All 16 charts
│   ├── evaluation.py      <- MAE, RMSE, prediction utilities
│   └── predict_roi.py     <- Predict ROI for new campaigns
│
├── outputs/
│   ├── figures/           <- 16 PNG charts
│   ├── predictions/
│   │   └── new_campaign_predictions.csv
│   ├── regression_metrics.json
│   └── ols_model.pkl      <- Saved fitted OLS model
│
├── excel/
│   └── influencer_marketing.xlsx  <- 6-sheet formatted workbook
│
├── archive/
│   └── old_synthetic_dataset/     <- LEGACY / UNUSED — 200-row synthetic data (not part of final project)
│
├── run_pipeline.py        <- Master script — runs complete pipeline end-to-end
├── requirements.txt       <- Python package dependencies
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels openpyxl scikit-learn jupyter
```

---

## How to Run

### Option 1 — Run complete pipeline (recommended)
```bash
python run_pipeline.py
```
This runs all 8 steps: data processing → statistics → EDA charts → regression → evaluation → predictions → regression charts → Excel workbook.

### Option 2 — Open the notebook
```bash
jupyter notebook notebooks/analysis.ipynb
```
Then: **Kernel → Restart & Run All**

### Option 3 — Run individual modules
```bash
# Data processing only
python src/process_data.py

# Predict ROI for a new campaign (interactive)
python src/predict_roi.py
```

---

## How to Run the Prediction Module

```bash
python src/predict_roi.py
```

You will be prompted to enter:
- Platform (Instagram / YouTube / TikTok / Twitter)
- Influencer Category (Beauty / Tech / Fashion / Food / Fitness / Travel / Gaming)
- Campaign Type (Brand Awareness / Product Launch / Giveaway / Seasonal Sale / Event Promotion)
- Estimated Reach
- Engagements
- Product Sales
- Campaign Duration (days)

The tool computes Engagement Rate, Campaign Cost, and Revenue using **the same formulas used during training**, then outputs:
- Predicted ROI
- 95% Prediction Interval

**Example output:**
```
===========================================================
  CAMPAIGN ROI PREDICTION
===========================================================
  Platform             : Instagram
  Influencer Category  : Beauty
  Campaign Type        : Product Launch
  Estimated Reach      : 500,000
  Engagements          : 42,500
  Product Sales        : 800
  Duration (days)      : 14
-----------------------------------------------------------
  COMPUTED FEATURES (same as training pipeline)
  Engagement Rate      : 8.5000 %
  Campaign Cost (INR)  : 75,000.00
  Revenue (INR)        : 1,200,000.00
-----------------------------------------------------------
  PREDICTED ROI        : 13.8472
  95% Prediction Interval: [-8.7412, 36.4356]
===========================================================
```

---

## Limitations

- R2 = 0.319 — the model explains ~32% of ROI variance; unobserved factors (creative quality, brand reputation, competitor activity) account for the rest
- CPM and average unit values are estimated assumptions, not actual invoice data
- Categorical variables used in EDA but not in regression — one-hot encoding could improve R2
- ROI is right-skewed; normality of residuals is not achieved (noted in diagnostics), but OLS is robust at n=147,000 due to the Central Limit Theorem

---

## Future Scope

- Include one-hot encoded categorical features (Platform, Category, Campaign Type) in regression
- Try log transformation of ROI to reduce skewness
- Explore polynomial or interaction terms
- Use actual campaign invoice data for more accurate cost estimates
- Apply regularised regression (Ridge/Lasso) to compare with OLS

---

## Data Source Note

The raw dataset (`data/raw/influencer_marketing_roi_dataset.csv`) is a **publicly available dataset** sourced from Kaggle. It was **not collected or fabricated by the author**. The project's analytical contribution consists of:
1. The data cleaning pipeline
2. The feature engineering (Engagement Rate, Campaign Cost, Revenue, ROI)
3. The exploratory and statistical analysis
4. The OLS regression model and interpretation

---

## License

Academic project. Raw dataset sourced from Kaggle (publicly available).
