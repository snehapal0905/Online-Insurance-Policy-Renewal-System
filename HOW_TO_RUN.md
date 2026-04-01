# ShieldSure — Online Insurance Policy Renewal System
## Complete Setup & Run Guide

---

## Project Structure

```
insurance_project/
├── app.py                    ← Main Flask entry point
├── requirements.txt          ← Python dependencies
├── database/
│   ├── __init__.py
│   ├── db.py                 ← DB connection + seed data
│   └── schema.sql            ← All SQL tables, views, indexes
├── routes/
│   ├── auth.py               ← Login, Register, Logout
│   ├── dashboard.py          ← Customer dashboard
│   ├── policies.py           ← View policies
│   ├── renewal.py            ← Renewal + payment flow
│   ├── admin.py              ← Admin panel
│   └── api.py                ← REST API (JSON)
├── ml/
│   └── predictor.py          ← AI/ML renewal prediction
├── utils/
│   └── helpers.py            ← Decorators, utilities
└── templates/
    ├── base.html             ← Shared layout + sidebar
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── policies.html
    ├── policy_detail.html
    ├── renew_list.html
    ├── renew_policy.html
    ├── renewal_success.html
    ├── admin.html
    └── edit_policy.html
```

---

## STEP 1 — Install Python

- Download Python 3.10+ from https://www.python.org/downloads/
- During install, check ✅ "Add Python to PATH"
- Verify: open Command Prompt / Terminal and type:
  ```
  python --version
  ```

---

## STEP 2 — Set Up the Project

Open **Command Prompt** (Windows) or **Terminal** (Mac/Linux):

```bash
# Navigate to the project folder
cd path/to/insurance_project

# Create a virtual environment



# Activate it:
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## STEP 3 — Run the App

```bash
python app.py
```

You will see:
```
=======================================================
  ShieldSure Insurance Portal — Starting Server
=======================================================
  Open in browser: http://127.0.0.1:5000
  Admin login:     admin@shieldsure.com / admin123
  User login:      rahul@example.com  / user123
=======================================================
```

Open your browser and go to:
```
http://127.0.0.1:5000
```

The database (`shieldsure.db`) and all demo data are created automatically on first run.

---

## STEP 4 — Demo Login Credentials

| Role     | Email                     | Password  |
|----------|---------------------------|-----------|
| Customer | rahul@example.com         | user123   |
| Customer | priya@example.com         | user123   |
| Customer | amit@example.com          | user123   |
| Admin    | admin@shieldsure.com      | admin123  |

---

## STEP 5 — View the Database in DB Browser for SQLite

This lets you see your SQL tables visually — perfect for project demos.

### Install DB Browser for SQLite:
- Download from: https://sqlitebrowser.org/dl/
- Install and open it

### Connect to the database:
1. Open **DB Browser for SQLite**
2. Click **"Open Database"**
3. Navigate to your project folder → select `database/shieldsure.db`
4. Click the **"Browse Data"** tab
5. From the dropdown, choose any table:
   - `users` — All registered users
   - `policies` — All insurance policies
   - `payments` — All payment records
   - `renewals` — Renewal history
   - `ai_logs` — AI prediction logs

### View SQL Views (Analytics):
Click the **"Execute SQL"** tab and run:

```sql
-- See expiring policies
SELECT * FROM v_expiring_soon;

-- Monthly revenue
SELECT * FROM v_monthly_revenue;

-- Renewal rate by policy type
SELECT * FROM v_renewal_rate;

-- All users and their policy counts
SELECT u.name, u.email, COUNT(p.id) AS policies
FROM users u
LEFT JOIN policies p ON p.user_id = u.id
GROUP BY u.id;
```

---

## MySQL Setup (Optional — for production/college demo)

If your college requires MySQL instead of SQLite:

### 1. Install MySQL
Download from: https://dev.mysql.com/downloads/mysql/

### 2. Install Python MySQL driver
```bash
pip install PyMySQL
```

### 3. Create database in MySQL
Open MySQL Workbench or MySQL command line:
```sql
CREATE DATABASE shieldsure_db;
USE shieldsure_db;
```

### 4. Convert schema for MySQL
The `schema.sql` uses SQLite syntax. For MySQL, change:
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `INT AUTO_INCREMENT PRIMARY KEY`
- `datetime('now')` → `NOW()`
- `date('now')` → `CURDATE()`
- `julianday()` → `DATEDIFF()`
- Remove `DROP TABLE IF EXISTS` before `CREATE TABLE IF NOT EXISTS`

### 5. Update db.py connection
Replace the `get_db()` function with:
```python
import pymysql

def get_db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='your_mysql_password',
        database='shieldsure_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn
```

---

## API Endpoints (for demo)

| Method | URL                   | Description              |
|--------|-----------------------|--------------------------|
| GET    | `/`                   | Redirect to login        |
| GET    | `/login`              | Login page               |
| POST   | `/login`              | Authenticate user        |
| GET    | `/register`           | Register page            |
| POST   | `/register`           | Create new account       |
| GET    | `/dashboard`          | Customer dashboard       |
| GET    | `/policies`           | List all policies        |
| GET    | `/policies/<id>`      | Policy detail            |
| GET    | `/renew`              | Renewal list             |
| GET    | `/renew/<id>`         | Renewal form             |
| POST   | `/renew/<id>`         | Process renewal          |
| GET    | `/admin`              | Admin dashboard          |
| GET    | `/admin/policy/edit/<id>` | Edit policy form    |
| POST   | `/admin/policy/edit/<id>` | Save policy edits   |
| GET    | `/admin/notify/<id>`  | Send renewal reminder    |
| GET    | `/api/policies`       | JSON: user's policies    |
| GET    | `/api/stats`          | JSON: summary stats      |
| GET    | `/api/predict/<uid>`  | JSON: AI predictions     |
| GET    | `/logout`             | Logout                   |

---

## Tech Stack Summary (for your report)

| Layer      | Technology               |
|------------|--------------------------|
| Frontend   | HTML5, CSS3, JavaScript  |
| Backend    | Python 3.10+, Flask 3.0  |
| Database   | SQLite 3 (/ MySQL)       |
| AI Module  | scikit-learn (Logistic Regression) + Rule-based fallback |
| Security   | Werkzeug password hashing, session auth, CSRF-ready |
| ORM        | Raw SQL with sqlite3 (parametrized queries — SQL injection safe) |

---

## Database Tables (for your SQL section)

```
users       → user_id (PK), name, email, password_hash, role, phone, address
policies    → policy_id (PK), user_id (FK), type, name, provider, premium, expiry_date, status
payments    → payment_id (PK), user_id (FK), policy_id (FK), amount, status, transaction_id
renewals    → renewal_id (PK), policy_id (FK), user_id (FK), renewal_date, amount_paid, status
ai_logs     → id (PK), user_id (FK), prediction_type, prediction_value, confidence
```

---

## Troubleshooting

| Problem                  | Solution                                        |
|--------------------------|-------------------------------------------------|
| `ModuleNotFoundError`    | Run `pip install -r requirements.txt` again     |
| Port 5000 already in use | Change port in app.py: `app.run(port=5001)`     |
| Database locked          | Delete `shieldsure.db` and re-run `python app.py` |
| scikit-learn not found   | AI falls back to rule-based mode automatically  |
| Blank page               | Check terminal for error messages               |

---

*ShieldSure — Industry Practices Internship Project*
*Built with Python + Flask + SQLite + scikit-learn*
