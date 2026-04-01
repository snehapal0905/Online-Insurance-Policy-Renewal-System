-- ============================================================
-- ShieldSure Insurance Portal — Database Schema
-- Engine: SQLite 3  (also compatible with MySQL — see notes)
-- ============================================================

-- Drop tables in reverse dependency order (for re-init)
DROP TABLE IF EXISTS renewals;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS policies;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS ai_logs;

-- ============================================================
-- TABLE: users
-- Stores all portal users (customers + admins + agents)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'customer'  -- customer | admin | agent
                          CHECK(role IN ('customer','admin','agent')),
    phone         TEXT,
    address       TEXT,
    dob           TEXT,
    pan           TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- TABLE: policies
-- Each row is one insurance policy belonging to a user
-- ============================================================
CREATE TABLE IF NOT EXISTS policies (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    type          TEXT    NOT NULL   -- Health | Motor | Life | Home
                          CHECK(type IN ('Health','Motor','Life','Home')),
    name          TEXT    NOT NULL,
    provider      TEXT    NOT NULL,
    policy_number TEXT    NOT NULL UNIQUE,
    sum_insured   REAL    NOT NULL,
    premium       REAL    NOT NULL,
    start_date    TEXT    NOT NULL,  -- YYYY-MM-DD
    expiry_date   TEXT    NOT NULL,  -- YYYY-MM-DD
    status        TEXT    NOT NULL DEFAULT 'active'
                          CHECK(status IN ('active','expiring','expired','cancelled')),
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    -- Foreign Key
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: payments
-- Records every payment transaction
-- ============================================================
CREATE TABLE IF NOT EXISTS payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    policy_id       INTEGER NOT NULL,
    amount          REAL    NOT NULL,
    payment_date    TEXT    NOT NULL DEFAULT (date('now')),
    status          TEXT    NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','success','failed','refunded')),
    transaction_id  TEXT    UNIQUE,
    payment_method  TEXT,   -- UPI | Card | Net Banking | Wallet
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    -- Foreign Keys
    FOREIGN KEY (user_id)   REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: renewals
-- Tracks every policy renewal event
-- ============================================================
CREATE TABLE IF NOT EXISTS renewals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id       INTEGER NOT NULL,
    user_id         INTEGER NOT NULL,
    renewal_date    TEXT    NOT NULL DEFAULT (date('now')),
    amount_paid     REAL    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','completed','failed')),
    transaction_id  TEXT,
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    -- Foreign Keys
    FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)   REFERENCES users(id)    ON DELETE CASCADE
);

-- ============================================================
-- TABLE: ai_logs
-- Stores AI prediction results per user (for audit/display)
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_logs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    policy_id           INTEGER,
    prediction_type     TEXT,   -- renewal_likelihood | churn_risk | recommendation
    prediction_value    TEXT,
    confidence          REAL,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id)   REFERENCES users(id),
    FOREIGN KEY (policy_id) REFERENCES policies(id)
);

-- ============================================================
-- INDEXES — speed up common queries
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_policies_user    ON policies(user_id);
CREATE INDEX IF NOT EXISTS idx_policies_expiry  ON policies(expiry_date);
CREATE INDEX IF NOT EXISTS idx_policies_status  ON policies(status);
CREATE INDEX IF NOT EXISTS idx_payments_user    ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_policy  ON payments(policy_id);
CREATE INDEX IF NOT EXISTS idx_renewals_policy  ON renewals(policy_id);
CREATE INDEX IF NOT EXISTS idx_renewals_user    ON renewals(user_id);

-- ============================================================
-- USEFUL VIEWS (read-only)
-- ============================================================

-- Expiring policies (within 30 days)
DROP VIEW IF EXISTS v_expiring_soon;
CREATE VIEW v_expiring_soon AS
SELECT p.id, p.policy_number, p.name, p.type, p.premium,
       p.expiry_date, u.name AS holder, u.email, u.phone,
       CAST(julianday(p.expiry_date) - julianday('now') AS INTEGER) AS days_left
FROM   policies p
JOIN   users u ON u.id = p.user_id
WHERE  p.status != 'expired'
  AND  julianday(p.expiry_date) - julianday('now') BETWEEN 0 AND 30
ORDER  BY days_left ASC;

-- Revenue summary per month
DROP VIEW IF EXISTS v_monthly_revenue;
CREATE VIEW v_monthly_revenue AS
SELECT strftime('%Y-%m', payment_date) AS month,
       COUNT(*)                         AS total_payments,
       SUM(amount)                      AS total_revenue
FROM   payments
WHERE  status = 'success'
GROUP  BY month
ORDER  BY month DESC;

-- Renewal rate per policy type
DROP VIEW IF EXISTS v_renewal_rate;
CREATE VIEW v_renewal_rate AS
SELECT p.type,
       COUNT(DISTINCT p.id)                                AS total_policies,
       COUNT(DISTINCT r.policy_id)                         AS renewed,
       ROUND(COUNT(DISTINCT r.policy_id) * 100.0
             / MAX(COUNT(DISTINCT p.id), 1), 1)            AS renewal_pct
FROM   policies p
LEFT JOIN renewals r ON r.policy_id = p.id AND r.status = 'completed'
GROUP  BY p.type;
