"""
routes/api.py  —  REST API endpoints (used by frontend JS)
"""

from flask import Blueprint, jsonify, session, request
from database.db import get_db
from utils.helpers import login_required
from ml.predictor import predict_renewal, get_ai_insights

api_bp = Blueprint("api", __name__)


@api_bp.route("/policies")
@login_required
def api_policies():
    db  = get_db()
    uid = session["user_id"]
    rows = db.execute(
        "SELECT * FROM policies WHERE user_id=?", (uid,)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@api_bp.route("/predict/<int:uid>")
@login_required
def api_predict(uid):
    db      = get_db()
    policies= db.execute("SELECT * FROM policies WHERE user_id=?", (uid,)).fetchall()
    db.close()
    result  = get_ai_insights(uid, policies)
    return jsonify(result)


@api_bp.route("/stats")
@login_required
def api_stats():
    db  = get_db()
    uid = session["user_id"]
    data = {
        "active":   db.execute("SELECT COUNT(*) FROM policies WHERE user_id=? AND status='active'",   (uid,)).fetchone()[0],
        "expiring": db.execute("SELECT COUNT(*) FROM policies WHERE user_id=? AND status='expiring'", (uid,)).fetchone()[0],
        "expired":  db.execute("SELECT COUNT(*) FROM policies WHERE user_id=? AND status='expired'",  (uid,)).fetchone()[0],
        "premium":  db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE user_id=? AND status='success'", (uid,)).fetchone()[0],
    }
    db.close()
    return jsonify(data)
