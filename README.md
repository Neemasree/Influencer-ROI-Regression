# Predictive Statistical Analysis of Influencer Marketing ROI
### Using Multiple Linear Regression (Python + Statsmodels)

---

## Project Overview

This project builds a **statistical regression model** to predict the **Return on Investment (ROI)** of influencer marketing campaigns using a real-world dataset of **150,000 campaigns** spanning Instagram, YouTube, TikTok, and Twitter (2022–2024).

Companies spend millions on influencer marketing without knowing in advance which campaigns will deliver good ROI. This project solves that problem using **Multiple Linear Regression** — a statistical technique that models the relationship between campaign characteristics and ROI.

---

## Problem Statement

> *"Can we predict whether an influencer campaign will give us a good ROI before spending money?"*

Currently, most companies rely on intuition when choosing influencers. This leads to poor investments and wasted budgets. A statistical model that predicts ROI based on measurable campaign features provides a data-driven alternative.

---

## Project Title

**Predictive Statistical Analysis of Influencer Marketing ROI Using Multiple Linear Regression**

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3** | Core programming language |
| **Pandas** | Data loading, cleaning, manipulation |
| **NumPy** | Numerical operations |
| **Matplotlib / Seaborn** | Data visualization |
| **Statsmodels** | Multiple Linear Regression, p-values, R², confidence intervals |
| **SciPy** | Normality tests (Shapiro-Wilk) |
| **Excel (openpyxl)** | Formatted Excel workbook with 4 sheets |
| **Jupyter Notebook** | Interactive project environment |

> No machine learning libraries (TensorFlow, scikit-learn for modeling) or web frameworks were used. This is a pure statistical project using Statsmodels.

---

## Dataset

**Source:** Kaggle — Real-world Influencer Marketing ROI Dataset

| Property | Value |
|----------|-------|
| Rows | 150,000 campaigns |
| Original columns | 10 |
| Engineered columns | 4 |
| Platforms | Instagram, YouTube, TikTok, Twitter |
| Time period | 2022–2024 |

### Original Columns
`campaign_id`, `platform`, `influencer_category`, `campaign_type`, `start_date`, `engagements`, `estimated_reach`, `product_sales`, `campaign_duration_days`, `end_date`

### Engineered Columns

| Column | Formula |
|--------|---------|
| `engagement_rate` | `engagements / estimated_reach × 100` |
| `campaign_cost` | `estimated_reach × CPM / 1000` (CPM varies by platform) |
| `revenue` | `product_sales × avg_unit_value` |
| `roi` | `(revenue − campaign_cost) / campaign_cost` ← **Target Variable** |

**CPM rates used:**
- Instagram: ₹150 | YouTube: ₹120 | TikTok: ₹100 | Twitter: ₹80

---

## Folder Structure

```
Influencer-ROI-Regression/
│
├── Dataset/
│     influencer_marketing_roi_dataset.csv   ← Real Kaggle dataset (150K rows)
│     influencer_marketing.csv               ← Synthetic dataset (200 rows)
│     generate_dataset.py                    ← Script to regenerate synthetic data
│
├── Excel/
│     influencer_marketing.xlsx              ← Formatted workbook (4 sheets)
│     create_excel.py                        ← Script that created the workbook
│
├── Images/
│     01_roi_distribution.png
│     02_platform_analysis.png
│     03_category_analysis.png
│     04_scatter_plots.png
│     05_campaign_type_year.png
│     06_correlation_heatmap.png
│     07_roi_correlation_bar.png
│     08_coefficients.png
│     09_residual_analysis.png
│     10_actual_vs_predicted.png
│     11_predictions.png
│     12_error_distribution.png
│
├── Python/
│     analysis.ipynb                         ← Main project notebook (13 modules)
│     run_analysis.py                        ← Extracts and runs notebook as script
│     verify_pipeline.py                     ← Quick pipeline verification (no graphs)
│
├── Report/                                  ← Project report (PDF)
├── PPT/                                     ← Presentation slides
├── .gitignore
└── README.md
```

---

## Notebook Structure (13 Modules)

| Module | Content |
|--------|---------|
| 1 | Import Libraries |
| 2 | Load Dataset (150,000 rows) |
| 3 | Data Cleaning — missing values, duplicates, invalid rows |
| 4 | Feature Engineering — ROI, Engagement Rate, Campaign Cost, Revenue |
| 5 | Exploratory Data Analysis — 5 chart types |
| 6 | Statistical Analysis — mean, median, std, skewness, normality test |
| 7 | Correlation Analysis — heatmap + bar chart |
| 8 | Multiple Linear Regression (Statsmodels OLS) |
| 9 | Model Interpretation — coefficients, p-values, R², confidence intervals |
| 10 | Residual Analysis — Q-Q plot, homoscedasticity, actual vs predicted |
| 11 | Prediction for New Campaigns (with 95% confidence intervals) |
| 12 | Model Evaluation — MAE, RMSE, error distribution |
| 13 | Conclusion + Final Regression Equation |

---

## Regression Model

**Method:** Ordinary Least Squares (OLS) via Statsmodels

**Features used:**
- `engagement_rate`
- `campaign_cost`
- `product_sales`
- `campaign_duration_days`

**Target:** `roi`

**Regression Equation:**
```
ROI = β₀ + β₁(Engagement_Rate) + β₂(Campaign_Cost) + β₃(Product_Sales) + β₄(Campaign_Duration) + ε
```

### Model Results

| Metric | Value |
|--------|-------|
| R² | 0.4721 |
| Adjusted R² | 0.4720 |
| F-statistic | 3352.43 |
| Prob (F-statistic) | 0.000 |
| Observations | 15,000 (sample) |
| MAE | 2.69 |
| RMSE | 5.73 |

### Key Findings

1. **Engagement Rate** is the strongest positive predictor of ROI (coef = +0.197, p < 0.001)
2. **Product Sales** has a significant positive effect (coef = +0.001, p < 0.001)
3. **Campaign Cost** has a negative effect — higher spend does not guarantee higher ROI (coef = -0.000022, p < 0.001)
4. **Campaign Duration** is not statistically significant (p = 0.16)

---

## Graphs Generated

| # | Graph | Description |
|---|-------|-------------|
| 01 | ROI Distribution | Histogram + KDE of ROI across all campaigns |
| 02 | Platform Analysis | Campaign counts and ROI boxplot by platform |
| 03 | Category Analysis | Average ROI and boxplot by influencer category |
| 04 | Scatter Plots | Engagement Rate vs ROI, Campaign Cost vs ROI |
| 05 | Campaign Type | ROI by campaign type + monthly trend |
| 06 | Correlation Heatmap | Pearson correlations between all numeric features |
| 07 | ROI Correlation Bar | Ranked correlation of each feature with ROI |
| 08 | Coefficients Plot | Regression coefficients with 95% confidence intervals |
| 09 | Residual Analysis | Q-Q plot, residuals vs fitted, homoscedasticity |
| 10 | Actual vs Predicted | Model fit scatter plot |
| 11 | Predictions | Bar chart of predicted ROI for 5 new campaigns |
| 12 | Error Distribution | MAE and prediction error histogram |

---

## Excel Workbook (4 Sheets)

| Sheet | Content |
|-------|---------|
| Dataset | All 200 rows from synthetic dataset, color-coded with conditional formatting |
| Summary Statistics | Mean, median, std, variance, skewness for all numeric variables |
| ROI by Category | ROI breakdown by influencer tier and platform |
| Data Dictionary | Description of every column with data types and roles |

---

## How to Run

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn statsmodels scipy openpyxl scikit-learn
```

### Open the Notebook
```bash
cd Influencer-ROI-Regression
jupyter notebook Python/analysis.ipynb
```
Then: **Kernel → Restart & Run All**

### Quick Verification (no graphs)
```bash
python Python/verify_pipeline.py
```

---

## Business Recommendations

Based on the regression results:

- **Prioritise engagement rate over follower count** — a micro-influencer with 8% engagement outperforms a mega-influencer with 1% engagement
- **Avoid overspending on reach alone** — campaign cost has a negative coefficient; efficiency matters more than scale
- **Focus on conversion** — product sales is a strong positive predictor; campaigns that drive actual purchases deliver the best ROI
- **Campaign duration has minimal effect** — a well-targeted 7-day campaign can match a 60-day campaign in ROI

---

## Limitations

- Feature engineering uses estimated CPM values — actual campaign invoices would give more precise cost data
- Categorical variables (platform, influencer category, campaign type) were used for EDA but not included in regression — one-hot encoding could improve the model
- External factors (seasonality, product category, competitor activity) are not captured in the dataset

---

## Author

**Neema Sree**
Final Year Project — Statistical Analysis and Predictive Modeling
Python + Statsmodels + Excel

---

## License

This project is for academic purposes. Dataset sourced from Kaggle.
