"""
routes/renewal.py  —  Policy Renewal + Payment Simulation
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db import get_db
from utils.helpers import login_required
from datetime import date, datetime, timedelta
import uuid

renewal_bp = Blueprint("renewal", __name__)


@renewal_bp.route("/renew")
@login_required
def renew_list():
    db  = get_db()
    uid = session["user_id"]

    # Policies expiring within 60 days or already expired
    policies = db.execute(
        """SELECT *, 
           CAST(julianday(expiry_date) - julianday('now') AS INTEGER) AS days_left
           FROM policies
           WHERE user_id = ? AND status IN ('expiring','expired','active')
           ORDER BY expiry_date ASC""",
        (uid,)
    ).fetchall()
    db.close()

    return render_template("renew_list.html", policies=policies)


@renewal_bp.route("/renew/<int:pid>", methods=["GET", "POST"])
@login_required
def renew_policy(pid):
    db  = get_db()
    uid = session["user_id"]

    policy = db.execute(
        "SELECT * FROM policies WHERE id=? AND user_id=?", (pid, uid)
    ).fetchone()

    if not policy:
        flash("Policy not found.", "danger")
        db.close()
        return redirect(url_for("renewal.renew_list"))

    if request.method == "POST":
        step           = request.form.get("step", "1")
        payment_method = request.form.get("payment_method", "UPI")
        addon_total    = float(request.form.get("addon_total", 0))
        total_amount   = policy["premium"] + addon_total

        # Simulate payment processing
        txn_id = "TXN-" + str(uuid.uuid4())[:8].upper()

        # Record payment
        db.execute(
            """INSERT INTO payments (user_id, policy_id, amount, payment_date, status, transaction_id, payment_method)
               VALUES (?, ?, ?, ?, 'success', ?, ?)""",
            (uid, pid, total_amount, date.today().isoformat(), txn_id, payment_method)
        )

        # Record renewal
        new_expiry = _extend_expiry(policy["expiry_date"])
        db.execute(
            """INSERT INTO renewals (policy_id, user_id, renewal_date, amount_paid, status, transaction_id)
               VALUES (?, ?, ?, ?, 'completed', ?)""",
            (pid, uid, date.today().isoformat(), total_amount, txn_id)
        )

        # Update policy
        db.execute(
            "UPDATE policies SET expiry_date=?, status='active' WHERE id=?",
            (new_expiry, pid)
        )
        db.commit()
        db.close()

        flash(f"Policy renewed successfully! Transaction ID: {txn_id}", "success")
        return redirect(url_for("renewal.renewal_success", txn=txn_id, pid=pid, amt=int(total_amount)))

    db.close()
    return render_template("renew_policy.html", policy=dict(policy))


@renewal_bp.route("/renew/success")
@login_required
def renewal_success():
    txn = request.args.get("txn", "")
    pid = request.args.get("pid", "")
    amt = request.args.get("amt", "")
    return render_template("renewal_success.html", txn=txn, pid=pid, amt=amt)


def _extend_expiry(current_expiry_str):
    """Add 1 year to the expiry date."""
    try:
        exp = datetime.strptime(current_expiry_str, "%Y-%m-%d").date()
        # If already expired, start from today
        if exp < date.today():
            exp = date.today()
        return (exp + timedelta(days=365)).isoformat()
    except Exception:
        return (date.today() + timedelta(days=365)).isoformat()
