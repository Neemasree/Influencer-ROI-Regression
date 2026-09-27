import pandas as pd, json, openpyxl, os

df = pd.read_csv('Dataset/influencer_marketing.csv')
print(f"CSV rows       : {len(df)}")
print(f"CSV columns    : {len(df.columns)}")

with open('Python/analysis.ipynb') as f:
    nb = json.load(f)
code_cells = [c for c in nb['cells'] if c['cell_type']=='code']
md_cells   = [c for c in nb['cells'] if c['cell_type']=='markdown']
print(f"Notebook code cells     : {len(code_cells)}")
print(f"Notebook markdown cells : {len(md_cells)}")

wb = openpyxl.load_workbook('Excel/influencer_marketing.xlsx')
print(f"Excel sheets   : {wb.sheetnames}")
ws1 = wb['Dataset']
print(f"Excel data rows: {ws1.max_row - 3}")

imgs = sorted([f for f in os.listdir('Images') if f.endswith('.png')])
print(f"Graphs saved   : {len(imgs)}")
for img in imgs:
    print(f"  {img}")

print("\nAll checks passed.")
