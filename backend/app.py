"""
backend/app.py
==============
Flask application entry-point for the Influencer ROI Analytics API.

Startup sequence:
  1. Load processed dataset (147,000 rows) into memory — once
  2. Load the saved OLS model (outputs/ols_model.pkl) — once
  3. Load regression_metrics.json — once
  4. Register all route blueprints under /api
  5. Start the Flask dev server

Run:
    python backend/app.py
"""

import os
import sys

# ── ensure project root is on the path ────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))   # backend/
_ROOT = os.path.dirname(_HERE)                        # project root
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

from backend.services.model_service import load_ols_model, load_metrics
from backend.routes.health    import health_bp
from backend.routes.dashboard import dashboard_bp
from backend.routes.analytics import analytics_bp
from backend.routes.model     import model_bp
from backend.routes.predict   import predict_bp
from backend.routes.campaigns import campaigns_bp

# ── paths ──────────────────────────────────────────────────────────────────────
PROC_CSV = os.path.join(_ROOT, "data", "processed",
                        "influencer_roi_analysis_dataset.csv")


def create_app() -> Flask:
    app = Flask(__name__)

    # ── CORS: allow Vite dev server and same-origin ───────────────────────────
    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]}})

    # ── load shared resources once ────────────────────────────────────────────
    print("[startup] Loading processed dataset …", flush=True)
    df = pd.read_csv(PROC_CSV, parse_dates=["Start_Date", "End_Date"])
    print(f"[startup] Dataset loaded: {len(df):,} rows x {len(df.columns)} columns",
          flush=True)

    print("[startup] Loading OLS model …", flush=True)
    model = load_ols_model()
    print("[startup] Model loaded.", flush=True)

    print("[startup] Loading regression metrics …", flush=True)
    metrics = load_metrics()
    print(f"[startup] Metrics loaded (R²={metrics['r2']}, n={metrics['observations']:,}).",
          flush=True)

    # ── store in app config (thread-safe for read-only access) ────────────────
    app.config["DATASET"] = df
    app.config["MODEL"]   = model
    app.config["METRICS"] = metrics

    # ── register blueprints under /api ────────────────────────────────────────
    prefix = "/api"
    app.register_blueprint(health_bp,    url_prefix=prefix)
    app.register_blueprint(dashboard_bp, url_prefix=prefix)
    app.register_blueprint(analytics_bp, url_prefix=prefix)
    app.register_blueprint(model_bp,     url_prefix=prefix)
    app.register_blueprint(predict_bp,   url_prefix=prefix)
    app.register_blueprint(campaigns_bp, url_prefix=prefix)

    # ── 404 / 405 JSON handlers ───────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error."}), 500

    print("[startup] All routes registered. API ready.", flush=True)
    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  Influencer ROI Analytics API")
    print(f"  Running on http://localhost:{port}/api")
    print(f"  Health check: http://localhost:{port}/api/health\n")
    app.run(host="0.0.0.0", port=port, debug=True)
