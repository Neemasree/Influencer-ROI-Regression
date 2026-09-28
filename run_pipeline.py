"""
run_pipeline.py
===============
Master script — runs the complete Influencer Marketing ROI analysis pipeline.

Usage:
    python run_pipeline.py

Steps
-----
1.  Data processing  : load raw CSV, clean, engineer features, save processed CSV
2.  Statistics       : descriptive stats and normality test
3.  Visualisation    : generate all 16 charts -> outputs/figures/
4.  Regression       : fit OLS on 147,000 rows, save model + metrics JSON
5.  Evaluation       : MAE, RMSE, actual-vs-predicted charts
6.  Predictions      : predict ROI for 5 new campaigns -> outputs/predictions/
7.  Excel            : build 6-sheet workbook -> excel/influencer_marketing.xlsx

All outputs go to:
    outputs/figures/            — PNG charts
    outputs/predictions/        — CSV of new-campaign predictions
    outputs/regression_metrics.json
    outputs/ols_model.pkl       — pickled fitted model
    excel/influencer_marketing.xlsx
"""

import os
import sys

# Ensure project root is on path
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pandas as pd

from src.process_data  import build_processed_dataset
from src.statistics    import print_stats_summary
from src.visualization import generate_eda_charts, generate_regression_charts
from src.regression    import fit_model, get_metrics, print_equation
from src.evaluation    import evaluate_model, predict_new_campaigns, default_new_campaigns

PROC_PATH = os.path.join(_ROOT, "data", "processed",
                         "influencer_roi_analysis_dataset.csv")

FEATURES  = ["Engagement_Rate", "Campaign_Cost",
             "Product_Sales",   "Campaign_Duration_Days"]
TARGET    = "ROI"


def main():
    print("\n" + "=" * 65)
    print("  INFLUENCER MARKETING ROI — FULL ANALYSIS PIPELINE")
    print("  Predictive Statistical Analysis Using Multiple Linear Regression")
    print("=" * 65)

    # ── STEP 1: Data Processing ──────────────────────────────────────────────
    print("\n[STEP 1] Data Processing")
    df = build_processed_dataset(save=True)

    # ── STEP 2: Descriptive Statistics ──────────────────────────────────────
    print("\n[STEP 2] Descriptive Statistics")
    print_stats_summary(df)

    # ── STEP 3: EDA Visualisations ───────────────────────────────────────────
    print("\n[STEP 3] EDA Visualisations")
    generate_eda_charts(df)

    # ── STEP 4: Regression ───────────────────────────────────────────────────
    print("\n[STEP 4] Multiple Linear Regression (OLS — n=147,000)")
    model = fit_model(df, features=FEATURES, target=TARGET, save=True)

    # ── STEP 5: Evaluation ───────────────────────────────────────────────────
    print("\n[STEP 5] Model Evaluation")
    y        = df[TARGET]
    y_pred   = model.fittedvalues
    eval_res = evaluate_model(model, y)
    print_equation(get_metrics())

    # ── STEP 6: Predictions for New Campaigns ────────────────────────────────
    print("\n[STEP 6] Predictions for New Campaigns")
    new_camps = default_new_campaigns()
    pred_df   = predict_new_campaigns(model, new_camps, save=True)
    print(pred_df[["Campaign", "Predicted_ROI",
                   "CI_Lower_95", "CI_Upper_95"]].to_string(index=False))

    # ── STEP 7: Regression & Evaluation Charts ───────────────────────────────
    print("\n[STEP 7] Regression & Evaluation Charts")
    generate_regression_charts(
        df, model, y, y_pred,
        mae=eval_res["MAE"], rmse=eval_res["RMSE"],
        pred_df=pred_df
    )

    # ── STEP 8: Excel Workbook ───────────────────────────────────────────────
    print("\n[STEP 8] Building Excel Workbook")
    _build_excel(df, eval_res, pred_df)

    # ── Done ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  PIPELINE COMPLETE")
    print(f"  Processed dataset : data/processed/influencer_roi_analysis_dataset.csv")
    print(f"  Model             : outputs/ols_model.pkl")
    print(f"  Metrics           : outputs/regression_metrics.json")
    print(f"  Figures           : outputs/figures/  (16 charts)")
    print(f"  Predictions       : outputs/predictions/new_campaign_predictions.csv")
    print(f"  Excel             : excel/influencer_marketing.xlsx")
    print("=" * 65)


def _build_excel(df: pd.DataFrame, eval_res: dict, pred_df: pd.DataFrame):
    """Build the 6-sheet Excel workbook."""
    import json
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.formatting.rule import ColorScaleRule

    METRICS_PATH = os.path.join(_ROOT, "outputs", "regression_metrics.json")
    with open(METRICS_PATH, encoding="utf-8") as f:
        met = json.load(f)

    OUT = os.path.join(_ROOT, "excel", "influencer_marketing.xlsx")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    # ── Style helpers ────────────────────────────────────────────────────────
    HDR_FILL  = PatternFill("solid", fgColor="1F3864")
    ALT_FILL  = PatternFill("solid", fgColor="EBF3FB")
    WHT_FILL  = PatternFill("solid", fgColor="FFFFFF")
    ACC_FILL  = PatternFill("solid", fgColor="D6E4F0")
    HDR_FONT  = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    BODY_FONT = Font(name="Calibri", size=10)
    TTL_FONT  = Font(name="Calibri", bold=True, size=13, color="1F3864")
    LBL_FONT  = Font(name="Calibri", bold=True, size=10, color="1F3864")
    C         = Alignment(horizontal="center", vertical="center")
    L         = Alignment(horizontal="left",   vertical="center")
    R         = Alignment(horizontal="right",  vertical="center")
    W         = Alignment(horizontal="left",   vertical="top", wrap_text=True)

    def _side(w="thin", c="BFBFBF"):
        return Side(style=w, color=c)

    def _bdr(thin=True):
        s = _side("thin" if thin else "medium",
                  "BFBFBF" if thin else "1F3864")
        return Border(left=s, right=s, top=s, bottom=s)

    def _hdr_row(ws, row, ncols, col_start=1):
        for c in range(col_start, col_start + ncols):
            cell = ws.cell(row=row, column=c)
            cell.fill      = HDR_FILL
            cell.font      = HDR_FONT
            cell.alignment = C
            cell.border    = _bdr(False)

    def _data_row(ws, row, values, col_start=1):
        alt = row % 2 == 0
        for c_idx, val in enumerate(values, col_start):
            cell = ws.cell(row=row, column=c_idx, value=val)
            cell.fill   = ALT_FILL if alt else WHT_FILL
            cell.font   = BODY_FONT
            cell.border = _bdr()
            if isinstance(val, float):
                cell.alignment  = R
                cell.number_format = "#,##0.0000"
            elif isinstance(val, int):
                cell.alignment  = R
                cell.number_format = "#,##0"
            else:
                cell.alignment = L

    def _col_w(ws, col, w):
        ws.column_dimensions[get_column_letter(col)].width = w

    def _title(ws, row, col, text):
        c = ws.cell(row=row, column=col, value=text)
        c.font = TTL_FONT
        c.alignment = L

    wb = Workbook()
    wb.remove(wb.active)

    # ── Sheet 1: Processed_Dataset ───────────────────────────────────────────
    ws1 = wb.create_sheet("Processed_Dataset")
    ws1.sheet_view.showGridLines = False
    _title(ws1, 1, 1, "Influencer Marketing ROI — Processed Analytical Dataset")
    ws1.cell(row=2, column=1,
             value=f"Source: data/processed/influencer_roi_analysis_dataset.csv  |  "
                   f"Total rows: {len(df):,}  |  Displaying first 5,000 rows  |  Columns: {len(df.columns)}")
    ws1.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="595959")

    disp = df.head(5000).copy()
    disp["Start_Date"] = disp["Start_Date"].astype(str)
    disp["End_Date"]   = disp["End_Date"].astype(str)
    cols = list(disp.columns)

    for c_idx, col_name in enumerate(cols, 1):
        ws1.cell(row=4, column=c_idx, value=col_name)
    _hdr_row(ws1, 4, len(cols))

    for r_idx, row_data in enumerate(disp.itertuples(index=False), 5):
        _data_row(ws1, r_idx, list(row_data))

    widths1 = [14,12,20,18,12,12,26,16,13,14,18,15,16,12,8,8]
    for i, w in enumerate(widths1[:len(cols)], 1):
        _col_w(ws1, i, w)
    ws1.freeze_panes = "A5"
    ws1.row_dimensions[4].height = 20

    roi_col = get_column_letter(14)
    ws1.conditional_formatting.add(
        f"{roi_col}5:{roi_col}{5+len(disp)-1}",
        ColorScaleRule(start_type="min", start_color="F4CCCC",
                       mid_type="percentile", mid_value=50, mid_color="FFFFFF",
                       end_type="max", end_color="C6EFCE")
    )

    # ── Sheet 2: Summary_Statistics ─────────────────────────────────────────
    ws2 = wb.create_sheet("Summary_Statistics")
    ws2.sheet_view.showGridLines = False
    _title(ws2, 1, 1, "Descriptive Statistics — Processed Dataset (147,000 rows)")

    num_cols = ["Estimated_Reach","Engagements","Product_Sales",
                "Campaign_Duration_Days","Engagement_Rate",
                "Campaign_Cost","Revenue","ROI"]
    desc = df[num_cols].describe().T.reset_index()
    desc.columns = ["Variable","Count","Mean","Std_Dev","Min",
                    "Pct_25","Median","Pct_75","Max"]
    desc["Skewness"] = df[num_cols].skew().values
    desc["Kurtosis"] = df[num_cols].kurt().values

    for c_idx, h in enumerate(desc.columns, 1):
        ws2.cell(row=4, column=c_idx, value=h)
    _hdr_row(ws2, 4, len(desc.columns))

    for r_idx, row_data in enumerate(desc.itertuples(index=False), 5):
        _data_row(ws2, r_idx, list(row_data))

    _col_w(ws2, 1, 28)
    for i in range(2, len(desc.columns)+1):
        _col_w(ws2, i, 16)
    ws2.freeze_panes = "B5"

    # ── Sheet 3: Correlation_Analysis ────────────────────────────────────────
    ws3 = wb.create_sheet("Correlation_Analysis")
    ws3.sheet_view.showGridLines = False
    _title(ws3, 1, 1, "Pearson Correlation Matrix")

    corr = df[num_cols].corr().round(4)
    ws3.cell(row=4, column=1, value="Variable").font = LBL_FONT
    _hdr_row(ws3, 4, 1)
    for c_idx, n in enumerate(num_cols, 2):
        ws3.cell(row=4, column=c_idx, value=n)
    _hdr_row(ws3, 4, len(num_cols), col_start=2)

    for r_idx, rv in enumerate(num_cols, 5):
        c0 = ws3.cell(row=r_idx, column=1, value=rv)
        c0.font = LBL_FONT; c0.fill = ACC_FILL
        c0.border = _bdr(); c0.alignment = L
        for c_idx, cv in enumerate(num_cols, 2):
            val  = corr.loc[rv, cv]
            cell = ws3.cell(row=r_idx, column=c_idx, value=round(float(val), 4))
            cell.font = BODY_FONT; cell.border = _bdr()
            cell.alignment = C; cell.number_format = "0.0000"
            if rv == cv:
                cell.fill = PatternFill("solid", fgColor="D9D9D9")
            elif abs(val) >= 0.3:
                intensity = min(int(abs(val) * 200), 200)
                if val > 0:
                    r_c, g_c, b_c = 70, 130+intensity//3, 70
                else:
                    r_c, g_c, b_c = 130+intensity//3, 70, 70
                cell.fill = PatternFill("solid", fgColor=f"{r_c:02X}{g_c:02X}{b_c:02X}")
                cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
            else:
                cell.fill = WHT_FILL

    _col_w(ws3, 1, 26)
    for i in range(2, len(num_cols)+2):
        _col_w(ws3, i, 20)

    # ROI correlation summary
    sr = 5 + len(num_cols) + 2
    ws3.cell(row=sr, column=1, value="ROI Correlation Summary").font = LBL_FONT
    for c_idx, h in enumerate(["Feature","Correlation with ROI","Strength"], 1):
        ws3.cell(row=sr+1, column=c_idx, value=h)
    _hdr_row(ws3, sr+1, 3)
    roi_corr = corr["ROI"].drop("ROI").sort_values(key=abs, ascending=False)
    interp = {
        "Revenue":               "Strong positive",
        "Estimated_Reach":       "Moderate negative",
        "Campaign_Cost":         "Moderate negative",
        "Engagement_Rate":       "Moderate positive",
        "Product_Sales":         "Moderate positive",
        "Engagements":           "Negligible",
        "Campaign_Duration_Days":"Negligible",
    }
    for i, (feat, val) in enumerate(roi_corr.items(), sr+2):
        _data_row(ws3, i, [feat, round(float(val), 4), interp.get(feat, "")])
    _col_w(ws3, 3, 36)

    # ── Sheet 4: Regression_Results ──────────────────────────────────────────
    ws4 = wb.create_sheet("Regression_Results")
    ws4.sheet_view.showGridLines = False
    _title(ws4, 1, 1, "Multiple Linear Regression Results — OLS (Statsmodels)")
    ws4.cell(row=2, column=1,
             value="Method: OLS | Observations: 147,000 (full processed dataset) | "
                   "Target: ROI | Predictors: Engagement_Rate, Campaign_Cost, Product_Sales, Campaign_Duration_Days")
    ws4.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="595959")

    fit_metrics = [
        ("R-squared (R2)",  met["r2"]),
        ("Adjusted R2",     met["adj_r2"]),
        ("F-statistic",     met["f_stat"]),
        ("Prob (F)",        met["f_pvalue"]),
        ("AIC",             met["aic"]),
        ("BIC",             met["bic"]),
        ("Observations",    met["observations"]),
        ("MAE",             met["mae"]),
        ("RMSE",            met["rmse"]),
    ]
    for c_idx, h in enumerate(["Metric","Value"], 1):
        ws4.cell(row=4, column=c_idx, value=h)
    _hdr_row(ws4, 4, 2)
    for r_idx, (label, val) in enumerate(fit_metrics, 5):
        _data_row(ws4, r_idx, [label, round(val,6) if isinstance(val,float) else val])

    coef_r = 4 + len(fit_metrics) + 3
    ws4.cell(row=coef_r, column=1, value="Regression Coefficients").font = LBL_FONT
    coef_hdrs = ["Variable","Coefficient","Std Error","t-stat",
                 "p-value","CI Lower 95","CI Upper 95","Significant?"]
    for c_idx, h in enumerate(coef_hdrs, 1):
        ws4.cell(row=coef_r+1, column=c_idx, value=h)
    _hdr_row(ws4, coef_r+1, len(coef_hdrs))

    feat_order = ["const","Engagement_Rate","Campaign_Cost",
                  "Product_Sales","Campaign_Duration_Days"]
    for i, feat in enumerate(feat_order, coef_r+2):
        p    = met["pvalues"][feat]
        sig  = "Yes ***" if p < 0.001 else ("Yes **" if p < 0.01 else ("Yes *" if p < 0.05 else "No"))
        row  = [feat,
                round(met["coefs"][feat], 8),
                round(met["std_errors"][feat], 8),
                round(met["t_stats"][feat], 4),
                round(p, 8),
                round(met["conf_int_lower"][feat], 8),
                round(met["conf_int_upper"][feat], 8),
                sig]
        _data_row(ws4, i, row)

    # Equation box
    eq_r = coef_r + len(feat_order) + 4
    ws4.cell(row=eq_r, column=1, value="Final Regression Equation").font = LBL_FONT
    c = met["coefs"]
    eq = (f"ROI = {c['const']:.4f}  +  {c['Engagement_Rate']:.4f} x Engagement_Rate"
          f"  -  {abs(c['Campaign_Cost']):.6f} x Campaign_Cost"
          f"  +  {c['Product_Sales']:.4f} x Product_Sales"
          f"  +  ({c['Campaign_Duration_Days']:.4f}) x Campaign_Duration_Days")
    cell_eq = ws4.cell(row=eq_r+1, column=1, value=eq)
    cell_eq.font = Font(name="Courier New", size=10, bold=True, color="1F3864")
    cell_eq.fill = PatternFill("solid", fgColor="EBF3FB")
    cell_eq.border = _bdr()
    ws4.merge_cells(f"A{eq_r+1}:H{eq_r+1}")
    ws4.row_dimensions[eq_r+1].height = 20

    w4 = [28,16,14,12,14,16,16,12]
    for i, w in enumerate(w4, 1):
        _col_w(ws4, i, w)

    # ── Sheet 5: Predictions ─────────────────────────────────────────────────
    ws5 = wb.create_sheet("Predictions")
    ws5.sheet_view.showGridLines = False
    _title(ws5, 1, 1, "ROI Predictions — New Campaigns (95% Prediction Intervals)")
    ws5.cell(row=2, column=1,
             value="Model: OLS fitted on 147,000 rows. "
                   "Wide PI reflects high ROI variance in the dataset.")
    ws5.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="595959")

    pred_disp = pred_df[["Campaign","Engagement_Rate","Campaign_Cost",
                         "Product_Sales","Campaign_Duration_Days",
                         "Predicted_ROI","CI_Lower_95","CI_Upper_95"]].copy()
    for c_idx, h in enumerate(pred_disp.columns, 1):
        ws5.cell(row=4, column=c_idx, value=h)
    _hdr_row(ws5, 4, len(pred_disp.columns))
    for r_idx, row_data in enumerate(pred_disp.itertuples(index=False), 5):
        _data_row(ws5, r_idx, list(row_data))

    ws5.conditional_formatting.add(
        "F5:F9",
        ColorScaleRule(start_type="min", start_color="F4CCCC",
                       end_type="max",   end_color="C6EFCE")
    )
    w5 = [28,18,16,16,24,16,14,14]
    for i, w in enumerate(w5, 1):
        _col_w(ws5, i, w)

    # ── Sheet 6: Data_Dictionary ─────────────────────────────────────────────
    ws6 = wb.create_sheet("Data_Dictionary")
    ws6.sheet_view.showGridLines = False
    _title(ws6, 1, 1, "Data Dictionary — Final Processed Dataset (16 Columns)")
    ws6.cell(row=2, column=1,
             value="IMPORTANT: Campaign_Cost, Revenue, and ROI are derived variables "
                   "calculated by this project's feature engineering. "
                   "They were NOT provided by the original Kaggle dataset.")
    ws6.cell(row=2, column=1).font = Font(name="Calibri", size=9, italic=True, color="C00000")

    dd_hdrs = ["Column","Data Type","Source","Description / Formula","Example"]
    for c_idx, h in enumerate(dd_hdrs, 1):
        ws6.cell(row=4, column=c_idx, value=h)
    _hdr_row(ws6, 4, len(dd_hdrs))

    dd = [
        ("Campaign_ID",            "String",  "Raw",        "Unique campaign identifier. Format: CAMP######", "CAMP100001"),
        ("Platform",               "String",  "Raw",        "Social platform: Instagram, YouTube, TikTok, Twitter", "YouTube"),
        ("Influencer_Category",    "String",  "Raw",        "Content niche: Beauty, Tech, Fashion, Food, Fitness, Travel, Gaming", "Food"),
        ("Campaign_Type",          "String",  "Raw",        "Strategy: Brand Awareness, Product Launch, Giveaway, Seasonal Sale, Event Promotion", "Product Launch"),
        ("Start_Date",             "Date",    "Raw",        "Campaign start date", "2022-01-02"),
        ("End_Date",               "Date",    "Raw",        "Campaign end date", "2022-01-15"),
        ("Campaign_Duration_Days", "Integer", "Raw",        "Duration in days (validated against Start/End dates)", "13"),
        ("Estimated_Reach",        "Integer", "Raw",        "Unique users estimated to have seen the campaign", "437228"),
        ("Engagements",            "Integer", "Raw",        "Total interactions: likes, comments, shares, saves", "47985"),
        ("Product_Sales",          "Integer", "Raw",        "Product units sold attributed to the campaign", "165"),
        ("Engagement_Rate",        "Float",   "Engineered", "FORMULA: (Engagements / Estimated_Reach) x 100  |  Unit: %", "10.9748"),
        ("Campaign_Cost",          "Float",   "Engineered", "FORMULA: (Estimated_Reach x Platform_CPM) / 1000  |  CPMs: Instagram=INR150, YouTube=INR120, TikTok=INR100, Twitter=INR80  |  Unit: INR", "52467.36"),
        ("Revenue",                "Float",   "Engineered", "FORMULA: Product_Sales x Category_Avg_Unit_Value  |  Values: Beauty=1500, Tech=5000, Fashion=1200, Food=300, Fitness=800, Travel=3000, Gaming=1000  |  Unit: INR", "49500.00"),
        ("ROI",                    "Float",   "Engineered", "FORMULA: (Revenue - Campaign_Cost) / Campaign_Cost  |  TARGET VARIABLE. Capped at 1st-99th percentile. Dimensionless ratio.", "-0.0566"),
        ("Year",                   "Integer", "Engineered", "Year extracted from Start_Date", "2022"),
        ("Month",                  "Integer", "Engineered", "Month number (1-12) extracted from Start_Date", "1"),
    ]

    for r_idx, row_data in enumerate(dd, 5):
        alt = r_idx % 2 == 0
        for c_idx, val in enumerate(row_data, 1):
            cell = ws6.cell(row=r_idx, column=c_idx, value=val)
            cell.font   = BODY_FONT
            cell.border = _bdr()
            cell.fill   = ALT_FILL if alt else WHT_FILL
            cell.alignment = W
        if row_data[2] == "Engineered":
            for c_idx in range(1, 6):
                ws6.cell(row=r_idx, column=c_idx).font = Font(
                    name="Calibri", size=10, bold=True, color="1F3864")

    w6 = [28, 12, 12, 70, 16]
    for i, w in enumerate(w6, 1):
        _col_w(ws6, i, w)
    for r in range(5, 5+len(dd)):
        ws6.row_dimensions[r].height = 38

    wb.save(OUT)
    print(f"[excel] Workbook saved -> {OUT}")
    print(f"        Sheets: {wb.sheetnames}")


if __name__ == "__main__":
    main()
