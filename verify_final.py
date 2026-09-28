"""Final verification script."""
import os, json, sys

root = os.path.dirname(os.path.abspath(__file__))

required = [
    "data/raw/influencer_marketing_roi_dataset.csv",
    "data/processed/influencer_roi_analysis_dataset.csv",
    "data/processed/regression_metrics.json",
    "notebooks/analysis.ipynb",
    "src/__init__.py",
    "src/process_data.py",
    "src/statistics.py",
    "src/regression.py",
    "src/visualization.py",
    "src/evaluation.py",
    "src/predict_roi.py",
    "outputs/ols_model.pkl",
    "outputs/regression_metrics.json",
    "outputs/predictions/new_campaign_predictions.csv",
    "excel/influencer_marketing.xlsx",
    "run_pipeline.py",
    "requirements.txt",
    "README.md",
]

print("FILE EXISTENCE CHECK")
print("=" * 55)
all_ok = True
for f in required:
    path = os.path.join(root, f.replace("/", os.sep))
    ok = os.path.isfile(path)
    if not ok:
        all_ok = False
    print(f"  {'OK ' if ok else 'MISSING'} : {f}")

figs = sorted(f for f in os.listdir(os.path.join(root, "outputs", "figures"))
              if f.endswith(".png"))
print(f"\n  Charts in outputs/figures/ : {len(figs)}")
for f in figs:
    print(f"    {f}")

m = json.load(open(os.path.join(root, "outputs", "regression_metrics.json"),
                   encoding="utf-8"))
print("\nMETRICS JSON")
print(f"  n (observations) : {m['observations']:,}")
print(f"  R2               : {m['r2']}")
print(f"  Adjusted R2      : {m['adj_r2']}")
print(f"  F-statistic      : {m['f_stat']}")
print(f"  MAE              : {m['mae']}")
print(f"  RMSE             : {m['rmse']}")

print("\nSAMPLING CHECK (no 15,000 sample)")
import subprocess
result = subprocess.run(
    ["python", "-c",
     "import ast,os; "
     "src = open(os.path.join(r'" + root.replace("\\","\\\\") + r"','run_pipeline.py')).read(); "
     "print('sample(n=15000' in src)"],
    capture_output=True, text=True
)
print(f"  run_pipeline.py contains 'sample(n=15000': {result.stdout.strip()}")

print("\nSYNTHETIC DATA CHECK")
arch = os.path.join(root, "archive", "old_synthetic_dataset")
if os.path.isdir(arch):
    for f in os.listdir(arch):
        print(f"  ARCHIVED (not in pipeline): {f}")

print(f"\nALL FILES PRESENT: {all_ok}")
sys.exit(0 if all_ok else 1)
