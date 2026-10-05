from flask import Blueprint, jsonify, current_app
from backend.services.model_service import format_model_info

model_bp = Blueprint("model", __name__)


@model_bp.get("/model")
def model_info():
    metrics = current_app.config["METRICS"]
    return jsonify(format_model_info(metrics))
