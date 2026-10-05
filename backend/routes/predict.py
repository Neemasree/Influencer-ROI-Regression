from flask import Blueprint, jsonify, request, current_app
from backend.services.model_service import run_prediction

predict_bp = Blueprint("predict", __name__)


@predict_bp.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Request body must be JSON."}), 400

    model = current_app.config["MODEL"]

    try:
        result = run_prediction(payload, model)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
