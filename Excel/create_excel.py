"""
Creates a formatted Excel workbook with multiple sheets:
  Sheet 1 — Raw Dataset (formatted table)
  Sheet 2 — Summary Statistics
  Sheet 3 — ROI Analysis by Category
  Sheet 4 — Data Dictionary
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import (PatternFill, Font, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
import os

# ── Load Data ────────────────────────────────────────────────────────────────
df = pd.read_csv('../Dataset/influencer_marketing.csv')
print(f"Loaded dataset: {df.shape[0]} rows x {df.shape[1]} columns")

# ── Colour Palette ────────────────────────────────────────────────────────────
HEADER_BG   = "1F4E79"   # dark navy
HEADER_FG   = "FFFFFF"   # white
SUBHEAD_BG  = "2E75B6"   # medium blue
ALT_ROW     = "D6E4F0"   # light blue
TITLE_BG    = "0D2E5A"   # deep navy
ACCENT      = "F4B942"   # gold accent
GREEN_BG    = "E2EFDA"   # light green
RED_BG      = "FCE4D6"   # light red

def header_style(bold=True, bg=HEADER_BG, fg=HEADER_FG, size=11):
    return {
        'font'  : Font(bold=bold, color=fg, size=size, name='Calibri'),
        'fill'  : PatternFill("solid", fgColor=bg),
        'align' : Alignment(horizontal='center', vertical='center', wrap_text=True),
        'border': thin_border()
    }

def thin_border():
    side = Side(style='thin', color='B0C4DE')
    return Border(left=side, right=side, top=side, bottom=side)

def apply_style(cell, font=None, fill=None, align=None, border=None):
    if font:   cell.font      = font
    if fill:   cell.fill      = fill
    if align:  cell.alignment = align
    if border: cell.border    = border

def style_header_row(ws, row_num, col_start, col_end, bg=HEADER_BG, fg=HEADER_FG):
    for col in range(col_start, col_end + 1):
        cell = ws.cell(row=row_num, column=col)
        cell.font      = Font(bold=True, color=fg, size=10, name='Calibri')
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border    = thin_border()

wb = Workbook()

# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 1 — Raw Dataset
# ═══════════════════════════════════════════════════════════════════════════════
ws1 = wb.active
ws1.title = "Dataset"

# Title row
ws1.merge_cells('A1:N1')
title_cell = ws1['A1']
title_cell.value     = "Influencer Marketing Campaign Dataset"
title_cell.font      = Font(bold=True, color="FFFFFF", size=14, name='Calibri')
title_cell.fill      = PatternFill("solid", fgColor=TITLE_BG)
title_cell.alignment = Alignment(horizontal='center', vertical='center')
ws1.row_dimensions[1].height = 30

# Subtitle
ws1.merge_cells('A2:N2')
sub = ws1['A2']
sub.value     = "Statistical Analysis and Predictive Modeling of Influencer Marketing ROI  |  200 Campaigns  |  14 Variables"
sub.font      = Font(italic=True, color="FFFFFF", size=10, name='Calibri')
sub.fill      = PatternFill("solid", fgColor=SUBHEAD_BG)
sub.alignment = Alignment(horizontal='center', vertical='center')
ws1.row_dimensions[2].height = 20

# Column headers (row 3)
headers = list(df.columns)
for col_num, header in enumerate(headers, start=1):
    cell = ws1.cell(row=3, column=col_num, value=header)
    cell.font      = Font(bold=True, color="FFFFFF", size=10, name='Calibri')
    cell.fill      = PatternFill("solid", fgColor=HEADER_BG)
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border    = thin_border()
ws1.row_dimensions[3].height = 28

# Data rows
for row_idx, row_data in enumerate(df.itertuples(index=False), start=4):
    bg = ALT_ROW if row_idx % 2 == 0 else "FFFFFF"
    for col_num, value in enumerate(row_data, start=1):
        cell = ws1.cell(row=row_idx, column=col_num, value=value)
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = thin_border()
        cell.font      = Font(size=9, name='Calibri')
        # Format numbers
        col_name = headers[col_num - 1]
        if col_name in ['Campaign_Cost', 'Revenue']:
            cell.number_format = '#,##0.00'
        elif col_name == 'ROI':
            cell.number_format = '0.0000'
        elif col_name == 'Engagement_Rate':
            cell.number_format = '0.00'

# Column widths
col_widths = {
    'A': 12, 'B': 13, 'C': 12, 'D': 16, 'E': 14,
    'F': 12, 'G': 12, 'H': 10, 'I': 17, 'J': 17,
    'K': 17, 'L': 22, 'M': 16, 'N': 10
}
for col_letter, width in col_widths.items():
    ws1.column_dimensions[col_letter].width = width

# Freeze panes (keep headers visible when scrolling)
ws1.freeze_panes = 'A4'

# Conditional formatting on ROI column (column N = 14)
roi_col_letter = get_column_letter(14)
roi_range = f"{roi_col_letter}4:{roi_col_letter}{3+len(df)}"
ws1.conditional_formatting.add(
    roi_range,
    ColorScaleRule(
        start_type='min', start_color='FCE4D6',
        mid_type='num',   mid_value=1.0, mid_color='FFFF00',
        end_type='max',   end_color='E2EFDA'
    )
)

print("Sheet 1 (Dataset) created.")

# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 2 — Summary Statistics
# ═══════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("Summary Statistics")

# Title
ws2.merge_cells('A1:H1')
t = ws2['A1']
t.value     = "Descriptive Statistics — All Numeric Variables"
t.font      = Font(bold=True, color="FFFFFF", size=13, name='Calibri')
t.fill      = PatternFill("solid", fgColor=TITLE_BG)
t.alignment = Alignment(horizontal='center', vertical='center')
ws2.row_dimensions[1].height = 28

numeric_cols = ['Followers','Likes','Comments','Shares','Engagement_Rate',
                'Campaign_Cost','Revenue','Campaign_Duration_Days','Post_Frequency','ROI']

stats_data = {
    'Variable'     : numeric_cols,
    'Count'        : [int(df[c].count()) for c in numeric_cols],
    'Mean'         : [round(df[c].mean(), 4)   for c in numeric_cols],
    'Median'       : [round(df[c].median(), 4) for c in numeric_cols],
    'Std Dev'      : [round(df[c].std(), 4)    for c in numeric_cols],
    'Min'          : [round(df[c].min(), 4)    for c in numeric_cols],
    'Max'          : [round(df[c].max(), 4)    for c in numeric_cols],
    'Skewness'     : [round(df[c].skew(), 4)   for c in numeric_cols],
}
stats_df = pd.DataFrame(stats_data)

stat_headers = list(stats_df.columns)
for col_num, h in enumerate(stat_headers, start=1):
    cell = ws2.cell(row=2, column=col_num, value=h)
    cell.font      = Font(bold=True, color="FFFFFF", size=10, name='Calibri')
    cell.fill      = PatternFill("solid", fgColor=HEADER_BG)
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border    = thin_border()
ws2.row_dimensions[2].height = 24

for row_idx, row in enumerate(stats_df.itertuples(index=False), start=3):
    bg = ALT_ROW if row_idx % 2 == 0 else "FFFFFF"
    for col_num, value in enumerate(row, start=1):
        cell = ws2.cell(row=row_idx, column=col_num, value=value)
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = thin_border()
        cell.font      = Font(size=10, name='Calibri')

stat_widths = [24, 10, 14, 14, 14, 16, 16, 12]
for i, w in enumerate(stat_widths, start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w

# ROI Summary box
start_row = len(stats_df) + 5
ws2.merge_cells(f'A{start_row}:H{start_row}')
box_title = ws2[f'A{start_row}']
box_title.value     = "ROI — Key Business Metrics"
box_title.font      = Font(bold=True, color="FFFFFF", size=11, name='Calibri')
box_title.fill      = PatternFill("solid", fgColor=SUBHEAD_BG)
box_title.alignment = Alignment(horizontal='center', vertical='center')
ws2.row_dimensions[start_row].height = 22

roi_metrics = [
    ("Campaigns with ROI > 1.0 (Profitable)", f"{(df['ROI']>1.0).sum()} ({(df['ROI']>1.0).mean()*100:.1f}%)"),
    ("Campaigns with ROI < 0.0 (Loss)",        f"{(df['ROI']<0.0).sum()} ({(df['ROI']<0.0).mean()*100:.1f}%)"),
    ("Best Campaign ROI",                        f"{df['ROI'].max():.4f}"),
    ("Worst Campaign ROI",                       f"{df['ROI'].min():.4f}"),
    ("Average ROI",                              f"{df['ROI'].mean():.4f}"),
]
for i, (metric, value) in enumerate(roi_metrics, start=start_row+1):
    ws2[f'A{i}'] = metric
    ws2[f'A{i}'].font      = Font(bold=True, size=10, name='Calibri')
    ws2[f'A{i}'].alignment = Alignment(vertical='center')
    ws2[f'A{i}'].border    = thin_border()
    ws2.merge_cells(f'B{i}:H{i}')
    ws2[f'B{i}'] = value
    ws2[f'B{i}'].alignment = Alignment(horizontal='center', vertical='center')
    ws2[f'B{i}'].border    = thin_border()
    bg = GREEN_BG if 'Profitable' in metric or 'Best' in metric or 'Average' in metric else RED_BG
    for col in range(1, 9):
        ws2.cell(row=i, column=col).fill = PatternFill("solid", fgColor=bg.replace('#',''))

print("Sheet 2 (Summary Statistics) created.")

# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 3 — ROI Analysis by Category
# ═══════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("ROI by Category")

ws3.merge_cells('A1:F1')
t3 = ws3['A1']
t3.value     = "ROI Analysis by Influencer Tier and Platform"
t3.font      = Font(bold=True, color="FFFFFF", size=13, name='Calibri')
t3.fill      = PatternFill("solid", fgColor=TITLE_BG)
t3.alignment = Alignment(horizontal='center', vertical='center')
ws3.row_dimensions[1].height = 28

# By Tier
tier_stats = df.groupby('Influencer_Tier')['ROI'].agg(
    Count='count', Mean='mean', Median='median', Std='std', Min='min', Max='max'
).round(4).reset_index()
tier_stats.columns = ['Influencer Tier','Count','Mean ROI','Median ROI','Std Dev','Min ROI','Max ROI']

ws3['A2'] = "By Influencer Tier"
ws3['A2'].font  = Font(bold=True, color="FFFFFF", size=11, name='Calibri')
ws3['A2'].fill  = PatternFill("solid", fgColor=SUBHEAD_BG)
ws3['A2'].alignment = Alignment(horizontal='center', vertical='center')
ws3.merge_cells('A2:G2')
ws3.row_dimensions[2].height = 22

for col_num, h in enumerate(tier_stats.columns, start=1):
    cell = ws3.cell(row=3, column=col_num, value=h)
    cell.font  = Font(bold=True, color="FFFFFF", size=10, name='Calibri')
    cell.fill  = PatternFill("solid", fgColor=HEADER_BG)
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = thin_border()
ws3.row_dimensions[3].height = 22

tier_colors = {'Nano':'E8F5E9','Micro':'E3F2FD','Macro':'FFF3E0','Mega':'F3E5F5'}
for row_idx, row in enumerate(tier_stats.itertuples(index=False), start=4):
    tier_name = row[0]
    bg = tier_colors.get(tier_name, "FFFFFF")
    for col_num, value in enumerate(row, start=1):
        cell = ws3.cell(row=row_idx, column=col_num, value=value)
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = thin_border()
        cell.font      = Font(size=10, name='Calibri', bold=(col_num==1))

# By Platform
plat_start = 4 + len(tier_stats) + 2
ws3.merge_cells(f'A{plat_start}:G{plat_start}')
p2 = ws3[f'A{plat_start}']
p2.value     = "By Platform"
p2.font      = Font(bold=True, color="FFFFFF", size=11, name='Calibri')
p2.fill      = PatternFill("solid", fgColor=SUBHEAD_BG)
p2.alignment = Alignment(horizontal='center', vertical='center')
ws3.row_dimensions[plat_start].height = 22

plat_stats = df.groupby('Platform')['ROI'].agg(
    Count='count', Mean='mean', Median='median', Std='std', Min='min', Max='max'
).round(4).reset_index()
plat_stats.columns = ['Platform','Count','Mean ROI','Median ROI','Std Dev','Min ROI','Max ROI']

for col_num, h in enumerate(plat_stats.columns, start=1):
    cell = ws3.cell(row=plat_start+1, column=col_num, value=h)
    cell.font  = Font(bold=True, color="FFFFFF", size=10, name='Calibri')
    cell.fill  = PatternFill("solid", fgColor=HEADER_BG)
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = thin_border()
ws3.row_dimensions[plat_start+1].height = 22

plat_colors = {'Instagram':'FCE4EC','YouTube':'FFEBEE','TikTok':'E8EAF6','Twitter':'E0F7FA'}
for row_idx, row in enumerate(plat_stats.itertuples(index=False), start=plat_start+2):
    bg = plat_colors.get(row[0], "FFFFFF")
    for col_num, value in enumerate(row, start=1):
        cell = ws3.cell(row=row_idx, column=col_num, value=value)
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = thin_border()
        cell.font      = Font(size=10, name='Calibri', bold=(col_num==1))

for i, w in enumerate([20,10,12,14,12,12,12], start=1):
    ws3.column_dimensions[get_column_letter(i)].width = w

print("Sheet 3 (ROI by Category) created.")

# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 4 — Data Dictionary
# ═══════════════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet("Data Dictionary")

ws4.merge_cells('A1:E1')
t4 = ws4['A1']
t4.value     = "Data Dictionary — Variable Descriptions"
t4.font      = Font(bold=True, color="FFFFFF", size=13, name='Calibri')
t4.fill      = PatternFill("solid", fgColor=TITLE_BG)
t4.alignment = Alignment(horizontal='center', vertical='center')
ws4.row_dimensions[1].height = 28

dict_headers = ['Column Name', 'Data Type', 'Description', 'Unit', 'Role']
for col_num, h in enumerate(dict_headers, start=1):
    cell = ws4.cell(row=2, column=col_num, value=h)
    cell.font      = Font(bold=True, color="FFFFFF", size=10, name='Calibri')
    cell.fill      = PatternFill("solid", fgColor=HEADER_BG)
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border    = thin_border()
ws4.row_dimensions[2].height = 24

dictionary = [
    ('Campaign_ID',            'String',  'Unique identifier for each campaign',                         'ID',         'Identifier'),
    ('Platform',               'String',  'Social media platform used for the campaign',                 'Category',   'Feature (EDA)'),
    ('Niche',                  'String',  'Content category of the influencer',                          'Category',   'Feature (EDA)'),
    ('Influencer_Tier',        'String',  'Tier based on follower count (Nano/Micro/Macro/Mega)',         'Category',   'Feature (EDA)'),
    ('Followers',              'Integer', 'Total number of followers the influencer has',                'Count',      'Input Feature'),
    ('Likes',                  'Integer', 'Average number of likes per post',                            'Count',      'Input Feature'),
    ('Comments',               'Integer', 'Average number of comments per post',                         'Count',      'Input Feature'),
    ('Shares',                 'Integer', 'Average number of shares per post',                           'Count',      'Input Feature'),
    ('Engagement_Rate',        'Float',   'Percentage of followers who engage with content',             'Percentage', 'Input Feature (Key)'),
    ('Campaign_Cost',          'Float',   'Total money spent on the influencer campaign',                'INR (₹)',    'Input Feature'),
    ('Revenue',                'Float',   'Total revenue generated from the campaign',                   'INR (₹)',    'Used to calculate ROI'),
    ('Campaign_Duration_Days', 'Integer', 'Number of days the campaign ran',                             'Days',       'Input Feature'),
    ('Post_Frequency',         'Integer', 'Number of posts made during the campaign',                    'Count',      'Input Feature'),
    ('ROI',                    'Float',   'Return on Investment = (Revenue - Cost) / Cost',              'Ratio',      'TARGET VARIABLE'),
]

role_colors = {
    'Identifier'          : 'F5F5F5',
    'Feature (EDA)'       : 'FFF9C4',
    'Input Feature'       : 'E3F2FD',
    'Input Feature (Key)' : 'C8E6C9',
    'Used to calculate ROI': 'FFE0B2',
    'TARGET VARIABLE'     : 'FFCDD2',
}

for row_idx, row_data in enumerate(dictionary, start=3):
    bg = role_colors.get(row_data[4], 'FFFFFF')
    for col_num, value in enumerate(row_data, start=1):
        cell = ws4.cell(row=row_idx, column=col_num, value=value)
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.alignment = Alignment(horizontal='left' if col_num==3 else 'center',
                                   vertical='center', wrap_text=True)
        cell.border    = thin_border()
        cell.font      = Font(size=10, name='Calibri',
                              bold=(row_data[4] == 'TARGET VARIABLE'))
    ws4.row_dimensions[row_idx].height = 22

ws4.column_dimensions['A'].width = 25
ws4.column_dimensions['B'].width = 12
ws4.column_dimensions['C'].width = 52
ws4.column_dimensions['D'].width = 14
ws4.column_dimensions['E'].width = 22

print("Sheet 4 (Data Dictionary) created.")

# ── Save Workbook ─────────────────────────────────────────────────────────────
output_path = 'influencer_marketing.xlsx'
wb.save(output_path)
file_size = os.path.getsize(output_path) / 1024
print(f"\nExcel file saved: {output_path}")
print(f"File size       : {file_size:.1f} KB")
print(f"Sheets created  : {[ws.title for ws in wb.worksheets]}")
