"""Shared data helpers — budget targets, goal config, helper math."""
from collections import defaultdict

# ── Budget targets (from your Excel plan) ────────────────────────────────────
BUDGET_TARGETS = {
    "Groceries":     1_000,
    "Dining":        600,
    "Shopping":      400,
    "Subscriptions": 300,
    "Health":        300,
    "Gas/EV":        200,
    "Pets":          150,
    "Transport":     100,
    "Entertainment": 100,
    "Other":         200,
}

# ── Savings goals ─────────────────────────────────────────────────────────────
SAVINGS_GOALS = {
    "🛡️ Emergency Fund":  {"goal": 30_000, "current": 2_621,  "monthly": 750,  "apy": 0.0005,  "color": "#2E75B6"},
    "🏠 House Fund":      {"goal": 50_000, "current": 17_825, "monthly": 1000, "apy": 0.0385,  "color": "#375623"},
    "✈️ Travel Fund":     {"goal": 10_000, "current": 3_206,  "monthly": 300,  "apy": 0.0435,  "color": "#C55A11"},
}

# ── Debt snapshot ─────────────────────────────────────────────────────────────
DEBTS = {
    "Apple FCU (Auto)": {"balance": 29_871, "rate": 0.0599, "monthly": 492},
    "PNC (Auto)":       {"balance": 15_546, "rate": 0.0749, "monthly": 381},
}

# ── Income ────────────────────────────────────────────────────────────────────
INCOME = {
    "Peraton (Primary)": 8_751,
    "Inova (Part-time)": 4_957,
}

# ── RSU ───────────────────────────────────────────────────────────────────────
RSU = {
    "ticker":      "AMZN",
    "shares":      450,
    "price":       211,
    "grant_date":  "2024-09-15",
    "status":      "Fully Vested",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def monthly_averages(transactions: list, months: int = 2) -> dict:
    """Compute per-category monthly average from transaction list."""
    monthly = defaultdict(lambda: defaultdict(float))
    for t in transactions:
        if t.get("_error"):
            continue
        if t["amount"] <= 0:
            continue
        if t["category"] in ("Savings/Transfer",):
            continue
        month = t["date"][:7]
        monthly[month][t["category"]] += t["amount"]

    if not monthly:
        return {}

    all_months = list(monthly.keys())
    all_cats   = set(c for m in monthly.values() for c in m)
    return {
        cat: round(sum(monthly[m].get(cat, 0) for m in all_months) / len(all_months), 2)
        for cat in all_cats
    }

def budget_status(category: str, actual: float) -> str:
    target = BUDGET_TARGETS.get(category, 0)
    if target == 0:
        return "⚪ No budget"
    pct = actual / target
    if pct <= 0.85:
        return "✅ On track"
    if pct <= 1.0:
        return "⚠️ Near limit"
    return "🔴 Over budget"

def months_to_goal(current: float, goal: float, monthly: float, apy: float) -> float:
    """Estimate months to reach goal with compound interest (monthly)."""
    if monthly <= 0:
        return float("inf")
    r = apy / 12
    bal = current
    months = 0
    while bal < goal and months < 600:
        bal = bal * (1 + r) + monthly
        months += 1
    return months
