import streamlit as st
import plotly.graph_objects as go
from utils.data import SAVINGS_GOALS, months_to_goal

def hex_to_rgba(hex_color, alpha=0.2):
    """Convert #RRGGBB to rgba(r,g,b,alpha) for Plotly fillcolor."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

st.set_page_config(page_title="Goals", page_icon="🎯", layout="wide")
st.title("🎯 Savings Goals")

for name, g in SAVINGS_GOALS.items():
    st.markdown(f"### {name}")
    col1, col2, col3 = st.columns([2, 1, 1])

    pct    = min(g["current"] / g["goal"], 1.0)
    months = months_to_goal(g["current"], g["goal"], g["monthly"], g["apy"])
    needed = g["goal"] - g["current"]

    with col1:
        st.progress(pct, text=f"${g['current']:,.0f} saved of ${g['goal']:,.0f}  ({pct*100:.1f}%)")

        bal, projection = g["current"], []
        r = g["apy"] / 12
        for m in range(int(months) + 1):
            projection.append({"Month": m, "Balance": round(bal, 2)})
            bal = bal * (1 + r) + g["monthly"]
            if bal >= g["goal"]:
                projection.append({"Month": m + 1, "Balance": g["goal"]})
                break

        xs = [p["Month"] for p in projection]
        ys = [p["Balance"] for p in projection]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill="tozeroy",
            line=dict(color=g["color"], width=2),
            fillcolor=hex_to_rgba(g["color"]),
            name="Projected Balance",
        ))
        fig.add_hline(y=g["goal"], line_dash="dash", line_color="#1F3864",
                      annotation_text=f"Goal: ${g['goal']:,}", annotation_position="top left")
        fig.update_layout(
            height=220,
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="Months from now",
            yaxis_title="Balance ($)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("Remaining",           f"${needed:,.0f}")
        st.metric("Monthly Contribution", f"${g['monthly']:,}")
        st.metric("APY",                 f"{g['apy']*100:.2f}%")

    with col3:
        st.metric("Est. Completion", f"{int(months)} months" if months < 600 else "∞")
        import datetime
        eta = datetime.date.today() + datetime.timedelta(days=int(months) * 30.4)
        st.metric("Target Date", eta.strftime("%b %Y") if months < 600 else "—")

        new_monthly = st.slider(
            "Adjust monthly contribution",
            min_value=0, max_value=3_000, value=g["monthly"], step=50,
            key=f"slider_{name}",
        )
        new_months = months_to_goal(g["current"], g["goal"], new_monthly, g["apy"])
        if new_monthly != g["monthly"]:
            st.caption(f"At ${new_monthly:,}/mo → **{int(new_months)} months**")

    st.markdown("---")