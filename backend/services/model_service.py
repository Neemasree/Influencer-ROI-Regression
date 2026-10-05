"""
backend/services/model_service.py
==================================
Thin wrapper around the existing predict_roi.py and regression.py modules.

The model is loaded ONCE at app startup and stored in the app context.
All prediction logic lives in src/predict_roi.py — this file only bridges
the HTTP layer to the existing statistical code.
"""

import os
import sys
import json
import math

# Ensure project root is on the Python path so src/ imports resolve
_HERE = os.path.dirname(os.path.abspath(__file__))         # backend/services/
_ROOT = os.path.dirname(os.path.dirname(_HERE))            # project root
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.predict_roi import (
    predict_single_campaign,
    compute_features,
    CPM,
    AVG_UNIT_VALUE,
    VALID_PLATFORMS,
    VALID_CATEGORIES,
    VALID_TYPES,
)
from src.regression import load_model, METRICS_PATH


# ── startup ───────────────────────────────────────────────────────────────────

def load_ols_model():
    """Load the pickled OLS model. Called once at app startup."""
    return load_model()


def load_metrics() -> dict:
    """Load regression_metrics.json. Called once at app startup."""
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ── prediction ────────────────────────────────────────────────────────────────

def run_prediction(payload: dict, model) -> dict:
    """
    Validate the incoming JSON payload, call the existing predict_single_campaign()
    from src/predict_roi.py, and return a clean response dict.

    Raises ValueError with a descriptive message on bad input.
    """
    # ── required field presence ───────────────────────────────────────────────
    required = ["platform", "influencer_category", "estimated_reach",
                "engagements", "product_sales", "campaign_duration_days"]
    missing = [f for f in required if payload.get(f) is None]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    platform      = str(payload["platform"]).strip()
    category      = str(payload["influencer_category"]).strip()
    campaign_type = str(payload.get("campaign_type", "Brand Awareness")).strip()

    # ── numeric coercions ─────────────────────────────────────────────────────
    try:
        estimated_reach        = int(payload["estimated_reach"])
        engagements            = int(payload["engagements"])
        product_sales          = int(payload["product_sales"])
        campaign_duration_days = int(payload["campaign_duration_days"])
    except (TypeError, ValueError):
        raise ValueError("estimated_reach, engagements, product_sales, and "
                         "campaign_duration_days must be integers.")

    # ── domain validation ─────────────────────────────────────────────────────
    if platform not in VALID_PLATFORMS:
        raise ValueError(f"Invalid platform '{platform}'. Valid: {VALID_PLATFORMS}")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid influencer_category '{category}'. "
                         f"Valid: {VALID_CATEGORIES}")
    if estimated_reach <= 0:
        raise ValueError("estimated_reach must be greater than 0.")
    if engagements < 0:
        raise ValueError("engagements cannot be negative.")
    if engagements > estimated_reach:
        raise ValueError("engagements cannot exceed estimated_reach.")
    if product_sales < 0:
        raise ValueError("product_sales cannot be negative.")
    if campaign_duration_days <= 0:
        raise ValueError("campaign_duration_days must be greater than 0.")

    # ── call existing prediction logic ────────────────────────────────────────
    result = predict_single_campaign(
        platform=platform,
        influencer_category=category,
        campaign_type=campaign_type,
        estimated_reach=estimated_reach,
        engagements=engagements,
        product_sales=product_sales,
        campaign_duration_days=campaign_duration_days,
        model=model,
    )

    predicted_roi = result["Predicted_ROI"]
    campaign_cost = result["Campaign_Cost"]
    revenue       = result["Revenue"]

    # estimated_return = revenue - campaign_cost
    estimated_return = round(revenue - campaign_cost, 2)

    return {
        "predicted_roi":      predicted_roi,
        "ci_lower_95":        result["CI_Lower_95"],
        "ci_upper_95":        result["CI_Upper_95"],
        "engagement_rate":    result["Engagement_Rate"],
        "campaign_cost":      campaign_cost,
        "estimated_revenue":  revenue,
        "estimated_return":   estimated_return,
        # echo inputs back for display
        "inputs": {
            "platform":               platform,
            "influencer_category":    category,
            "campaign_type":          campaign_type,
            "estimated_reach":        estimated_reach,
            "engagements":            engagements,
            "product_sales":          product_sales,
            "campaign_duration_days": campaign_duration_days,
        },
    }


# ── metrics formatting for /api/model ─────────────────────────────────────────

def format_model_info(metrics: dict) -> dict:
    """Return a clean, frontend-ready version of the metrics JSON."""
    coefs   = metrics.get("coefs", {})
    pvalues = metrics.get("pvalues", {})
    std_err = metrics.get("std_errors", {})
    t_stats = metrics.get("t_stats", {})
    ci_lo   = metrics.get("conf_int_lower", {})
    ci_hi   = metrics.get("conf_int_upper", {})

    features = metrics.get("features", [])

    coefficient_table = []
    for feat in features:
        p = pvalues.get(feat, 1.0)
        if p < 0.001:
            sig = "***"
        elif p < 0.01:
            sig = "**"
        elif p < 0.05:
            sig = "*"
        else:
            sig = "ns"

        interpretations = {
            "Engagement_Rate": "Positive association with ROI. Higher engagement rate is associated with higher predicted ROI, holding other predictors constant.",
            "Campaign_Cost":   "Negative association with ROI. Higher campaign cost is associated with lower predicted ROI, holding other predictors constant.",
            "Product_Sales":   "Positive association with ROI. More product sales are associated with higher predicted ROI, holding other predictors constant.",
            "Campaign_Duration_Days": "Not statistically significant at the 5% level (p = 0.916). Campaign duration alone is not a meaningful predictor of ROI in this model.",
        }

        coefficient_table.append({
            "predictor":       feat,
            "coefficient":     round(coefs.get(feat, 0), 6),
            "std_error":       round(std_err.get(feat, 0), 6),
            "t_statistic":     round(t_stats.get(feat, 0), 4),
            "p_value":         round(p, 6),
            "significance":    sig,
            "ci_lower":        round(ci_lo.get(feat, 0), 6),
            "ci_upper":        round(ci_hi.get(feat, 0), 6),
            "interpretation":  interpretations.get(feat, ""),
        })

    return {
        "algorithm":        "Ordinary Least Squares (OLS)",
        "library":          "Statsmodels",
        "target":           metrics.get("target", "ROI"),
        "features":         features,
        "observations":     metrics.get("observations", 147000),
        "r_squared":        round(metrics.get("r2", 0), 6),
        "adjusted_r_squared": round(metrics.get("adj_r2", 0), 6),
        "f_statistic":      round(metrics.get("f_stat", 0), 4),
        "f_pvalue":         metrics.get("f_pvalue", 0.0),
        "aic":              round(metrics.get("aic", 0), 4),
        "bic":              round(metrics.get("bic", 0), 4),
        "mae":              round(metrics.get("mae", 0), 6),
        "rmse":             round(metrics.get("rmse", 0), 6),
        "intercept":        round(coefs.get("const", 0), 6),
        "coefficients":     coefficient_table,
        "equation": {
            "intercept":              round(coefs.get("const", 0), 4),
            "Engagement_Rate":        round(coefs.get("Engagement_Rate", 0), 6),
            "Campaign_Cost":          round(coefs.get("Campaign_Cost", 0), 8),
            "Product_Sales":          round(coefs.get("Product_Sales", 0), 6),
            "Campaign_Duration_Days": round(coefs.get("Campaign_Duration_Days", 0), 6),
        },
    }
