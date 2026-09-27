"""
src/regression.py
=================
OLS multiple linear regression using Statsmodels.
Fits the model on ALL processed observations (n=147,000).
Saves the fitted model using Statsmodels' built-in pickle wrapper.

Usage:
    from src.regression import fit_model, load_model, get_metrics
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import statsmodels.api as sm

_HERE      = os.path.dirname(os.path.abspath(__file__))
_ROOT      = os.path.dirname(_HERE)
MODEL_PATH  = os.path.join(_ROOT, "outputs", "ols_model.pkl")
METRICS_PATH = os.path.join(_ROOT, "outputs", "regression_metrics.json")

FEATURES = ["Engagement_Rate", "Campaign_Cost", "Product_Sales", "Campaign_Duration_Days"]
TARGET   = "ROI"


def fit_model(df: pd.DataFrame,
              features: list = None,
              target: str = TARGET,
              save: bool = True):
    """
    Fit OLS on ALL rows of df. No sampling.

    Parameters
    ----------
    df       : processed DataFrame (147,000 rows)
    features : list of predictor column names
    target   : dependent variable column name
    save     : if True, saves model and metrics to outputs/

    Returns
    -------
    model : fitted OLS results object
    """
    if features is None:
        features = FEATURES

    print(f"\n[regression] Fitting OLS on n = {len(df):,} observations")
    print(f"             Features : {features}")
    print(f"             Target   : {target}")

    X = df[features]
    y = df[target]
    X_const = sm.add_constant(X)

    model = sm.OLS(y, X_const).fit()

    print("\n" + model.summary().as_text())

    if save:
        _save_model(model)
        _save_metrics(model, df, y, features)

    return model


def _save_model(model) -> None:
    """Persist the fitted model with pickle (Statsmodels-compatible)."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"[regression] Model saved -> {MODEL_PATH}")


def load_model():
    """Load the previously saved fitted model."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"No saved model found at {MODEL_PATH}. "
            "Run fit_model() first."
        )
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print(f"[regression] Model loaded from {MODEL_PATH}")
    return model


def _save_metrics(model, df: pd.DataFrame, y: pd.Series, features: list) -> None:
    """Compute evaluation metrics and save to JSON."""
    from sklearn.metrics import mean_absolute_error, mean_squared_error

    y_pred = model.fittedvalues
    mae    = mean_absolute_error(y, y_pred)
    rmse   = float(np.sqrt(mean_squared_error(y, y_pred)))
    conf   = model.conf_int()

    metrics = {
        "observations": int(model.nobs),
        "r2":           round(model.rsquared, 6),
        "adj_r2":       round(model.rsquared_adj, 6),
        "f_stat":       round(model.fvalue, 4),
        "f_pvalue":     model.f_pvalue,
        "aic":          round(model.aic, 4),
        "bic":          round(model.bic, 4),
        "mae":          round(mae, 6),
        "rmse":         round(rmse, 6),
        "features":     features,
        "target":       TARGET,
        "coefs":        {k: round(v, 8) for k, v in model.params.to_dict().items()},
        "std_errors":   {k: round(v, 8) for k, v in model.bse.to_dict().items()},
        "t_stats":      {k: round(v, 6) for k, v in model.tvalues.to_dict().items()},
        "pvalues":      {k: round(v, 8) for k, v in model.pvalues.to_dict().items()},
        "conf_int_lower": {k: round(conf.loc[k, 0], 8) for k in model.params.index},
        "conf_int_upper": {k: round(conf.loc[k, 1], 8) for k in model.params.index},
    }

    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Also keep a copy in data/processed/ for backward compatibility
    alt = os.path.join(_ROOT, "data", "processed", "regression_metrics.json")
    with open(alt, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[regression] Metrics saved -> {METRICS_PATH}")
    print(f"             R2={metrics['r2']:.4f}  Adj-R2={metrics['adj_r2']:.4f}  "
          f"F={metrics['f_stat']:.2f}  MAE={metrics['mae']:.4f}  RMSE={metrics['rmse']:.4f}")


def get_metrics() -> dict:
    """Load and return saved metrics dict."""
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def print_equation(metrics: dict) -> None:
    """Print the final regression equation from saved metrics."""
    c = metrics["coefs"]
    print("\nFINAL REGRESSION EQUATION")
    print("-" * 52)
    print(f"ROI = {c['const']:.4f}")
    for feat in metrics["features"]:
        sign = "+" if c[feat] >= 0 else "-"
        print(f"    {sign} {abs(c[feat]):.6f}  x  {feat}")
    print()
    print(f"  R2          = {metrics['r2']:.4f}")
    print(f"  Adjusted R2 = {metrics['adj_r2']:.4f}")
    print(f"  F-statistic = {metrics['f_stat']:.2f}  (p < 0.001)")
    print(f"  MAE         = {metrics['mae']:.4f}")
    print(f"  RMSE        = {metrics['rmse']:.4f}")
    print(f"  n           = {metrics['observations']:,}")
