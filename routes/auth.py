"""
routes/auth.py  —  Login, Register, Logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import get_db
from utils.helpers import login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"]   = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            session["user_email"]= user["email"]
            flash(f"Welcome back, {user['name'].split()[0]}!", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        phone    = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not all([name, email, password]):
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("Email already registered. Please login.", "warning")
            db.close()
            return render_template("register.html")

        hashed = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (name, email, password_hash, phone, role) VALUES (?,?,?,?,?)",
            (name, email, hashed, phone, "customer")
        )
        db.commit()
        db.close()

        flash("Account created! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
