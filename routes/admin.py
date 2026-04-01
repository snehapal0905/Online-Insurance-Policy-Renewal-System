"""
routes/admin.py  —  Admin Panel
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from database.db import get_db
from utils.helpers import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()

    stats = {
        "total_users":    db.execute("SELECT COUNT(*) FROM users WHERE role='customer'").fetchone()[0],
        "total_policies": db.execute("SELECT COUNT(*) FROM policies").fetchone()[0],
        "active_policies":db.execute("SELECT COUNT(*) FROM policies WHERE status='active'").fetchone()[0],
        "expiring":       db.execute("SELECT COUNT(*) FROM policies WHERE status='expiring'").fetchone()[0],
        "expired":        db.execute("SELECT COUNT(*) FROM policies WHERE status='expired'").fetchone()[0],
        "total_revenue":  db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='success'").fetchone()[0],
        "monthly_renewals": db.execute(
            "SELECT COUNT(*) FROM renewals WHERE strftime('%Y-%m', renewal_date)=strftime('%Y-%m','now') AND status='completed'"
        ).fetchone()[0],
    }

    policies = db.execute(
        """SELECT p.*, u.name AS holder, u.email
           FROM policies p JOIN users u ON u.id=p.user_id
           ORDER BY p.expiry_date ASC LIMIT 50"""
    ).fetchall()

    users = db.execute(
        "SELECT id, name, email, phone, role, created_at FROM users WHERE role='customer' LIMIT 30"
    ).fetchall()

    # Monthly revenue for chart
    monthly = db.execute(
        """SELECT strftime('%b %Y', payment_date) AS month,
                  SUM(amount) AS revenue
           FROM payments WHERE status='success'
           GROUP BY strftime('%Y-%m', payment_date)
           ORDER BY payment_date ASC LIMIT 12"""
    ).fetchall()

    # Renewal rate per type
    renewal_rate = db.execute("SELECT * FROM v_renewal_rate").fetchall()

    db.close()
    return render_template(
        "admin.html",
        stats=stats,
        policies=policies,
        users=users,
        monthly=monthly,
        renewal_rate=renewal_rate,
    )


@admin_bp.route("/admin/policy/edit/<int:pid>", methods=["GET", "POST"])
@admin_required
def edit_policy(pid):
    db = get_db()
    policy = db.execute("SELECT * FROM policies WHERE id=?", (pid,)).fetchone()
    if not policy:
        flash("Policy not found.", "danger")
        db.close()
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        db.execute(
            "UPDATE policies SET name=?, premium=?, expiry_date=?, status=? WHERE id=?",
            (request.form["name"], request.form["premium"],
             request.form["expiry_date"], request.form["status"], pid)
        )
        db.commit()
        flash("Policy updated.", "success")
        db.close()
        return redirect(url_for("admin.admin_dashboard"))

    db.close()
    return render_template("edit_policy.html", policy=policy)


@admin_bp.route("/admin/notify/<int:pid>")
@admin_required
def send_notification(pid):
    db = get_db()
    p = db.execute(
        "SELECT p.*, u.name, u.email FROM policies p JOIN users u ON u.id=p.user_id WHERE p.id=?",
        (pid,)
    ).fetchone()
    db.close()
    if p:
        flash(f"Renewal reminder sent to {p['email']} for policy {p['policy_number']}.", "success")
    return redirect(url_for("admin.admin_dashboard"))
