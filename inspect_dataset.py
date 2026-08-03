import pandas as pd

path = r'C:\Users\Neema Sree\OneDrive\python\Documents\Desktop\predaa-dataset\influencer_marketing_roi_dataset.csv'
df = pd.read_csv(path)

print(f'Rows    : {len(df)}')
print(f'Columns : {len(df.columns)}')
print()
print('Column Names and Types:')
for col in df.columns:
    print(f'  {col}  —  {df[col].dtype}')
print()
print('First 3 rows:')
print(df.head(3).to_string())
print()
print('Missing values per column:')
print(df.isnull().sum().to_string())
print()
print('Basic stats:')
print(df.describe().round(2).to_string())
