import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data import RSU, DEBTS, SAVINGS_GOALS

st.set_page_config(page_title="RSU Tracker", page_icon="📈", layout="wide")
st.title("📈 Amazon RSU Tracker")

# ── Live inputs ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    price  = st.number_input("Current AMZN Price ($)", value=float(RSU["price"]), step=0.5, format="%.2f")
with col2:
    shares = st.number_input("Shares Held", value=RSU["shares"], step=1)

value = shares * price
st.metric("📦 Total Value", f"${value:,.0f}", f"{shares} shares × ${price:.2f}")

st.markdown("---")

# ── What it could fund ────────────────────────────────────────────────────────
st.subheader("What Your Shares Could Fund")
tax_pct  = st.slider("Estimated tax rate (%)", min_value=15, max_value=35, value=24, step=1)
TAX_RATE = tax_pct / 100

scenarios = [
    ("Pay off Apple FCU auto loan",  DEBTS["Apple FCU (Auto)"]["balance"]),
    ("Pay off PNC auto loan",        DEBTS["PNC (Auto)"]["balance"]),
    ("Pay off BOTH auto loans",      sum(d["balance"] for d in DEBTS.values())),
    ("Top-up Emergency Fund",        SAVINGS_GOALS["🛡️ Emergency Fund"]["goal"] - SAVINGS_GOALS["🛡️ Emergency Fund"]["current"]),
    ("Top-up House Fund",            SAVINGS_GOALS["🏠 House Fund"]["goal"] - SAVINGS_GOALS["🏠 House Fund"]["current"]),
    ("Top-up Travel Fund",           SAVINGS_GOALS["✈️ Travel Fund"]["goal"] - SAVINGS_GOALS["✈️ Travel Fund"]["current"]),
]

import math
rows = []
for name, goal in scenarios:
    needed_shares = math.ceil(goal / (price * (1 - TAX_RATE)))
    gross         = needed_shares * price
    tax           = gross * TAX_RATE
    net           = gross - tax
    funded        = "✅ Fully Funded" if net >= goal else "⚠️ Partial"
    rows.append({
        "Scenario":       name,
        "Goal ($)":       goal,
        "Shares to Sell": needed_shares,
        "Gross ($)":      gross,
        f"Tax ({tax_pct}%) ($)": tax,
        "Net ($)":        net,
        "Status":         funded,
    })

df = pd.DataFrame(rows)
st.dataframe(
    df.style.format({
        "Goal ($)": "${:,.0f}",
        "Gross ($)": "${:,.0f}",
        f"Tax ({tax_pct}%) ($)": "${:,.0f}",
        "Net ($)": "${:,.0f}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.caption("Shares to Sell = minimum shares needed to cover goal after estimated taxes.")

st.markdown("---")

# ── Remaining shares gauge ────────────────────────────────────────────────────
st.subheader("Sell Simulator")
sell = st.slider("How many shares would you sell?", 0, shares, 0)
net_proceeds = sell * price * (1 - TAX_RATE)
remaining    = shares - sell
remaining_val = remaining * price

c1, c2, c3 = st.columns(3)
c1.metric("Shares Remaining",  f"{remaining}")
c2.metric("Net Proceeds",      f"${net_proceeds:,.0f}", f"after {tax_pct}% tax")
c3.metric("Remaining Value",   f"${remaining_val:,.0f}")

# Visual breakdown
fig = go.Figure(go.Pie(
    labels=["Sold", "Remaining"],
    values=[sell, remaining],
    hole=0.6,
    marker_colors=["#EF5350", "#43A047"],
))
fig.update_layout(height=250, margin=dict(t=10, b=10), showlegend=True,
                  legend=dict(orientation="h", y=-0.1))
if sell > 0:
    fig.add_annotation(text=f"${net_proceeds:,.0f}\nnet", x=0.5, y=0.5,
                       font_size=14, showarrow=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("⚠️ Not financial advice. Consult a CPA before selling. AMZN shares granted Sep 2024 — held 18+ months → long-term capital gains rates apply.")
