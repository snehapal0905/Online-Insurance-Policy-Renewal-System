"""
ShieldSure - Online Insurance Policy Renewal System
Main Flask Application Entry Point
"""

from flask import Flask
from database.db import init_db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.policies import policies_bp
from routes.renewal import renewal_bp
from routes.admin import admin_bp
from routes.api import api_bp
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "shieldsure-dev-secret-2024")

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(policies_bp)
app.register_blueprint(renewal_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp, url_prefix="/api")

# Initialize DB on first run
with app.app_context():
    init_db()

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  ShieldSure Insurance Portal — Starting Server")
    print("="*55)
    print("  Open in browser: http://127.0.0.1:5000")
    print("  Admin login:     admin@shieldsure.com / admin123")
    print("  User login:      rahul@example.com  / user123")
    print("="*55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
