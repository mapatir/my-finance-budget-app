"""Plaid API client — shared across all pages."""
import os
import json
from pathlib import Path
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

TOKENS_FILE = Path(__file__).parent.parent / "data" / "plaid_tokens.json"
TOKENS_FILE.parent.mkdir(exist_ok=True)

CATEGORY_RULES = {
    "Groceries":       ["WHOLE FOODS","TRADER JOE","GIANT","SAFEWAY","KROGER",
                        "COSTCO","ALDI","FOOD LION","HARRIS TEETER","WEGMANS",
                        "SHOPPERS","LIDL","PUBLIX"],
    "Dining":          ["RESTAURANT","DOORDASH","UBER EATS","GRUBHUB","SEAMLESS",
                        "CHICK-FIL-A","MCDONALD","STARBUCKS","CHIPOTLE","PANERA",
                        "SUBWAY","DOMINO","PIZZA","SUSHI","CAFE","DINER","GRILL",
                        "KITCHEN","BISTRO","TAVERN","BAR ","BREWERY"],
    "Shopping":        ["AMAZON","TARGET","WALMART","BEST BUY","NORDSTROM",
                        "MACY","TJ MAXX","MARSHALLS","ROSS ","HOME DEPOT",
                        "LOWE'S","IKEA","ZARA","H&M","GAP ","OLD NAVY"],
    "Subscriptions":   ["NETFLIX","SPOTIFY","APPLE ","GOOGLE ","HULU","DISNEY",
                        "HBO","AMAZON PRIME","YOUTUBE","MICROSOFT","ADOBE",
                        "DROPBOX","OPENAI","CHATGPT","CLAUDE"],
    "Health":          ["CVS","WALGREENS","PHARMACY","DOCTOR","DENTAL","VISION",
                        "HOSPITAL","CLINIC","MEDICAL","HEALTH","GYM","FITNESS",
                        "PLANET FITNESS","EQUINOX","ORANGE THEORY"],
    "Gas/EV":          ["SHELL","EXXON","BP ","CHEVRON","SUNOCO","MOBIL",
                        "WAWA","SHEETZ","CHARGING","TESLA","BLINK ","CHARGEPOINT",
                        "EVGO","ELECTRIFY"],
    "Pets":            ["PETCO","PETSMART","VET ","ANIMAL","PET SUPPLIES","CHEWY"],
    "Transport":       ["UBER","LYFT","METRO","WMATA","PARKING","EZ PASS",
                        "TOLL ","AMTRAK","AIRLINE","FLIGHT","DELTA","UNITED",
                        "SOUTHWEST","AMERICAN AIR"],
    "Entertainment":   ["TICKETMASTER","AMC ","REGAL ","CINEMA","CONCERT",
                        "MUSEUM","ZOO ","SPORT"],
    "Utilities":       ["DOMINION","PEPCO","BGE ","WASHINGTON GAS",
                        "VERIZON","AT&T","T-MOBILE","COMCAST","COX "],
    "Savings/Transfer":["FORBRIGHT","TAB BANK","AMEX SAVINGS","TRANSFER",
                        "ZELLE ","VENMO"],
}

def categorize(name: str) -> str:
    name_upper = name.upper()
    for cat, keywords in CATEGORY_RULES.items():
        if any(kw in name_upper for kw in keywords):
            return cat
    return "Other"

def get_plaid_client():
    try:
        from plaid.api import plaid_api
        from plaid.configuration import Configuration
        from plaid.api_client import ApiClient

        env_map = {
            "sandbox":     "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production":  "https://production.plaid.com",
        }
        env = os.getenv("PLAID_ENV", "development")
        config = Configuration(
            host=env_map[env],
            api_key={
                "clientId": os.getenv("PLAID_CLIENT_ID", ""),
                "secret":   os.getenv("PLAID_SECRET", ""),
            },
        )
        return plaid_api.PlaidApi(ApiClient(config))
    except Exception:
        return None

def load_tokens() -> dict:
    if TOKENS_FILE.exists():
        return json.loads(TOKENS_FILE.read_text())
    return {}

def save_token(institution: str, access_token: str, item_id: str):
    tokens = load_tokens()
    tokens[institution] = {"access_token": access_token, "item_id": item_id}
    TOKENS_FILE.write_text(json.dumps(tokens, indent=2))

def fetch_transactions(days: int = 60) -> tuple[list, dict]:
    """Returns (transactions_list, account_balances_dict)."""
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
    from plaid.model.accounts_get_request import AccountsGetRequest

    client = get_plaid_client()
    tokens = load_tokens()

    end   = date.today()
    start = end - timedelta(days=days)

    all_txns     = []
    all_balances = {}

    for institution, creds in tokens.items():
        token = creds["access_token"]
        try:
            resp = client.transactions_get(
                TransactionsGetRequest(
                    access_token=token,
                    start_date=start,
                    end_date=end,
                    options=TransactionsGetRequestOptions(count=500),
                )
            )
            for t in resp["transactions"]:
                if t.get("pending"):
                    continue
                all_txns.append({
                    "date":        str(t["date"]),
                    "name":        t["name"],
                    "amount":      float(t["amount"]),
                    "category":    categorize(t["name"]),
                    "institution": institution,
                    "account_id":  t["account_id"],
                })
        except Exception as e:
            all_txns.append({"_error": institution, "_msg": str(e)})

        try:
            acct_resp = client.accounts_get(AccountsGetRequest(access_token=token))
            for a in acct_resp["accounts"]:
                all_balances[a["account_id"]] = {
                    "name":        a["name"],
                    "institution": institution,
                    "type":        str(a["type"]),
                    "subtype":     str(a.get("subtype", "")),
                    "balance":     float(a["balances"]["current"] or 0),
                    "available":   float(a["balances"].get("available") or 0),
                }
        except Exception:
            pass

    return all_txns, all_balances
