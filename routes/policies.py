"""
routes/policies.py  —  View and manage policies
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from database.db import get_db
from utils.helpers import login_required
from datetime import date, datetime

policies_bp = Blueprint("policies", __name__)


def days_until(expiry_str):
    try:
        exp = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        return (exp - date.today()).days
    except Exception:
        return 999


@policies_bp.route("/policies")
@login_required
def my_policies():
    db  = get_db()
    uid = session["user_id"]

    rows = db.execute(
        "SELECT * FROM policies WHERE user_id = ? ORDER BY expiry_date ASC", (uid,)
    ).fetchall()
    db.close()

    # Annotate days_left
    policies = []
    for p in rows:
        d = dict(p)
        d["days_left"] = days_until(p["expiry_date"])
        policies.append(d)

    return render_template("policies.html", policies=policies)


@policies_bp.route("/policies/<int:pid>")
@login_required
def policy_detail(pid):
    db  = get_db()
    uid = session["user_id"]

    policy = db.execute(
        "SELECT * FROM policies WHERE id=? AND user_id=?", (pid, uid)
    ).fetchone()

    if not policy:
        flash("Policy not found.", "danger")
        return redirect(url_for("policies.my_policies"))

    renewals = db.execute(
        "SELECT * FROM renewals WHERE policy_id=? ORDER BY renewal_date DESC", (pid,)
    ).fetchall()
    db.close()

    d = dict(policy)
    d["days_left"] = days_until(policy["expiry_date"])

    return render_template("policy_detail.html", policy=d, renewals=renewals)
