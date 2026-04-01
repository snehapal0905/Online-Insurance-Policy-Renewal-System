"""
utils/helpers.py  —  Decorators and utility functions
"""

from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import date, datetime


def login_required(f):
    """Redirect to login if user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Restrict route to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("user_role") != "admin":
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("dashboard.dashboard"))
        return f(*args, **kwargs)
    return decorated


def days_until_expiry(expiry_str):
    try:
        exp = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        return (exp - date.today()).days
    except Exception:
        return 999


def expiry_status(days_left):
    if days_left < 0:
        return "expired"
    if days_left <= 30:
        return "expiring"
    return "active"


def format_inr(amount):
    """Format number as Indian Rupees string."""
    try:
        return f"₹{amount:,.0f}"
    except Exception:
        return str(amount)
