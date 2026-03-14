"""
Insurance Fraud Detection API - Flask Application
Production-ready backend with CORS, logging, and error handling.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

from config import (
    MODEL_PATH,
    METRICS_PATH,
    LOGS_DIR,
    CLAIM_STATUSES,
)
from models import (
    init_database,
    create_claim,
    get_claim,
    get_claims,
    update_claim_status,
    save_prediction,
    generate_claim_id,
)
from validators import validate_claim_data
from fraud_model import get_model, MODEL_VERSION, FraudDetectionModel

# Setup logging
LOGS_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOGS_DIR / f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])


# Initialize model on startup
def init_model():
    """Load ML model if exists."""
    try:
        model = get_model(MODEL_PATH)
        logger.info(f"Model loaded from {MODEL_PATH}")
        return model
    except (FileNotFoundError, Exception) as e:
        logger.warning(f"Model not loaded: {e}. Run setup to train model.")
        return None


model = None


@app.before_request
def before_request():
    """Load model on first request."""
    global model
    if model is None:
        model = init_model()
    logger.info(f"API call: {request.method} {request.path}")


# ============ Helper functions ============


def get_model_info():
    """Get model metadata and metrics."""
    try:
        if METRICS_PATH.exists():
            with open(METRICS_PATH) as f:
                data = json.load(f)
            return data
    except Exception as e:
        logger.error(f"Error loading model info: {e}")
    return {}


# ============ API Endpoints ============


@app.route("/api/claims", methods=["POST"])
def post_claim():
    """
    Create a new claim.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        is_valid, errors = validate_claim_data(data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "errors": errors}), 400

        result = create_claim(data)
        logger.info(f"Claim created: {result['claim_id']}")
        return jsonify({
            "claim_id": result["claim_id"],
            "status": result["status"],
            "message": "Claim submitted successfully",
        }), 201
    except Exception as e:
        logger.exception("Error creating claim")
        return jsonify({"error": str(e)}), 500


@app.route("/api/claims", methods=["GET"])
def list_claims():
    """
    Get claims with pagination, filtering, and sorting.
    """
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        status = request.args.get("status")
        claim_type = request.args.get("claim_type")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        sort_by = request.args.get("sort_by", "date")
        sort_order = request.args.get("sort_order", "desc")
        search = request.args.get("search")

        result = get_claims(
            page=page,
            per_page=per_page,
            status=status,
            claim_type=claim_type,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
        )

        # Convert rows to serializable
        claims = []
        for c in result["claims"]:
            row = dict(c)
            for k, v in row.items():
                if hasattr(v, "isoformat"):
                    row[k] = v.isoformat() if v else None
            claims.append(row)

        return jsonify({
            "claims": claims,
            "total": result["total"],
            "page": result["page"],
            "pages": result["pages"],
        })
    except Exception as e:
        logger.exception("Error listing claims")
        return jsonify({"error": str(e)}), 500


@app.route("/api/claims/<claim_id>", methods=["GET"])
def get_claim_detail(claim_id):
    """
    Get single claim with prediction data.
    """
    try:
        claim = get_claim(claim_id)
        if not claim:
            return jsonify({"error": "Claim not found"}), 404

        # Serialize
        out = {}
        for k, v in claim.items():
            if hasattr(v, "isoformat"):
                out[k] = v.isoformat() if v else None
            elif isinstance(v, dict) and "prediction" in str(k):
                pass
            else:
                out[k] = v
        if "prediction" in claim:
            pred = claim["prediction"]
            out["prediction"] = {k: (v.isoformat() if hasattr(v, "isoformat") else v)
                                for k, v in pred.items()}
        else:
            out["prediction"] = None

        return jsonify(out)
    except Exception as e:
        logger.exception("Error fetching claim")
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict-fraud", methods=["POST"])
def predict_fraud():
    """
    Predict fraud probability for claim data.
    Optionally accepts claim_id to save prediction.
    """
    try:
        if model is None or getattr(model, "model", None) is None:
            return jsonify({"error": "ML model not loaded. Run setup to train model."}), 503

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        is_valid, errors = validate_claim_data(data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "errors": errors}), 400

        # Map frontend field names
        claim_data = {
            "claimant_name": data.get("claimant_name"),
            "claimant_age": data.get("claimant_age"),
            "claim_amount": data.get("claim_amount"),
            "claim_type": data.get("claim_type", "auto").lower(),
            "policy_duration_months": data.get("policy_duration_months"),
            "previous_claims_count": data.get("previous_claims_count", 0),
            "claim_description": data.get("claim_description", ""),
        }

        prob = model.predict_fraud_probability(claim_data)
        risk_level = model.get_risk_level(prob)
        explanation = model.explain_prediction(claim_data)
        feature_importance = model.get_feature_importance()

        # Save prediction if claim_id provided
        claim_id = data.get("claim_id")
        if claim_id:
            save_prediction(
                claim_id=claim_id,
                fraud_probability=prob,
                risk_level=risk_level,
                feature_importance=feature_importance,
                model_version=MODEL_VERSION,
            )
            logger.info(f"Prediction saved for claim {claim_id}: {risk_level} ({prob}%)")

        return jsonify({
            "probability": prob,
            "risk_level": risk_level,
            "feature_importance": feature_importance,
            "explanation": explanation,
            "claim_id": claim_id,
        })
    except Exception as e:
        logger.exception("Error in fraud prediction")
        return jsonify({"error": str(e)}), 500


@app.route("/api/claims/<claim_id>/status", methods=["PUT"])
def update_status(claim_id):
    """
    Update claim status.
    """
    try:
        data = request.get_json()
        if not data or "status" not in data:
            return jsonify({"error": "status is required"}), 400

        status = data["status"].lower()
        if status not in CLAIM_STATUSES:
            return jsonify({
                "error": f"Invalid status. Must be one of: {', '.join(CLAIM_STATUSES)}"
            }), 400

        claim = update_claim_status(claim_id, status)
        if not claim:
            return jsonify({"error": "Claim not found"}), 404

        return jsonify({
            "claim_id": claim_id,
            "status": claim["status"],
            "updated_at": claim["updated_at"],
        })
    except Exception as e:
        logger.exception("Error updating status")
        return jsonify({"error": str(e)}), 500


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """
    Get aggregate statistics.
    """
    try:
        from models import get_db_connection

        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM claims")
            total_claims = cursor.fetchone()[0]

            cursor.execute("""
                SELECT AVG(p.fraud_probability)
                FROM predictions p
                INNER JOIN (
                    SELECT claim_id, MAX(predicted_at) as max_at
                    FROM predictions GROUP BY claim_id
                ) latest ON p.claim_id = latest.claim_id AND p.predicted_at = latest.max_at
            """)
            avg_prob_row = cursor.fetchone()
            avg_fraud_prob = float(avg_prob_row[0]) if avg_prob_row and avg_prob_row[0] else 0

            cursor.execute("SELECT COUNT(*) FROM claims WHERE status = 'fraud'")
            fraud_count = cursor.fetchone()[0]
            fraud_rate = (fraud_count / total_claims * 100) if total_claims > 0 else 0

            cursor.execute("""
                SELECT COUNT(DISTINCT claim_id) FROM predictions
                WHERE risk_level IN ('high', 'critical')
            """)
            high_risk_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT claim_type, COUNT(*) as cnt
                FROM claims
                GROUP BY claim_type
            """)
            by_type_raw = cursor.fetchall()

            cursor.execute("""
                SELECT substr(submission_date, 1, 7) as month, COUNT(*) as cnt
                FROM claims
                GROUP BY month
                ORDER BY month
            """)
            by_month_raw = cursor.fetchall()

            cursor.execute("""
                SELECT status, COUNT(*) as cnt
                FROM claims
                GROUP BY status
            """)
            by_status_raw = cursor.fetchall()

        by_type = [{"claim_type": r[0], "count": r[1]} for r in by_type_raw]
        by_month = [{"month": r[0], "count": r[1]} for r in by_month_raw]
        by_status = [{"status": r[0], "count": r[1]} for r in by_status_raw]

        return jsonify({
            "total_claims": total_claims,
            "average_fraud_probability": round(avg_fraud_prob, 2),
            "fraud_rate": round(fraud_rate, 2),
            "high_risk_count": high_risk_count,
            "by_type": by_type,
            "by_month": by_month,
            "by_status": by_status,
        })
    except Exception as e:
        logger.exception("Error fetching statistics")
        return jsonify({"error": str(e)}), 500


@app.route("/api/model-info", methods=["GET"])
def model_info():
    """
    Get model performance metrics and version.
    """
    try:
        info = get_model_info()
        if not info and model:
            info = {
                "version": MODEL_VERSION,
                "accuracy": model.metrics.get("accuracy", 0),
                "precision": model.metrics.get("precision", 0),
                "recall": model.metrics.get("recall", 0),
                "f1_score": model.metrics.get("f1_score", 0),
                "roc_auc": model.metrics.get("roc_auc", 0),
                "feature_importance": model.get_feature_importance() if model else {},
            }
        return jsonify(info)
    except Exception as e:
        logger.exception("Error fetching model info")
        return jsonify({"error": str(e)}), 500


@app.route("/api/export/claims/csv", methods=["GET"])
def export_claims_csv():
    """Export claims as CSV."""
    try:
        from flask import Response
        import csv
        from io import StringIO

        result = get_claims(page=1, per_page=10000)
        claims = result["claims"]
        if not claims:
            return "No claims to export", 404

        si = StringIO()
        writer = csv.DictWriter(si, fieldnames=claims[0].keys())
        writer.writeheader()
        for c in claims:
            row = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in c.items()}
            writer.writerow(row)
        output = si.getvalue()
        return Response(output, mimetype="text/csv",
                       headers={"Content-Disposition": "attachment;filename=claims_export.csv"})
    except Exception as e:
        logger.exception("Export error")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "model_loaded": model is not None})


# ============ Error handlers ============


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.exception("Server error")
    return jsonify({"error": "Internal server error"}), 500


# ============ Entry point ============

if __name__ == "__main__":
    init_database()
    port = int(__import__("os").environ.get("API_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
