import streamlit as st
from utils.data import INCOME, DEBTS, SAVINGS_GOALS, RSU

st.set_page_config(
    page_title="Abadir's Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💰 Personal Finance Dashboard")

col1, col2, col3, col4 = st.columns(4)

total_income  = sum(INCOME.values())
total_debt    = sum(d["balance"] for d in DEBTS.values())
total_savings = sum(g["current"] for g in SAVINGS_GOALS.values())
rsu_value     = RSU["shares"] * RSU["price"]

col1.metric("💵 Monthly Income", f"${total_income:,.0f}")
col2.metric("💳 Total Debt",     f"${total_debt:,.0f}")
col3.metric("🏦 Total Savings",  f"${total_savings:,.0f}")
col4.metric("📈 RSU Value",      f"${rsu_value:,.0f}", f"{RSU['shares']} shares @ ${RSU['price']}")

st.markdown("---")
st.info("👈 Select a section from the sidebar to get started.")