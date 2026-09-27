"""
src/evaluation.py
=================
Model evaluation metrics and prediction utilities.

Usage:
    from src.evaluation import evaluate_model, predict_new_campaigns
"""

import os
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

_HERE       = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_HERE)
PRED_DIR    = os.path.join(_ROOT, "outputs", "predictions")
METRICS_PATH = os.path.join(_ROOT, "outputs", "regression_metrics.json")

FEATURES = ["Engagement_Rate", "Campaign_Cost", "Product_Sales", "Campaign_Duration_Days"]


def evaluate_model(model, y_actual: pd.Series) -> dict:
    """
    Compute R2, Adjusted R2, MAE, RMSE and print summary.
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error

    y_pred = model.fittedvalues
    mae  = mean_absolute_error(y_actual, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_actual, y_pred)))

    result = {
        "R2":      round(model.rsquared, 6),
        "Adj_R2":  round(model.rsquared_adj, 6),
        "F_stat":  round(model.fvalue, 4),
        "F_pvalue": model.f_pvalue,
        "MAE":     round(mae, 6),
        "RMSE":    round(rmse, 6),
        "AIC":     round(model.aic, 4),
        "BIC":     round(model.bic, 4),
        "n":       int(model.nobs),
    }

    print("\nMODEL EVALUATION SUMMARY")
    print("=" * 50)
    for k, v in result.items():
        print(f"  {k:12s}: {v}")
    print("=" * 50)

    return result


def predict_new_campaigns(model, campaigns: pd.DataFrame,
                          features: list = None,
                          save: bool = True) -> pd.DataFrame:
    """
    Generate predictions with 95% prediction intervals for new campaigns.

    Parameters
    ----------
    model     : fitted OLS model
    campaigns : DataFrame with columns matching FEATURES
    features  : list of feature names (default FEATURES)
    save      : if True, saves predictions CSV to outputs/predictions/

    Returns
    -------
    DataFrame with Predicted_ROI, CI_Lower_95, CI_Upper_95 appended
    """
    if features is None:
        features = FEATURES

    X_new       = campaigns[features]
    X_new_const = sm.add_constant(X_new, has_constant="add")
    pred        = model.get_prediction(X_new_const)
    pred_frame  = pred.summary_frame(alpha=0.05)

    result = campaigns.copy()
    result["Predicted_ROI"] = pred_frame["mean"].values.round(4)
    result["CI_Lower_95"]   = pred_frame["obs_ci_lower"].values.round(4)
    result["CI_Upper_95"]   = pred_frame["obs_ci_upper"].values.round(4)

    if save:
        os.makedirs(PRED_DIR, exist_ok=True)
        out_path = os.path.join(PRED_DIR, "new_campaign_predictions.csv")
        result.to_csv(out_path, index=False)
        print(f"[eval] Predictions saved -> {out_path}")

    return result


def default_new_campaigns() -> pd.DataFrame:
    """
    Return a default set of 5 hypothetical new campaigns for demonstration.
    These use the same engineered feature values as training inputs.
    """
    return pd.DataFrame({
        "Campaign": [
            "Micro-Influencer Instagram",
            "Macro-Influencer YouTube",
            "TikTok Viral Campaign",
            "Twitter Tech Launch",
            "Long-Duration Fitness",
        ],
        "Engagement_Rate":        [8.5,   2.1,   15.3,  4.2,   6.8],
        "Campaign_Cost":          [30000, 90000, 50000, 25000, 45000],
        "Product_Sales":          [500,   1200,  800,   300,   700],
        "Campaign_Duration_Days": [14,    30,    7,     10,    60],
    })
