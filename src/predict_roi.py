"""
src/predict_roi.py
==================
Predict ROI for a new influencer marketing campaign using the trained OLS model.

The feature engineering applied here is IDENTICAL to what was used during training:
    Engagement_Rate = (Engagements / Estimated_Reach) * 100
    Campaign_Cost   = (Estimated_Reach * Platform_CPM) / 1000
    Revenue         = Product_Sales * Category_Avg_Unit_Value
    ROI (predicted) = model output

Usage (interactive):
    python src/predict_roi.py

Usage (as a function):
    from src.predict_roi import predict_single_campaign, predict_batch
    result = predict_single_campaign(
        platform="Instagram",
        influencer_category="Beauty",
        campaign_type="Product Launch",
        estimated_reach=500000,
        engagements=45000,
        product_sales=800,
        campaign_duration_days=14,
    )
    print(result)
"""

import os
import sys
import pandas as pd
import statsmodels.api as sm

# ── ensure root is on path so src/ imports work when run directly ──────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.regression import load_model

# ── Lookup tables (MUST match process_data.py exactly) ────────────────────────
CPM = {
    "Instagram": 150,
    "YouTube":   120,
    "TikTok":    100,
    "Twitter":    80,
}

AVG_UNIT_VALUE = {
    "Beauty":  1500,
    "Tech":    5000,
    "Fashion": 1200,
    "Food":     300,
    "Fitness":  800,
    "Travel":  3000,
    "Gaming":  1000,
}

FEATURES = ["Engagement_Rate", "Campaign_Cost", "Product_Sales", "Campaign_Duration_Days"]

VALID_PLATFORMS   = list(CPM.keys())
VALID_CATEGORIES  = list(AVG_UNIT_VALUE.keys())
VALID_TYPES       = ["Brand Awareness", "Product Launch", "Giveaway",
                     "Seasonal Sale", "Event Promotion"]


# ── Feature engineering (mirrors training pipeline exactly) ────────────────────

def compute_features(platform: str,
                     influencer_category: str,
                     estimated_reach: int,
                     engagements: int,
                     product_sales: int,
                     campaign_duration_days: int) -> dict:
    """
    Compute the four engineered features from raw campaign inputs.
    Uses the same formulas and lookup tables as the training pipeline.

    Returns a dict of computed feature values.
    """
    if platform not in CPM:
        raise ValueError(f"Unknown platform '{platform}'. Valid: {VALID_PLATFORMS}")
    if influencer_category not in AVG_UNIT_VALUE:
        raise ValueError(f"Unknown category '{influencer_category}'. Valid: {VALID_CATEGORIES}")
    if estimated_reach <= 0:
        raise ValueError("estimated_reach must be > 0")

    engagement_rate = (engagements / estimated_reach) * 100
    campaign_cost   = (estimated_reach * CPM[platform]) / 1000
    revenue         = product_sales * AVG_UNIT_VALUE[influencer_category]

    return {
        "Engagement_Rate":        round(engagement_rate, 4),
        "Campaign_Cost":          round(campaign_cost, 2),
        "Revenue":                round(revenue, 2),
        "Product_Sales":          product_sales,
        "Campaign_Duration_Days": campaign_duration_days,
    }


def predict_single_campaign(platform: str,
                             influencer_category: str,
                             campaign_type: str,
                             estimated_reach: int,
                             engagements: int,
                             product_sales: int,
                             campaign_duration_days: int,
                             model=None) -> dict:
    """
    Predict ROI for one campaign with a 95% prediction interval.

    Parameters
    ----------
    platform               : 'Instagram', 'YouTube', 'TikTok', or 'Twitter'
    influencer_category    : 'Beauty', 'Tech', 'Fashion', 'Food', 'Fitness', 'Travel', 'Gaming'
    campaign_type          : campaign strategy label (informational only)
    estimated_reach        : unique users estimated to see the campaign
    engagements            : total interactions (likes, comments, shares, saves)
    product_sales          : product units sold attributed to the campaign
    campaign_duration_days : length of the campaign in days
    model                  : optional pre-loaded model; loads from disk if None

    Returns
    -------
    dict with input summary, computed features, predicted ROI, and 95% PI
    """
    if model is None:
        model = load_model()

    feats = compute_features(
        platform, influencer_category, estimated_reach,
        engagements, product_sales, campaign_duration_days
    )

    X_new = pd.DataFrame([{
        "Engagement_Rate":        feats["Engagement_Rate"],
        "Campaign_Cost":          feats["Campaign_Cost"],
        "Product_Sales":          feats["Product_Sales"],
        "Campaign_Duration_Days": feats["Campaign_Duration_Days"],
    }])
    X_new_const = sm.add_constant(X_new, has_constant="add")

    pred       = model.get_prediction(X_new_const)
    pred_frame = pred.summary_frame(alpha=0.05)

    predicted_roi = round(float(pred_frame["mean"].iloc[0]), 4)
    ci_lower      = round(float(pred_frame["obs_ci_lower"].iloc[0]), 4)
    ci_upper      = round(float(pred_frame["obs_ci_upper"].iloc[0]), 4)

    return {
        # Inputs
        "Platform":               platform,
        "Influencer_Category":    influencer_category,
        "Campaign_Type":          campaign_type,
        "Estimated_Reach":        estimated_reach,
        "Engagements":            engagements,
        "Product_Sales":          product_sales,
        "Campaign_Duration_Days": campaign_duration_days,
        # Computed features (identical to training)
        "Engagement_Rate":        feats["Engagement_Rate"],
        "Campaign_Cost":          feats["Campaign_Cost"],
        "Revenue":                feats["Revenue"],
        # Prediction
        "Predicted_ROI":          predicted_roi,
        "CI_Lower_95":            ci_lower,
        "CI_Upper_95":            ci_upper,
    }


def predict_batch(campaigns: list, model=None) -> pd.DataFrame:
    """
    Predict ROI for a list of campaign dicts.
    Each dict must have the same keys as predict_single_campaign parameters.

    Returns a DataFrame with all inputs, features, and predictions.
    """
    if model is None:
        model = load_model()

    results = []
    for camp in campaigns:
        result = predict_single_campaign(model=model, **camp)
        results.append(result)

    return pd.DataFrame(results)


def _print_result(result: dict) -> None:
    """Print a formatted prediction result."""
    print()
    print("=" * 58)
    print("  CAMPAIGN ROI PREDICTION")
    print("=" * 58)
    print(f"  Platform             : {result['Platform']}")
    print(f"  Influencer Category  : {result['Influencer_Category']}")
    print(f"  Campaign Type        : {result['Campaign_Type']}")
    print(f"  Estimated Reach      : {result['Estimated_Reach']:,}")
    print(f"  Engagements          : {result['Engagements']:,}")
    print(f"  Product Sales        : {result['Product_Sales']:,}")
    print(f"  Duration (days)      : {result['Campaign_Duration_Days']}")
    print("-" * 58)
    print("  COMPUTED FEATURES (same as training pipeline)")
    print(f"  Engagement Rate      : {result['Engagement_Rate']:.4f} %")
    print(f"  Campaign Cost (INR)  : {result['Campaign_Cost']:,.2f}")
    print(f"  Revenue (INR)        : {result['Revenue']:,.2f}")
    print("-" * 58)
    print(f"  PREDICTED ROI        : {result['Predicted_ROI']:.4f}")
    print(f"  95% Prediction Interval: [{result['CI_Lower_95']:.4f}, {result['CI_Upper_95']:.4f}]")
    print("=" * 58)
    print()
    print("  NOTE: This prediction is based on the OLS regression model")
    print("  fitted on 147,000 processed campaign observations.")
    print("  A wide prediction interval reflects high ROI variance in the data.")
    print()


def _interactive_mode() -> None:
    """Run an interactive command-line prediction session."""
    print()
    print("=" * 58)
    print("  INFLUENCER MARKETING ROI PREDICTOR")
    print("  Model: OLS Regression (Statsmodels)  n=147,000")
    print("=" * 58)

    print(f"\n  Valid platforms   : {', '.join(VALID_PLATFORMS)}")
    print(f"  Valid categories  : {', '.join(VALID_CATEGORIES)}")
    print(f"  Valid types       : {', '.join(VALID_TYPES)}")
    print()

    try:
        platform   = input("  Platform           : ").strip()
        category   = input("  Influencer Category: ").strip()
        camp_type  = input("  Campaign Type      : ").strip()
        reach      = int(input("  Estimated Reach    : ").strip())
        engage     = int(input("  Engagements        : ").strip())
        sales      = int(input("  Product Sales      : ").strip())
        duration   = int(input("  Duration (days)    : ").strip())
    except (ValueError, EOFError) as e:
        print(f"\n  Input error: {e}")
        return

    try:
        model  = load_model()
        result = predict_single_campaign(
            platform=platform,
            influencer_category=category,
            campaign_type=camp_type,
            estimated_reach=reach,
            engagements=engage,
            product_sales=sales,
            campaign_duration_days=duration,
            model=model,
        )
        _print_result(result)
    except (ValueError, FileNotFoundError) as e:
        print(f"\n  Error: {e}")


if __name__ == "__main__":
    _interactive_mode()
