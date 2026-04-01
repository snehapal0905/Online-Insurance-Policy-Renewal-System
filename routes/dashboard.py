"""
routes/dashboard.py  —  Customer Dashboard
"""

from flask import Blueprint, render_template, session
from database.db import get_db
from utils.helpers import login_required
from ml.predictor import get_ai_insights
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    db      = get_db()
    uid     = session["user_id"]

    # Summary counts
    policies = db.execute(
        "SELECT * FROM policies WHERE user_id = ? ORDER BY expiry_date ASC", (uid,)
    ).fetchall()

    active_count   = sum(1 for p in policies if p["status"] in ("active", "expiring"))
    expiring_count = sum(1 for p in policies if p["status"] == "expiring")

    # Total premium paid
    total_premium = db.execute(
        "SELECT COALESCE(SUM(amount),0) AS t FROM payments WHERE user_id=? AND status='success'",
        (uid,)
    ).fetchone()["t"]

    # Renewal count
    renewal_count = db.execute(
        "SELECT COUNT(*) AS c FROM renewals WHERE user_id=? AND status='completed'", (uid,)
    ).fetchone()["c"]

    # Recent transactions (last 5)
    transactions = db.execute(
        """SELECT py.*, p.name AS policy_name, p.type
           FROM payments py
           JOIN policies p ON p.id = py.policy_id
           WHERE py.user_id = ?
           ORDER BY py.payment_date DESC LIMIT 5""",
        (uid,)
    ).fetchall()

    # Monthly renewal chart data (last 12 months)
    chart_data = db.execute(
        """SELECT strftime('%b', payment_date) AS month,
                  SUM(amount) AS revenue, COUNT(*) AS count
           FROM payments
           WHERE user_id=? AND status='success'
           GROUP BY strftime('%Y-%m', payment_date)
           ORDER BY payment_date ASC LIMIT 12""",
        (uid,)
    ).fetchall()

    db.close()

    ai = get_ai_insights(uid, policies)

    return render_template(
        "dashboard.html",
        policies=policies,
        active_count=active_count,
        expiring_count=expiring_count,
        total_premium=total_premium,
        renewal_count=renewal_count,
        transactions=transactions,
        chart_data=chart_data,
        ai=ai,
    )
