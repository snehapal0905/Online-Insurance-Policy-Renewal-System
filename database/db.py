"""
database/db.py
SQLite database initialization and connection helper
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, date

conn = sqlite3.connect("shieldsure.db")
cursor = conn.cursor()


DB_PATH = os.path.join(os.path.dirname(__file__), "shieldsure.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_db():
    """Return a new database connection with row_factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables from schema.sql and seed demo data if DB is empty."""
    conn = get_db()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    _seed_demo_data(conn)
    conn.close()
    print("[DB] Database initialized successfully.")


def _seed_demo_data(conn):
    """Insert demo users, policies, and renewals if not already present."""
    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        return  # Already seeded

    # ── USERS ──────────────────────────────────────────────────────────────
    users = [
        (1, "Rahul Kumar",    "rahul@example.com",        generate_password_hash("user123"),  "customer", "+91 98765 43210", "Pimpri, Pune", "15-08-1990", "ABCPK1234D"),
        (2, "Priya Sharma",   "priya@example.com",        generate_password_hash("user123"),  "customer", "+91 90123 45678", "Baner, Pune",  "22-03-1992", "BSDPM5678E"),
        (3, "Amit Patel",     "amit@example.com",         generate_password_hash("user123"),  "customer", "+91 97654 32100", "Kothrud, Pune","10-11-1985", "CPZPA9012F"),
        (4, "Sunita Rao",     "sunita@example.com",       generate_password_hash("user123"),  "customer", "+91 88901 23456", "Wakad, Pune",  "05-07-1994", "DRQSR3456G"),
        (5, "Admin User",     "admin@shieldsure.com",     generate_password_hash("admin123"), "admin",    "+91 99999 00000", "HO Mumbai",   "01-01-1980", "ADMIN00000"),
    ]
    conn.executemany(
        "INSERT INTO users (id, name, email, password_hash, role, phone, address, dob, pan) VALUES (?,?,?,?,?,?,?,?,?)",
        users
    )

    # ── POLICIES ────────────────────────────────────────────────────────────
    policies = [
        (1, 1, "Health",  "Health Shield Premium",     "HDFC Ergo",      "POL-2024-0041", 1000000, 12500.00, "2024-01-12", "2026-01-12", "active"),
        (2, 1, "Motor",   "Motor Comprehensive",        "ICICI Lombard",  "POL-2024-0038",  540000,  8200.00, "2024-04-14", "2025-04-14", "expiring"),
        (3, 1, "Life",    "Term Life Cover",            "LIC India",      "POL-2023-0097", 5000000, 15000.00, "2023-03-20", "2026-03-20", "active"),
        (4, 1, "Home",    "Home Protect Plus",          "Bajaj Allianz",  "POL-2023-0055",  2500000,  3200.00, "2023-07-18", "2025-07-18", "active"),
        (5, 2, "Health",  "Health Family Floater",      "Star Health",    "POL-2024-0039",   500000,  9800.00, "2024-02-22", "2026-02-22", "active"),
        (6, 3, "Life",    "Endowment Plan",             "SBI Life",       "POL-2024-0036",  2500000, 22000.00, "2024-01-01", "2053-12-30", "active"),
        (7, 4, "Motor",   "Third Party Motor",          "New India",      "POL-2024-0030",   300000,  6400.00, "2024-02-01", "2025-02-01", "expired"),
    ]
    conn.executemany(
        "INSERT INTO policies (id, user_id, type, name, provider, policy_number, sum_insured, premium, start_date, expiry_date, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        policies
    )

    # ── PAYMENTS ────────────────────────────────────────────────────────────
    payments = [
        (1, 1, 1, 12500.00, "2024-01-12", "success", "TXN-112741", "UPI"),
        (2, 1, 2,  8200.00, "2024-04-14", "success", "TXN-882741", "UPI"),
        (3, 1, 3, 15000.00, "2023-03-20", "success", "TXN-332741", "Card"),
        (4, 1, 4,  3200.00, "2023-07-18", "success", "TXN-442741", "Net Banking"),
        (5, 2, 5,  9800.00, "2024-02-22", "success", "TXN-552741", "UPI"),
        (6, 3, 6, 22000.00, "2024-01-01", "success", "TXN-662741", "Card"),
        (7, 4, 7,  6400.00, "2024-02-01", "success", "TXN-772741", "UPI"),
    ]
    conn.executemany(
        "INSERT INTO payments (id, user_id, policy_id, amount, payment_date, status, transaction_id, payment_method) VALUES (?,?,?,?,?,?,?,?)",
        payments
    )
    
# CREATE TABLES FIRST
with open(SCHEMA_PATH, "r") as f:
    conn.executescript(f.read())

# ── RENEWALS ────────────────────────────────────────────────────────────
renewals = [
    (1, 1, "2024-01-12", 12500.00, "completed", "TXN-112741"),
    (2, 1, "2024-04-14", 8200.00, "completed", "TXN-882741"),
    (3, 1, "2023-03-20", 15000.00, "completed", "TXN-332741"),
    (4, 1, "2023-07-18", 3200.00, "completed", "TXN-442741"),
]
conn.executemany(
    "INSERT INTO renewals (policy_id, user_id, renewal_date, amount_paid, status, transaction_id) VALUES (?,?,?,?,?,?)",
    renewals
)

conn.commit()
print("[DB] Demo data seeded.")