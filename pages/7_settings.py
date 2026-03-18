"""Edit budget targets, savings goals, income, and debts."""
import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
st.title("⚙️ Settings")
st.caption("Update your numbers here. Changes apply for this session. To make them permanent, edit `utils/data.py` in VS Code.")

from utils.data import INCOME, DEBTS, SAVINGS_GOALS, BUDGET_TARGETS, RSU

# ── Income ────────────────────────────────────────────────────────────────────
st.subheader("💵 Income")
cols = st.columns(len(INCOME))
for col, (name, amt) in zip(cols, INCOME.items()):
    col.number_input(name, value=amt, step=100, key=f"income_{name}")

st.markdown("---")

# ── Savings goals ─────────────────────────────────────────────────────────────
st.subheader("🎯 Savings Goals")
for name, g in SAVINGS_GOALS.items():
    with st.expander(name):
        c1, c2, c3 = st.columns(3)
        c1.number_input("Current Balance ($)", value=g["current"], step=100, key=f"cur_{name}")
        c2.number_input("Goal ($)",            value=g["goal"],    step=500, key=f"goal_{name}")
        c3.number_input("Monthly Contribution ($)", value=g["monthly"], step=50, key=f"mo_{name}")

st.markdown("---")

# ── Budget targets ────────────────────────────────────────────────────────────
st.subheader("💳 Monthly Budget Targets")
cols = st.columns(3)
for i, (cat, amt) in enumerate(BUDGET_TARGETS.items()):
    cols[i % 3].number_input(cat, value=amt, step=50, key=f"budget_{cat}")

st.markdown("---")

# ── Debts ─────────────────────────────────────────────────────────────────────
st.subheader("⚡ Debt Balances")
for name, d in DEBTS.items():
    with st.expander(name):
        c1, c2, c3 = st.columns(3)
        c1.number_input("Balance ($)",      value=d["balance"], step=100, key=f"debt_bal_{name}")
        c2.number_input("APR (%)",          value=d["rate"]*100, step=0.1, format="%.2f", key=f"debt_rate_{name}")
        c3.number_input("Monthly Payment ($)", value=d["monthly"], step=10, key=f"debt_mo_{name}")

st.markdown("---")

# ── RSU ───────────────────────────────────────────────────────────────────────
st.subheader("📈 RSU")
c1, c2 = st.columns(2)
c1.number_input("Shares Held",          value=RSU["shares"], step=1,  key="rsu_shares")
c2.number_input("Current Price ($)",    value=RSU["price"],  step=1,  key="rsu_price")

st.markdown("---")
st.info("To permanently save changes, update the values in `utils/data.py` and restart the app.")
