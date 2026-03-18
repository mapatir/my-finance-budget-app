import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data import DEBTS, RSU

st.set_page_config(page_title="Debt", page_icon="⚡", layout="wide")
st.title("⚡ Debt Payoff")

# ── Summary metrics ───────────────────────────────────────────────────────────
total_balance = sum(d["balance"] for d in DEBTS.values())
total_monthly = sum(d["monthly"] for d in DEBTS.values())
total_interest = sum(d["balance"] * d["rate"] / 12 for d in DEBTS.values())

c1, c2, c3 = st.columns(3)
c1.metric("Total Debt",           f"${total_balance:,.0f}")
c2.metric("Monthly Payments",     f"${total_monthly:,.0f}")
c3.metric("Monthly Interest Cost", f"${total_interest:,.0f}", "money not reducing principal")

st.markdown("---")

# ── Payoff projections ────────────────────────────────────────────────────────
st.subheader("Payoff Timeline")

col_left, col_right = st.columns(2)

def payoff_schedule(balance, rate, monthly):
    r       = rate / 12
    history = []
    bal     = balance
    month   = 0
    while bal > 0 and month < 360:
        interest = bal * r
        principal = min(monthly - interest, bal)
        if principal <= 0:
            break
        bal    -= principal
        month  += 1
        history.append({"Month": month, "Balance": round(max(bal, 0), 2)})
    return history

with col_left:
    for name, d in DEBTS.items():
        schedule = payoff_schedule(d["balance"], d["rate"], d["monthly"])
        months   = len(schedule)

        st.markdown(f"**{name}**")
        st.caption(f"${d['balance']:,.0f} @ {d['rate']*100:.2f}% APR — ${d['monthly']:,}/mo — payoff in **{months} months**")

        fig = go.Figure(go.Scatter(
            x=[s["Month"] for s in schedule],
            y=[s["Balance"] for s in schedule],
            fill="tozeroy",
            line=dict(color="#EF5350", width=2),
            fillcolor="rgba(239,83,80,0.2)",
        ))
        fig.update_layout(height=180, margin=dict(t=10, b=20, l=20, r=20),
                          xaxis_title="Months", yaxis_title="Balance ($)",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ── RSU payoff scenario ───────────────────────────────────────────────────────
with col_right:
    st.subheader("🚀 RSU Payoff Scenario")

    price  = st.number_input("AMZN Share Price ($)", value=RSU["price"], step=1)
    shares = RSU["shares"]

    st.markdown(f"You hold **{shares} shares** of AMZN worth **${shares * price:,.0f}**.")
    st.markdown("Selling shares to pay off debt would free up:")

    freed = total_monthly
    st.metric("Monthly cash freed", f"${freed:,.0f}/mo", "no more debt payments")

    shares_needed = {}
    rows = []
    for name, d in DEBTS.items():
        after_tax_per_share = price * 0.76   # ~24% combined tax
        n = -(-d["balance"] // after_tax_per_share)  # ceiling
        shares_needed[name] = int(n)
        rows.append({
            "Debt": name,
            "Balance": f"${d['balance']:,.0f}",
            "Shares to Sell": int(n),
            "Gross Proceeds": f"${int(n) * price:,.0f}",
            "Net After Tax":  f"${int(int(n) * price * 0.76):,.0f}",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    both = sum(shares_needed.values())
    st.info(f"Selling **{both} shares** (~${both * price:,.0f} gross) eliminates both loans "
            f"and frees **${freed:,}/month**.")

    # Show remaining shares
    remaining = shares - both
    if remaining > 0:
        st.success(f"You'd still have **{remaining} shares** worth ~**${remaining * price:,.0f}** after payoff.")
    else:
        st.warning("This would require more shares than you currently hold.")
