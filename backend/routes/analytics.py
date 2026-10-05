from flask import Blueprint, jsonify, request, current_app
from backend.services.data_service import (
    get_platform_analytics,
    get_category_analytics,
    get_campaign_type_analytics,
    get_monthly_analytics,
    get_correlation_data,
    get_scatter_data,
    get_roi_histogram,
)

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/analytics/platform")
def platform():
    df = current_app.config["DATASET"]
    return jsonify(get_platform_analytics(df))


@analytics_bp.get("/analytics/category")
def category():
    df = current_app.config["DATASET"]
    return jsonify(get_category_analytics(df))


@analytics_bp.get("/analytics/campaign-type")
def campaign_type():
    df = current_app.config["DATASET"]
    return jsonify(get_campaign_type_analytics(df))


@analytics_bp.get("/analytics/monthly")
def monthly():
    df = current_app.config["DATASET"]
    return jsonify(get_monthly_analytics(df))


@analytics_bp.get("/analytics/correlation")
def correlation():
    df = current_app.config["DATASET"]
    return jsonify(get_correlation_data(df))


@analytics_bp.get("/analytics/scatter")
def scatter():
    """
    Returns sampled scatter data.
    Query params: x_col (required), sample_n (default 3000)
    """
    df    = current_app.config["DATASET"]
    x_col = request.args.get("x_col", "Engagement_Rate")
    y_col = request.args.get("y_col", "ROI")
    try:
        sample_n = int(request.args.get("sample_n", 3000))
        sample_n = min(sample_n, 5000)
    except ValueError:
        sample_n = 3000

    data = get_scatter_data(df, x_col, y_col, sample_n)
    return jsonify({"x_col": x_col, "y_col": y_col, "data": data})


@analytics_bp.get("/analytics/roi-histogram")
def roi_histogram():
    df = current_app.config["DATASET"]
    try:
        bins = int(request.args.get("bins", 50))
        bins = min(max(bins, 10), 100)
    except ValueError:
        bins = 50
    return jsonify(get_roi_histogram(df, bins))
