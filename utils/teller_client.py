"""Teller.io client for fetching transactions and managing bank account connections."""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# ── File paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CERT_FILE = DATA_DIR / "certificate.pem"
KEY_FILE = DATA_DIR / "private_key.pem"
TOKENS_FILE = DATA_DIR / "teller_tokens.json"

# ── Teller API ─────────────────────────────────────────────────────────────────
TELLER_API_BASE = "https://api.teller.io"


def certs_available() -> bool:
    """Check if Teller certificate files are present."""
    return CERT_FILE.exists() and KEY_FILE.exists()


def load_tokens() -> Dict[str, str]:
    """Load saved access tokens from file."""
    if not TOKENS_FILE.exists():
        return {}
    try:
        with open(TOKENS_FILE, "r") as f:
            data = json.load(f)
            # Return just the access tokens in a simple dict
            return {inst: data[inst]["access_token"] for inst in data}
    except Exception as e:
        print(f"⚠️ Error loading tokens: {e}")
        return {}


def save_token(institution: str, access_token: str, enrollment_id: str = "") -> None:
    """Save a new Teller access token."""
    tokens = {}
    if TOKENS_FILE.exists():
        try:
            with open(TOKENS_FILE, "r") as f:
                tokens = json.load(f)
        except:
            tokens = {}

    tokens[institution] = {
        "access_token": access_token,
        "enrollment_id": enrollment_id,
        "saved_at": datetime.now().isoformat()
    }

    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    print(f"✅ Saved token for {institution}")


def teller_get(path: str, access_token: str) -> dict:
    """Make an authenticated GET request to Teller API with mutual TLS."""
    url = f"{TELLER_API_BASE}{path}"

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            cert=(str(CERT_FILE), str(KEY_FILE)),
            verify=True,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def fetch_all_transactions(days: int = 60) -> Tuple[List[dict], Dict]:
    """
    Fetch transactions from all linked accounts.

    Returns:
        (transactions_list, balances_dict)
        - transactions_list: List of transaction dicts with fields:
          {date, description, amount, category, _error (if failed)}
        - balances_dict: {account_id: {institution, name, balance}}
    """
    tokens = load_tokens()

    if not tokens:
        print("⚠️ No accounts linked. Run Connect_Accounts page first.")
        return [], {}

    all_transactions = []
    balances = {}

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for institution, access_token in tokens.items():
        try:
            # Get accounts for this institution
            accounts_resp = teller_get("/accounts", access_token)

            if "error" in accounts_resp:
                all_transactions.append({
                    "_error": institution,
                    "_msg": accounts_resp.get("error", "Failed to fetch accounts")
                })
                continue

            accounts = accounts_resp.get("accounts", [])

            for account in accounts:
                account_id = account.get("id")
                account_name = account.get("name", "Unknown")
                account_balance = account.get("balance", 0)

                # Store balance info
                balances[account_id] = {
                    "institution": institution,
                    "name": account_name,
                    "balance": account_balance
                }

                # Fetch transactions for this account
                params = {
                    "account_id": account_id,
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d")
                }

                txns_resp = teller_get("/transactions", access_token)

                if "error" in txns_resp:
                    all_transactions.append({
                        "_error": institution,
                        "_msg": txns_resp.get("error", "Failed to fetch transactions"),
                        "account": account_name
                    })
                    continue

                transactions = txns_resp.get("transactions", [])

                for txn in transactions:
                    all_transactions.append({
                        "date": txn.get("date", ""),
                        "description": txn.get("description", ""),
                        "amount": float(txn.get("amount", 0)),
                        "category": "Uncategorized",
                        "institution": institution,
                        "account": account_name,
                        "account_id": account_id
                    })

        except Exception as e:
            all_transactions.append({
                "_error": institution,
                "_msg": f"Exception: {str(e)}"
            })

    # Sort transactions by date (newest first)
    all_transactions.sort(key=lambda x: x.get("date", ""), reverse=True)

    return all_transactions, balances


def delete_token(institution: str) -> None:
    """Remove a saved token."""
    if not TOKENS_FILE.exists():
        return

    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)

        if institution in tokens:
            del tokens[institution]
            with open(TOKENS_FILE, "w") as f:
                json.dump(tokens, f, indent=2)
            print(f"✅ Removed token for {institution}")
    except Exception as e:
        print(f"⚠️ Error deleting token: {e}")
