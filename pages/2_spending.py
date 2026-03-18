import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data import BUDGET_TARGETS, budget_status

st.set_page_config(page_title="Spending", page_icon="💳", layout="wide")
st.title("💳 Spending")

# ── Load cached transactions ──────────────────────────────────────────────────
txns = st.session_state.get("transactions", [])

if not txns:
    st.warning("No transaction data loaded yet. Go to **🔗 Connect Accounts** and sync first.")
    st.info("Using sample averages from your statements in the meantime.")
    # Fall back to known CC averages from statements
    averages = {
        "Groceries":     1_307,
        "Dining":        961,
        "Shopping":      586,
        "Subscriptions": 487,
        "Health":        321,
        "Gas/EV":        193,
        "Pets":          161,
        "Other":         300,
    }
else:
    from utils.data import monthly_averages
    averages = monthly_averages(txns)

# ── Budget vs Actual ──────────────────────────────────────────────────────────
st.subheader("Budget vs. Actual (Monthly Average)")

rows = []
for cat, actual in sorted(averages.items(), key=lambda x: -x[1]):
    budget = BUDGET_TARGETS.get(cat, 0)
    status = budget_status(cat, actual)
    rows.append({
        "Category": cat,
        "Actual ($)": actual,
        "Budget ($)": budget,
        "Over/Under": actual - budget if budget > 0 else 0,
        "Status": status,
    })

df = pd.DataFrame(rows)

# Color-coded bar chart
fig = go.Figure()
for _, row in df.iterrows():
    color = "#43A047" if "✅" in row["Status"] else "#FFB300" if "⚠️" in row["Status"] else "#EF5350" if "🔴" in row["Status"] else "#90A4AE"
    fig.add_trace(go.Bar(
        name=row["Category"],
        x=[row["Category"]],
        y=[row["Actual ($)"]],
        marker_color=color,
        showlegend=False,
        text=f"${row['Actual ($)']:,.0f}",
        textposition="outside",
    ))

# Budget line
fig.add_trace(go.Scatter(
    x=df["Category"],
    y=df["Budget ($)"],
    mode="markers",
    marker=dict(symbol="line-ew", size=20, color="#1F3864", line=dict(width=3, color="#1F3864")),
    name="Budget",
))
fig.update_layout(
    height=380,
    margin=dict(t=30, b=20, l=20, r=20),
    yaxis_title="Amount ($)",
    barmode="group",
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig, use_container_width=True)

# ── Table ─────────────────────────────────────────────────────────────────────
st.dataframe(
    df.style
      .format({"Actual ($)": "${:,.0f}", "Budget ($)": "${:,.0f}", "Over/Under": "${:+,.0f}"})
      .applymap(lambda v: "color: #EF5350; font-weight:bold" if isinstance(v, str) and "🔴" in v else
                          "color: #FFB300" if isinstance(v, str) and "⚠️" in v else
                          "color: #43A047" if isinstance(v, str) and "✅" in v else "",
                subset=["Status"]),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# ── Spending donut ────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Spending Mix")
    fig_pie = px.pie(
        df, values="Actual ($)", names="Category",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_layout(height=320, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Monthly Overspend")
    total_budget = sum(BUDGET_TARGETS.get(c, 0) for c in averages)
    total_actual = sum(averages.values())
    overspend    = total_actual - total_budget

    st.metric("Total Budgeted", f"${total_budget:,.0f}")
    st.metric("Total Actual",   f"${total_actual:,.0f}")
    st.metric("Monthly Overspend", f"${overspend:,.0f}",
              delta=f"${overspend:,.0f} over" if overspend > 0 else "Under budget",
              delta_color="inverse")

    if overspend > 0:
        st.error(f"You're spending **${overspend:,.0f}/month more** than budgeted. "
                 f"That's **${overspend*12:,.0f}/year** that could go toward your goals.")
    else:
        st.success("You're within budget!")

# ── Transaction list (if available) ──────────────────────────────────────────
if txns:
    st.markdown("---")
    st.subheader("Recent Transactions")
    clean = [t for t in txns if not t.get("_error") and t["amount"] > 0]
    df_txns = pd.DataFrame(clean).sort_values("date", ascending=False).head(50)
    df_txns["amount"] = df_txns["amount"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_txns[["date", "name", "amount", "category", "institution"]],
                 use_container_width=True, hide_index=True)
