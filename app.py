"""
Personal Finance App — main entry point
Run with:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Manny's Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar nav ───────────────────────────────────────────────────────────────
st.sidebar.title("💰 Finance App")
st.sidebar.markdown("---")

pages = {
    "📊 Dashboard":          "pages/1_dashboard.py",
    "💳 Spending":           "pages/2_spending.py",
    "🎯 Goals":              "pages/3_goals.py",
    "⚡ Debt":               "pages/4_debt.py",
    "📈 RSU Tracker":        "pages/5_rsu.py",
    "🔗 Connect Accounts":   "pages/6_connect.py",
    "⚙️ Settings":           "pages/7_settings.py",
}

# Streamlit multi-page via st.navigation (1.31+) or sidebar links
st.sidebar.markdown("### Navigation")
for name in pages:
    st.sidebar.page_link(pages[name], label=name)

st.sidebar.markdown("---")

# Quick sync button in sidebar
if st.sidebar.button("🔄 Sync Now", use_container_width=True):
    st.sidebar.info("Go to Connect Accounts to sync.")

st.sidebar.caption("Data updates every time you sync.")

# ── Home / welcome screen ─────────────────────────────────────────────────────
st.title("💰 Personal Finance Dashboard")
st.markdown("Use the sidebar to navigate between sections.")

col1, col2, col3, col4 = st.columns(4)

from utils.data import INCOME, DEBTS, SAVINGS_GOALS, RSU, BUDGET_TARGETS

total_income  = sum(INCOME.values())
total_debt    = sum(d["balance"] for d in DEBTS.values())
total_savings = sum(g["current"] for g in SAVINGS_GOALS.values())
rsu_value     = RSU["shares"] * RSU["price"]

col1.metric("💵 Monthly Income",  f"${total_income:,.0f}")
col2.metric("💳 Total Debt",      f"${total_debt:,.0f}")
col3.metric("🏦 Total Savings",   f"${total_savings:,.0f}")
col4.metric("📈 RSU Value",       f"${rsu_value:,.0f}", f"{RSU['shares']} shares @ ${RSU['price']}")

st.markdown("---")
st.info("👈 Select a section from the sidebar to get started.")
