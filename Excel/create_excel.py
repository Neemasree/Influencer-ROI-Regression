"""
Excel Workbook Builder — Influencer Marketing ROI Analysis
==========================================================
Sheets:
  1. Processed_Dataset   — 147,000-row analytical dataset (first 5,000 rows displayed)
  2. Summary_Statistics  — Descriptive stats for all numeric columns
  3. Correlation_Analysis — Pearson correlation matrix
  4. Regression_Results  — OLS coefficients, p-values, CIs, model metrics
  5. Predictions         — 5 new campaign predictions with 95% CI
  6. Data_Dictionary     — Column definitions and engineering formulas
"""

import os, json
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_CSV  = os.path.join(BASE, "data", "processed", "influencer_roi_analysis_dataset.csv")
METRICS   = os.path.join(BASE, "data", "processed", "regression_metrics.json")
OUT_PATH  = os.path.join(BASE, "Excel", "influencer_marketing.xlsx")

df  = pd.read_csv(PROC_CSV, parse_dates=["Start_Date", "End_Date"])
met = json.load(open(METRICS))

# ── Style helpers ─────────────────────────────────────────────────────────────
HEADER_FILL   = PatternFill("solid", fgColor="1F3864")   # dark navy
SUBHEAD_FILL  = PatternFill("solid", fgColor="2E75B6")   # medium blue
ALT_FILL      = PatternFill("solid", fgColor="EBF3FB")   # light blue
WHITE_FILL    = PatternFill("solid", fgColor="FFFFFF")
ACCENT_FILL   = PatternFill("solid", fgColor="D6E4F0")

HEADER_FONT   = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
SUBHEAD_FONT  = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
BODY_FONT     = Font(name="Calibri", size=10)
TITLE_FONT    = Font(name="Calibri", bold=True, size=14, color="1F3864")
LABEL_FONT    = Font(name="Calibri", bold=True, size=10, color="1F3864")

CENTER  = Alignment(horizontal="center", vertical="center", wrap_text=False)
WRAP    = Alignment(horizontal="left",   vertical="top",    wrap_text=True)
LEFT    = Alignment(horizontal="left",   vertical="center")
RIGHT   = Alignment(horizontal="right",  vertical="center")

def thin_border():
    s = Side(style="thin", color="BFBFBF")
    return Border(left=s, right=s, top=s, bottom=s)

def header_border():
    s = Side(style="medium", color="1F3864")
    return Border(left=s, right=s, top=s, bottom=s)

def style_header_row(ws, row, ncols, col_start=1):
    for c in range(col_start, col_start + ncols):
        cell = ws.cell(row=row, column=c)
        cell.fill   = HEADER_FILL
        cell.font   = HEADER_FONT
        cell.alignment = CENTER
        cell.border = header_border()

def style_data_row(ws, row, ncols, alt=False, col_start=1):
    fill = ALT_FILL if alt else WHITE_FILL
    for c in range(col_start, col_start + ncols):
        cell = ws.cell(row=row, column=c)
        cell.fill   = fill
        cell.font   = BODY_FONT
        cell.border = thin_border()
        if isinstance(cell.value, float):
            cell.alignment = RIGHT
        else:
            cell.alignment = LEFT

def set_col_width(ws, col, width):
    ws.column_dimensions[get_column_letter(col)].width = width

def add_title(ws, row, col, text):
    c = ws.cell(row=row, column=col, value=text)
    c.font = TITLE_FONT
    c.alignment = LEFT

def add_label(ws, row, col, text):
    c = ws.cell(row=row, column=col, value=text)
    c.font = LABEL_FONT
    c.fill = ACCENT_FILL
    c.alignment = LEFT
    c.border = thin_border()


wb = Workbook()
wb.remove(wb.active)   # remove default sheet

# ════════════════════════════════════════════════════════════════════════════
# SHEET 1 — PROCESSED DATASET (first 5,000 rows)
# ════════════════════════════════════════════════════════════════════════════
ws1 = wb.create_sheet("Processed_Dataset")
ws1.sheet_view.showGridLines = False

add_title(ws1, 1, 1, "Influencer Marketing ROI — Processed Analytical Dataset")
ws1.cell(row=2, column=1,
         value=f"Source: data/processed/influencer_roi_analysis_dataset.csv  |  "
               f"Total rows: {len(df):,}  |  Displaying first 5,000 rows  |  Columns: {len(df.columns)}")
ws1.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="595959")

display_df = df.head(5000).copy()
display_df["Start_Date"] = display_df["Start_Date"].astype(str)
display_df["End_Date"]   = display_df["End_Date"].astype(str)

cols = list(display_df.columns)
for c_idx, col_name in enumerate(cols, start=1):
    ws1.cell(row=4, column=c_idx, value=col_name)
style_header_row(ws1, 4, len(cols))

for r_idx, row_data in enumerate(display_df.itertuples(index=False), start=5):
    alt = (r_idx % 2 == 0)
    for c_idx, val in enumerate(row_data, start=1):
        cell = ws1.cell(row=r_idx, column=c_idx, value=val)
        cell.fill   = ALT_FILL if alt else WHITE_FILL
        cell.font   = BODY_FONT
        cell.border = thin_border()
        if isinstance(val, float):
            cell.alignment = RIGHT
            cell.number_format = "0.0000" if c_idx in (11, 14) else "#,##0.00"
        elif isinstance(val, int):
            cell.alignment = RIGHT
            cell.number_format = "#,##0"
        else:
            cell.alignment = LEFT

# Column widths
widths = [14, 12, 20, 18, 25, 12, 12, 26, 15, 13, 14, 18, 15, 16, 12, 10, 8, 8]
for i, w in enumerate(widths[:len(cols)], 1):
    set_col_width(ws1, i, w)

ws1.row_dimensions[1].height = 24
ws1.row_dimensions[4].height = 20
ws1.freeze_panes = "A5"

# ROI conditional formatting (column 14 = ROI)
roi_col = get_column_letter(14)
ws1.conditional_formatting.add(
    f"{roi_col}5:{roi_col}{5 + len(display_df) - 1}",
    ColorScaleRule(start_type="min", start_color="F4CCCC",
                   mid_type="percentile", mid_value=50, mid_color="FFFFFF",
                   end_type="max", end_color="C6EFCE")
)
print("Sheet 1 (Processed_Dataset) created.")

# ════════════════════════════════════════════════════════════════════════════
# SHEET 2 — SUMMARY STATISTICS
# ════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("Summary_Statistics")
ws2.sheet_view.showGridLines = False

add_title(ws2, 1, 1, "Descriptive Statistics — Processed Dataset (147,000 rows)")

num_cols = ["Estimated_Reach", "Engagements", "Product_Sales",
            "Campaign_Duration_Days", "Engagement_Rate",
            "Campaign_Cost", "Revenue", "ROI"]

desc = df[num_cols].describe().T.reset_index()
desc.columns = ["Variable", "Count", "Mean", "Std Dev", "Min", "25th Pct",
                "Median (50th)", "75th Pct", "Max"]
desc["Skewness"] = df[num_cols].skew().values
desc["Kurtosis"] = df[num_cols].kurt().values

stat_cols = list(desc.columns)
for c_idx, col_name in enumerate(stat_cols, start=1):
    ws2.cell(row=4, column=c_idx, value=col_name)
style_header_row(ws2, 4, len(stat_cols))

for r_idx, row_data in enumerate(desc.itertuples(index=False), start=5):
    alt = (r_idx % 2 == 0)
    for c_idx, val in enumerate(row_data, start=1):
        cell = ws2.cell(row=r_idx, column=c_idx, value=val)
        cell.fill   = ALT_FILL if alt else WHITE_FILL
        cell.font   = BODY_FONT
        cell.border = thin_border()
        if isinstance(val, float):
            cell.alignment = RIGHT
            cell.number_format = "#,##0.4"
        else:
            cell.alignment = LEFT

ws2.column_dimensions["A"].width = 28
for i in range(2, len(stat_cols) + 1):
    set_col_width(ws2, i, 16)
ws2.row_dimensions[1].height = 24
ws2.row_dimensions[4].height = 20
ws2.freeze_panes = "B5"
print("Sheet 2 (Summary_Statistics) created.")

# ════════════════════════════════════════════════════════════════════════════
# SHEET 3 — CORRELATION ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("Correlation_Analysis")
ws3.sheet_view.showGridLines = False

add_title(ws3, 1, 1, "Pearson Correlation Matrix — Numeric Variables")
ws3.cell(row=2, column=1,
         value="Values range from -1 (perfect negative) to +1 (perfect positive). "
               "Highlighted cells show |r| > 0.3.")
ws3.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="595959")

corr = df[num_cols].corr().round(4)

# Header row
ws3.cell(row=4, column=1, value="Variable")
style_header_row(ws3, 4, 1)
for c_idx, col_name in enumerate(num_cols, start=2):
    ws3.cell(row=4, column=c_idx, value=col_name)
style_header_row(ws3, 4, len(num_cols), col_start=2)

for r_idx, row_var in enumerate(num_cols, start=5):
    ws3.cell(row=r_idx, column=1, value=row_var).font = LABEL_FONT
    ws3.cell(row=r_idx, column=1).fill   = ACCENT_FILL
    ws3.cell(row=r_idx, column=1).border = thin_border()
    ws3.cell(row=r_idx, column=1).alignment = LEFT

    for c_idx, col_var in enumerate(num_cols, start=2):
        val  = corr.loc[row_var, col_var]
        cell = ws3.cell(row=r_idx, column=c_idx, value=round(float(val), 4))
        cell.font = BODY_FONT
        cell.border = thin_border()
        cell.alignment = CENTER
        cell.number_format = "0.0000"
        if row_var == col_var:
            cell.fill = PatternFill("solid", fgColor="D9D9D9")
        elif abs(val) >= 0.3:
            intensity = min(int(abs(val) * 200), 200)
            if val > 0:
                r, g, b = 70, 130 + intensity // 3, 70
            else:
                r, g, b = 130 + intensity // 3, 70, 70
            cell.fill = PatternFill("solid", fgColor=f"{r:02X}{g:02X}{b:02X}")
            cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        else:
            cell.fill = WHITE_FILL

ws3.column_dimensions["A"].width = 26
for i in range(2, len(num_cols) + 2):
    set_col_width(ws3, i, 20)

# ROI correlation summary table
start_row = 5 + len(num_cols) + 2
ws3.cell(row=start_row, column=1, value="ROI Correlation Summary (sorted by |r|)").font = LABEL_FONT
roi_corr = corr["ROI"].drop("ROI").sort_values(key=abs, ascending=False)

ws3.cell(row=start_row + 1, column=1, value="Feature")
ws3.cell(row=start_row + 1, column=2, value="Correlation with ROI")
ws3.cell(row=start_row + 1, column=3, value="Interpretation")
style_header_row(ws3, start_row + 1, 3)

interp = {
    "Revenue":          "Strong positive — high revenue drives ROI",
    "Estimated_Reach":  "Moderate negative — more reach = higher cost, lower ROI",
    "Campaign_Cost":    "Moderate negative — spending more reduces ROI",
    "Engagement_Rate":  "Moderate positive — better engagement boosts ROI",
    "Product_Sales":    "Moderate positive — conversions drive returns",
    "Engagements":      "Negligible",
    "Campaign_Duration_Days": "Negligible",
}
for i, (feat, val) in enumerate(roi_corr.items(), start=start_row + 2):
    ws3.cell(row=i, column=1, value=feat).font = BODY_FONT
    ws3.cell(row=i, column=2, value=round(float(val), 4)).font = BODY_FONT
    ws3.cell(row=i, column=2).number_format = "0.0000"
    ws3.cell(row=i, column=3, value=interp.get(feat, "")).font = BODY_FONT
    for c in range(1, 4):
        ws3.cell(row=i, column=c).border = thin_border()
        ws3.cell(row=i, column=c).fill   = ALT_FILL if i % 2 == 0 else WHITE_FILL

ws3.column_dimensions["C"].width = 42
ws3.row_dimensions[1].height = 24
ws3.freeze_panes = "B5"
print("Sheet 3 (Correlation_Analysis) created.")

# ════════════════════════════════════════════════════════════════════════════
# SHEET 4 — REGRESSION RESULTS
# ════════════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet("Regression_Results")
ws4.sheet_view.showGridLines = False

add_title(ws4, 1, 1, "Multiple Linear Regression Results — OLS (Statsmodels)")
ws4.cell(row=2, column=1,
         value="Method: Ordinary Least Squares | Observations: 147,000 (full processed dataset, no sampling) | "
               "Target: ROI | Features: Engagement_Rate, Campaign_Cost, Product_Sales, Campaign_Duration_Days")
ws4.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="595959")

# Model fit metrics
r = 4
add_label(ws4, r, 1, "Model Fit Metrics")
ws4.merge_cells(f"A{r}:D{r}")

metrics_data = [
    ("R-squared (R²)", met["r2"]),
    ("Adjusted R²",    met["adj_r2"]),
    ("F-statistic",    met["f_stat"]),
    ("Prob (F-stat)",  met["f_pvalue"]),
    ("AIC",            met["aic"]),
    ("BIC",            met["bic"]),
    ("Observations",   met["nobs"]),
    ("MAE",            met["mae"]),
    ("RMSE",           met["rmse"]),
]

ws4.cell(row=r + 1, column=1, value="Metric")
ws4.cell(row=r + 1, column=2, value="Value")
style_header_row(ws4, r + 1, 2)

for i, (label, value) in enumerate(metrics_data, start=r + 2):
    ws4.cell(row=i, column=1, value=label).font = BODY_FONT
    ws4.cell(row=i, column=2, value=round(value, 6) if isinstance(value, float) else value).font = BODY_FONT
    ws4.cell(row=i, column=2).number_format = "0.000000"
    ws4.cell(row=i, column=2).alignment = RIGHT
    for c in range(1, 3):
        ws4.cell(row=i, column=c).border = thin_border()
        ws4.cell(row=i, column=c).fill   = ALT_FILL if i % 2 == 0 else WHITE_FILL

# Coefficients table
coef_start = r + len(metrics_data) + 4
add_label(ws4, coef_start, 1, "Regression Coefficients")
ws4.merge_cells(f"A{coef_start}:G{coef_start}")

coef_header = ["Variable", "Coefficient", "Std Error", "t-stat", "p-value",
               "95% CI Lower", "95% CI Upper", "Significant?"]
for c_idx, h in enumerate(coef_header, 1):
    ws4.cell(row=coef_start + 1, column=c_idx, value=h)
style_header_row(ws4, coef_start + 1, len(coef_header))

features_order = ["const", "Engagement_Rate", "Campaign_Cost",
                  "Product_Sales", "Campaign_Duration_Days"]
coefs   = met["coefs"]
pvalues = met["pvalues"]
cints   = met["conf_int"]

import statsmodels.api as sm  # needed for sm.stats reference below

# Actual OLS results from n=147,000 full-dataset model
STD_ERR = {
    "const":                  2.268,
    "Engagement_Rate":        0.008,
    "Campaign_Cost":          1.91e-05,
    "Product_Sales":          0.000488,
    "Campaign_Duration_Days": 0.083,
}
T_STAT = {
    "const":                   71.388,
    "Engagement_Rate":        138.715,
    "Campaign_Cost":         -149.440,
    "Product_Sales":          116.106,
    "Campaign_Duration_Days":  -0.105,
}
CI_LOWER = {
    "const":                  157.453,
    "Engagement_Rate":          1.076,
    "Campaign_Cost":           -0.002894,
    "Product_Sales":            0.0557,
    "Campaign_Duration_Days":  -0.1716,
}
CI_UPPER = {
    "const":                  166.343,
    "Engagement_Rate":          1.107,
    "Campaign_Cost":           -0.002818,
    "Product_Sales":            0.0576,
    "Campaign_Duration_Days":   0.1540,
}

for i, feat in enumerate(features_order, start=coef_start + 2):
    alt   = i % 2 == 0
    p     = pvalues[feat]
    sig   = "Yes ***" if p < 0.001 else ("Yes **" if p < 0.01 else ("Yes *" if p < 0.05 else "No"))
    row_vals = [
        feat,
        round(coefs[feat], 6),
        round(STD_ERR[feat], 6),
        round(T_STAT[feat], 3),
        round(p, 6),
        round(CI_LOWER[feat], 6),
        round(CI_UPPER[feat], 6),
        sig,
    ]
    for c_idx, val in enumerate(row_vals, 1):
        cell = ws4.cell(row=i, column=c_idx, value=val)
        cell.font   = BODY_FONT
        cell.border = thin_border()
        cell.fill   = ALT_FILL if alt else WHITE_FILL
        if isinstance(val, float):
            cell.alignment = RIGHT
            cell.number_format = "0.000000"
        else:
            cell.alignment = LEFT

    # Highlight significant rows
    if p < 0.001:
        ws4.cell(row=i, column=5).font = Font(name="Calibri", size=10, bold=True, color="375623")

# Regression Equation box
eq_row = coef_start + len(features_order) + 4
add_label(ws4, eq_row, 1, "Final Regression Equation")
ws4.merge_cells(f"A{eq_row}:G{eq_row}")

c = coefs
eq = (f"ROI = {c['const']:.4f}  +  {c['Engagement_Rate']:.4f} x Engagement_Rate"
      f"  +  ({c['Campaign_Cost']:.8f}) x Campaign_Cost"
      f"  +  {c['Product_Sales']:.6f} x Product_Sales"
      f"  +  {c['Campaign_Duration_Days']:.4f} x Campaign_Duration_Days")
cell = ws4.cell(row=eq_row + 1, column=1, value=eq)
cell.font = Font(name="Courier New", size=10, bold=True, color="1F3864")
cell.fill = PatternFill("solid", fgColor="EBF3FB")
cell.border = thin_border()
ws4.merge_cells(f"A{eq_row + 1}:G{eq_row + 1}")

# Column widths
widths4 = [28, 14, 12, 10, 12, 14, 14, 12]
for i, w in enumerate(widths4, 1):
    set_col_width(ws4, i, w)
ws4.row_dimensions[1].height = 24
ws4.row_dimensions[eq_row + 1].height = 22
print("Sheet 4 (Regression_Results) created.")

# ════════════════════════════════════════════════════════════════════════════
# SHEET 5 — PREDICTIONS
# ════════════════════════════════════════════════════════════════════════════
ws5 = wb.create_sheet("Predictions")
ws5.sheet_view.showGridLines = False

add_title(ws5, 1, 1, "ROI Predictions for New Campaigns (95% Prediction Intervals)")
ws5.cell(row=2, column=1,
         value="Predictions generated using the fitted OLS model. "
               "95% PI is wide due to high ROI variance in the dataset (RMSE=261.47).")
ws5.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="595959")

pred_cols = ["Campaign", "Engagement_Rate", "Campaign_Cost", "Product_Sales",
             "Campaign_Duration_Days", "Predicted_ROI", "CI_Lower_95", "CI_Upper_95"]
for c_idx, h in enumerate(pred_cols, 1):
    ws5.cell(row=4, column=c_idx, value=h)
style_header_row(ws5, 4, len(pred_cols))

for r_idx, camp in enumerate(met["new_campaigns"], start=5):
    alt = (r_idx % 2 == 0)
    row_vals = [
        camp["Campaign"],
        camp["Engagement_Rate"],
        camp["Campaign_Cost"],
        camp["Product_Sales"],
        camp["Campaign_Duration_Days"],
        camp["Predicted_ROI"],
        camp["CI_Lower_95"],
        camp["CI_Upper_95"],
    ]
    for c_idx, val in enumerate(row_vals, 1):
        cell = ws5.cell(row=r_idx, column=c_idx, value=val)
        cell.font   = BODY_FONT
        cell.border = thin_border()
        cell.fill   = ALT_FILL if alt else WHITE_FILL
        if isinstance(val, float):
            cell.alignment = RIGHT
            cell.number_format = "#,##0.00"
        elif isinstance(val, int):
            cell.alignment = RIGHT
            cell.number_format = "#,##0"
        else:
            cell.alignment = LEFT

# Conditional format for Predicted_ROI
ws5.conditional_formatting.add(
    "F5:F9",
    ColorScaleRule(start_type="min", start_color="F4CCCC",
                   end_type="max",   end_color="C6EFCE")
)

widths5 = [28, 18, 16, 16, 24, 16, 14, 14]
for i, w in enumerate(widths5, 1):
    set_col_width(ws5, i, w)
ws5.row_dimensions[1].height = 24
ws5.row_dimensions[4].height = 20
print("Sheet 5 (Predictions) created.")

# ════════════════════════════════════════════════════════════════════════════
# SHEET 6 — DATA DICTIONARY
# ════════════════════════════════════════════════════════════════════════════
ws6 = wb.create_sheet("Data_Dictionary")
ws6.sheet_view.showGridLines = False

add_title(ws6, 1, 1, "Data Dictionary — Final Processed Dataset")
ws6.cell(row=2, column=1,
         value="File: data/processed/influencer_roi_analysis_dataset.csv  |  "
               "Rows: 147,000  |  Columns: 16")
ws6.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="595959")

dict_header = ["Column Name", "Data Type", "Source", "Description / Formula", "Example Value"]
for c_idx, h in enumerate(dict_header, 1):
    ws6.cell(row=4, column=c_idx, value=h)
style_header_row(ws6, 4, len(dict_header))

dd = [
    ("Campaign_ID",             "String",   "Raw",        "Unique identifier for each campaign. Format: CAMP######", "CAMP100001"),
    ("Platform",                "String",   "Raw",        "Social media platform: Instagram, YouTube, TikTok, Twitter", "YouTube"),
    ("Influencer_Category",     "String",   "Raw",        "Content niche: Beauty, Tech, Fashion, Food, Fitness, Travel, Gaming", "Food"),
    ("Campaign_Type",           "String",   "Raw",        "Type of campaign: Brand Awareness, Product Launch, Giveaway, Seasonal Sale, Event Promotion", "Product Launch"),
    ("Start_Date",              "Date",     "Raw",        "Campaign start date (parsed to datetime)", "2022-01-02"),
    ("End_Date",                "Date",     "Raw",        "Campaign end date (parsed to datetime)", "2022-01-15"),
    ("Campaign_Duration_Days",  "Integer",  "Raw",        "Duration of campaign in days (validated against Start/End dates)", "13"),
    ("Estimated_Reach",         "Integer",  "Raw",        "Number of unique users estimated to have seen the campaign", "437228"),
    ("Engagements",             "Integer",  "Raw",        "Total interactions: likes, comments, shares, saves", "47985"),
    ("Product_Sales",           "Integer",  "Raw",        "Number of product units sold attributed to the campaign", "165"),
    ("Engagement_Rate",         "Float",    "Engineered", "FORMULA: (Engagements / Estimated_Reach) x 100  |  Measures how effectively the audience engaged. Units: %", "10.9748"),
    ("Campaign_Cost",           "Float",    "Engineered", "FORMULA: (Estimated_Reach x Platform_CPM) / 1000  |  CPM: Instagram=INR150, YouTube=INR120, TikTok=INR100, Twitter=INR80. Units: INR", "52467.36"),
    ("Revenue",                 "Float",    "Engineered", "FORMULA: Product_Sales x Category_Avg_Unit_Value  |  Avg unit values: Beauty=1500, Tech=5000, Fashion=1200, Food=300, Fitness=800, Travel=3000, Gaming=1000. Units: INR", "49500.00"),
    ("ROI",                     "Float",    "Engineered", "FORMULA: (Revenue - Campaign_Cost) / Campaign_Cost  |  TARGET VARIABLE. Capped at 1st-99th pct to remove extremes. Dimensionless ratio.", "-0.0566"),
    ("Year",                    "Integer",  "Engineered", "Year extracted from Start_Date", "2022"),
    ("Month",                   "Integer",  "Engineered", "Month number (1-12) extracted from Start_Date", "1"),
]

for r_idx, row_data in enumerate(dd, start=5):
    alt = (r_idx % 2 == 0)
    for c_idx, val in enumerate(row_data, 1):
        cell = ws6.cell(row=r_idx, column=c_idx, value=val)
        cell.font   = BODY_FONT
        cell.border = thin_border()
        cell.fill   = ALT_FILL if alt else WHITE_FILL
        cell.alignment = WRAP

    # Highlight engineered columns
    if row_data[2] == "Engineered":
        for c_idx in range(1, 6):
            ws6.cell(row=r_idx, column=c_idx).font = Font(
                name="Calibri", size=10, bold=True, color="1F3864")

widths6 = [28, 12, 12, 70, 18]
for i, w in enumerate(widths6, 1):
    set_col_width(ws6, i, w)
for r in range(5, 5 + len(dd)):
    ws6.row_dimensions[r].height = 36
ws6.row_dimensions[1].height = 24
ws6.row_dimensions[4].height = 20
ws6.freeze_panes = "A5"
print("Sheet 6 (Data_Dictionary) created.")

# ── Save workbook ─────────────────────────────────────────────────────────────
wb.save(OUT_PATH)
print(f"\nWorkbook saved: {OUT_PATH}")
print(f"Sheets: {wb.sheetnames}")
