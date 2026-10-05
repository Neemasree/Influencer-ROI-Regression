from flask import Blueprint, jsonify, current_app
from backend.services.data_service import get_dashboard_stats

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/dashboard")
def dashboard():
    df      = current_app.config["DATASET"]
    metrics = current_app.config["METRICS"]

    stats = get_dashboard_stats(df)

    # merge model metrics from JSON (not hardcoded)
    stats["r_squared"]        = metrics.get("r2")
    stats["adjusted_r_squared"] = metrics.get("adj_r2")
    stats["mae"]              = metrics.get("mae")
    stats["rmse"]             = metrics.get("rmse")
    stats["f_statistic"]      = metrics.get("f_stat")
    stats["observations"]     = metrics.get("observations")

    return jsonify(stats)
