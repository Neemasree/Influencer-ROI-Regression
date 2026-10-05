from flask import Blueprint, jsonify, request, current_app, Response
from backend.services.data_service import get_campaigns, get_filter_values
import csv
import io

campaigns_bp = Blueprint("campaigns", __name__)


@campaigns_bp.get("/campaigns")
def campaigns():
    df = current_app.config["DATASET"]

    platform      = request.args.get("platform")      or None
    category      = request.args.get("category")      or None
    campaign_type = request.args.get("campaign_type") or None
    search        = request.args.get("search")        or None
    sort_by       = request.args.get("sort_by", "ROI")
    sort_dir      = request.args.get("sort_dir", "desc")

    try:
        year  = int(request.args.get("year"))  if request.args.get("year")  else None
        month = int(request.args.get("month")) if request.args.get("month") else None
        page  = max(1, int(request.args.get("page",  1)))
        limit = min(100, max(1, int(request.args.get("limit", 25))))
    except (ValueError, TypeError):
        return jsonify({"error": "page, limit, year, and month must be integers."}), 400

    result = get_campaigns(
        df,
        platform=platform,
        category=category,
        campaign_type=campaign_type,
        year=year,
        month=month,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        limit=limit,
    )
    return jsonify(result)


@campaigns_bp.get("/campaigns/export")
def export_campaigns():
    """Export current filtered results as CSV (max 10,000 rows)."""
    df = current_app.config["DATASET"]

    platform      = request.args.get("platform")      or None
    category      = request.args.get("category")      or None
    campaign_type = request.args.get("campaign_type") or None
    search        = request.args.get("search")        or None
    sort_by       = request.args.get("sort_by", "ROI")
    sort_dir      = request.args.get("sort_dir", "desc")

    try:
        year  = int(request.args.get("year"))  if request.args.get("year")  else None
        month = int(request.args.get("month")) if request.args.get("month") else None
    except (ValueError, TypeError):
        year = month = None

    # use limit=10000 for export, page=1
    result = get_campaigns(
        df,
        platform=platform,
        category=category,
        campaign_type=campaign_type,
        year=year,
        month=month,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=1,
        limit=10000,
    )

    rows = result["data"]
    if not rows:
        return jsonify({"error": "No data to export."}), 404

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=campaigns_export.csv"},
    )


@campaigns_bp.get("/filters")
def filters():
    df = current_app.config["DATASET"]
    return jsonify(get_filter_values(df))
