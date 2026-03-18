import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.data import INCOME, DEBTS, SAVINGS_GOALS, RSU, BUDGET_TARGETS, months_to_goal

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard")

# ── Top metrics ───────────────────────────────────────────────────────────────
total_income   = sum(INCOME.values())
fixed_expenses = 2_985 + 492 + 676 + 191 + 185 + 381 + 990  # from your budget
total_savings  = sum(g["current"] for g in SAVINGS_GOALS.values())
total_debt     = sum(d["balance"] for d in DEBTS.values())
rsu_value      = RSU["shares"] * RSU["price"]
net_worth      = total_savings + rsu_value - total_debt

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Monthly Income",    f"${total_income:,.0f}")
c2.metric("Fixed Expenses",    f"${fixed_expenses:,.0f}", f"-{fixed_expenses/total_income*100:.0f}% of income")
c3.metric("Total Savings",     f"${total_savings:,.0f}")
c4.metric("Total Debt",        f"${total_debt:,.0f}")
c5.metric("Est. Net Worth",    f"${net_worth:,.0f}", "incl. RSU")

st.markdown("---")

# ── Income breakdown (donut) ──────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Income Sources")
    fig_income = go.Figure(go.Pie(
        labels=list(INCOME.keys()),
        values=list(INCOME.values()),
        hole=0.55,
        marker_colors=["#2E75B6", "#375623"],
    ))
    fig_income.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
    )
    fig_income.add_annotation(
        text=f"${total_income:,}", x=0.5, y=0.5,
        font_size=18, showarrow=False, font_color="#1F3864",
    )
    st.plotly_chart(fig_income, use_container_width=True)

# ── Monthly cash flow (waterfall) ────────────────────────────────────────────
with col_right:
    st.subheader("Monthly Cash Flow")
    var_expenses = 1_307 + 961 + 586 + 487 + 321 + 193 + 161  # CC averages
    savings_out  = 500 + 750 + 1_000 + 300                     # recommended savings

    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Income", "Fixed", "Variable", "Savings", "Left Over"],
        y=[total_income, -fixed_expenses, -var_expenses, -savings_out, 0],
        connector={"line": {"color": "#CCCCCC"}},
        decreasing={"marker": {"color": "#FF7043"}},
        increasing={"marker": {"color": "#43A047"}},
        totals={"marker": {"color": "#2E75B6"}},
        text=[f"${abs(v):,.0f}" for v in [total_income, -fixed_expenses, -var_expenses, -savings_out, 0]],
        textposition="outside",
    ))
    fig_wf.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
        showlegend=False,
        yaxis_title="Amount ($)",
    )
    st.plotly_chart(fig_wf, use_container_width=True)

st.markdown("---")

# ── Savings goals progress ────────────────────────────────────────────────────
st.subheader("🎯 Savings Goals")
for name, g in SAVINGS_GOALS.items():
    pct     = min(g["current"] / g["goal"], 1.0)
    months  = months_to_goal(g["current"], g["goal"], g["monthly"], g["apy"])
    c1, c2, c3 = st.columns([3, 1, 1])
    c1.markdown(f"**{name}**")
    c1.progress(pct, text=f"${g['current']:,.0f} of ${g['goal']:,.0f}  ({pct*100:.0f}%)")
    c2.metric("Monthly", f"+${g['monthly']:,}")
    c3.metric("ETA", f"{int(months)} mo" if months < 600 else "∞")

st.markdown("---")

# ── Debt snapshot ─────────────────────────────────────────────────────────────
st.subheader("⚡ Debt")
d_cols = st.columns(len(DEBTS))
for col, (name, d) in zip(d_cols, DEBTS.items()):
    col.metric(name, f"${d['balance']:,.0f}", f"{d['rate']*100:.2f}% APR")
