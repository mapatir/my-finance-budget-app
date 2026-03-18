"""Connect bank accounts via Plaid Link."""
import os
import json
import threading
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Connect Accounts", page_icon="🔗", layout="wide")
st.title("🔗 Connect Accounts")

from utils.plaid_client import load_tokens, get_plaid_client, TOKENS_FILE, fetch_transactions
from utils.data import monthly_averages

# ── Connection status ─────────────────────────────────────────────────────────
tokens  = load_tokens()
missing_keys = not os.getenv("PLAID_CLIENT_ID") or os.getenv("PLAID_CLIENT_ID") == "your_client_id_here"

if missing_keys:
    st.error("⚠️ Plaid API keys not found. Add them to your `.env` file first.")
    st.code("""
# In your .env file:
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=development
""")
    st.markdown("[Get free API keys → dashboard.plaid.com/signup](https://dashboard.plaid.com/signup)")
    st.stop()

if not tokens:
    st.warning("No bank accounts linked yet. Run the link flow below.")
else:
    st.success(f"✅ {len(tokens)} institution(s) connected: {', '.join(tokens.keys())}")

# ── Link new account (embedded Plaid Link via local Flask server) ─────────────
st.markdown("---")
st.subheader("Link a New Account")

st.markdown("""
To connect a bank account, run the setup script in a separate terminal window:

```bash
python plaid_sync/1_setup_plaid.py
```

A browser window will open with Plaid's secure bank login. Connect each institution one by one.
Once done, come back here and click **Sync Now**.
""")

st.markdown("---")

# ── Sync button ───────────────────────────────────────────────────────────────
st.subheader("Sync Transactions")

days = st.slider("Pull transactions from the last N days", 30, 90, 60)

if st.button("🔄 Sync Now", type="primary", use_container_width=True):
    if not tokens:
        st.error("No accounts linked. Run 1_setup_plaid.py first.")
    else:
        with st.spinner("Fetching transactions from all linked accounts..."):
            try:
                txns, balances = fetch_transactions(days=days)
                errors = [t for t in txns if t.get("_error")]
                clean  = [t for t in txns if not t.get("_error")]

                st.session_state["transactions"]    = clean
                st.session_state["balances"]        = balances
                st.session_state["monthly_averages"] = monthly_averages(clean)

                st.success(f"✅ Synced {len(clean)} transactions from {len(tokens)} institution(s).")

                if errors:
                    for e in errors:
                        st.warning(f"⚠️ {e['_error']}: {e['_msg']}")

                # Show balance summary
                if balances:
                    st.markdown("#### Account Balances")
                    cols = st.columns(min(len(balances), 4))
                    for (acct_id, acct), col in zip(balances.items(), cols):
                        col.metric(
                            f"{acct['institution']} — {acct['name']}",
                            f"${acct['balance']:,.2f}",
                        )
            except Exception as e:
                st.error(f"Sync failed: {e}")
                st.info("Make sure your .env file has valid Plaid credentials.")

# ── Last sync info ────────────────────────────────────────────────────────────
if "transactions" in st.session_state:
    txns = st.session_state["transactions"]
    st.caption(f"Session has {len(txns)} transactions loaded. Refresh the page or sync again to update.")
