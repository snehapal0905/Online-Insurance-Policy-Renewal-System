"""
ml/predictor.py
AI Module — Renewal Likelihood Prediction + Smart Recommendations

Uses:
  1. Rule-based scoring (primary — no external deps needed)
  2. scikit-learn Logistic Regression (optional — used if sklearn installed)

To use scikit-learn, run:  pip install scikit-learn
"""

from datetime import date, datetime

# ── Try to import sklearn; fall back to rule-based if not available ──────────
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# ── Rule-based prediction ─────────────────────────────────────────────────────

def _rule_based_score(num_policies, days_left_min, total_premium, renewal_count):
    """
    Simple scoring:
      - More policies  → higher loyalty
      - Higher premium → higher financial commitment
      - More renewals  → stronger retention
      - Days left      → urgency
    Returns a probability float 0.0–1.0
    """
    score = 0.5  # base

    if num_policies >= 3:       score += 0.15
    elif num_policies >= 2:     score += 0.08

    if total_premium >= 20000:  score += 0.12
    elif total_premium >= 8000: score += 0.06

    if renewal_count >= 3:      score += 0.15
    elif renewal_count >= 1:    score += 0.08

    if days_left_min < 0:       score -= 0.10  # already lapsed
    elif days_left_min < 15:    score += 0.05  # urgency boost

    return max(0.0, min(1.0, score))


# ── sklearn-based prediction (trains on synthetic data) ──────────────────────

def _sklearn_predict(features):
    """
    Train a logistic regression model on synthetic historical data,
    then predict for the given feature vector.

    Features: [num_policies, min_days_left, total_premium_k, renewal_count]
    """
    if not SKLEARN_AVAILABLE:
        return None

    # Synthetic training data  [num_policies, days_left, premium_k, renewals]  → label
    X_train = np.array([
        [1, 5,  6, 0], [1, 10, 8, 0], [2, 20, 12, 1], [2, 30, 15, 2],
        [3, 45, 20, 3], [3, 60, 25, 4], [4, 90, 30, 5], [4, 120, 35, 6],
        [1, -5, 5, 0], [1, -10, 4, 0], [2, -20, 10, 1], [3, 200, 40, 7],
        [2, 15, 18, 2], [3, 25, 22, 3], [1, 50, 7, 1],  [4, 300, 60, 8],
    ])
    y_train = np.array([0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression(max_iter=200, random_state=42)
    model.fit(X_scaled, y_train)

    X_pred = scaler.transform([features])
    prob = model.predict_proba(X_pred)[0][1]
    return round(float(prob), 3)


# ── Public API ────────────────────────────────────────────────────────────────

def predict_renewal(num_policies, days_left_min, total_premium, renewal_count):
    """
    Return renewal probability (0.0 – 1.0) using best available method.
    """
    if SKLEARN_AVAILABLE:
        prob = _sklearn_predict([
            num_policies, days_left_min, total_premium / 1000, renewal_count
        ])
        if prob is not None:
            return prob

    return _rule_based_score(num_policies, days_left_min, total_premium, renewal_count)


def get_ai_insights(user_id, policies):
    """
    Analyze a user's policies and return an insights dict for the UI.
    """
    if not policies:
        return {
            "renewal_probability": 0.5,
            "renewal_pct":         50,
            "urgent_policy":       None,
            "recommendation":      "Add your first insurance policy to get started.",
            "savings_tip":         None,
            "method":              "rule-based",
        }

    today = date.today()

    # Compute days left per policy
    days_list = []
    for p in policies:
        try:
            exp = datetime.strptime(p["expiry_date"] if isinstance(p, dict) else p["expiry_date"], "%Y-%m-%d").date()
            days_list.append((exp - today).days)
        except Exception:
            days_list.append(999)

    min_days      = min(days_list) if days_list else 999
    total_premium = sum((p["premium"] if isinstance(p, dict) else p["premium"]) for p in policies)
    renewal_count = len([d for d in days_list if d > 0])

    prob = predict_renewal(len(policies), min_days, total_premium, renewal_count)
    pct  = round(prob * 100)

    # Identify the most urgent policy
    urgent = None
    urgent_days = None
    for i, p in enumerate(policies):
        if days_list[i] == min_days and min_days < 30:
            urgent = p["name"] if isinstance(p, dict) else p["name"]
            urgent_days = min_days
            break

    # Recommendation text
    if urgent_days is not None and urgent_days <= 0:
        rec = f"⚠ Your '{urgent}' has expired. Renew immediately to restore coverage."
    elif urgent_days is not None and urgent_days <= 15:
        rec = f"🚨 '{urgent}' expires in {urgent_days} days. Renew now to avoid a lapse."
    elif urgent_days is not None and urgent_days <= 30:
        rec = f"'{urgent}' expires in {urgent_days} days. Schedule renewal soon."
    else:
        rec = "All policies are in good standing. Consider reviewing coverage amounts annually."

    # Savings tip
    types = set((p["type"] if isinstance(p, dict) else p["type"]) for p in policies)
    savings = None
    if "Health" in types and "Home" not in types:
        savings = "Add a Home Insurance policy and bundle it with your Health plan to save up to ₹2,100/year."
    elif len(types) >= 3:
        savings = f"You qualify for a multi-policy loyalty discount. Contact your agent for up to 8% off."
    elif "Motor" in types and "Home" in types:
        savings = "Renew Motor + Home together in one transaction to save ₹2,100."

    return {
        "renewal_probability": prob,
        "renewal_pct":         pct,
        "urgent_policy":       urgent,
        "urgent_days":         urgent_days,
        "recommendation":      rec,
        "savings_tip":         savings,
        "method":              "scikit-learn" if SKLEARN_AVAILABLE else "rule-based",
    }
