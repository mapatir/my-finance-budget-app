# 💰 Personal Finance App

A personal finance dashboard built with Streamlit + Plaid. Runs locally on your Mac and looks great on iPhone via Safari.

## Folder Structure

```
finance-app/
├── app.py                  ← Main entry point
├── requirements.txt        ← Python dependencies
├── .env.example            ← Copy to .env and fill in keys
├── .gitignore              ← Keeps secrets out of Git
├── pages/
│   ├── 1_dashboard.py      ← Overview: income, cash flow, goals
│   ├── 2_spending.py       ← Budget vs actual, transaction list
│   ├── 3_goals.py          ← Savings goals with projections
│   ├── 4_debt.py           ← Debt payoff + RSU payoff scenario
│   ├── 5_rsu.py            ← Amazon RSU tracker + sell simulator
│   ├── 6_connect.py        ← Plaid bank linking + sync
│   └── 7_settings.py       ← Edit budget targets & balances
├── utils/
│   ├── plaid_client.py     ← Plaid API + transaction categorization
│   └── data.py             ← Your budget targets, goals, debts, RSU
└── data/
    └── plaid_tokens.json   ← Created after linking accounts (git-ignored)
```

## One-Time Setup

### 1. Open in VS Code
```bash
code finance-app
```

### 2. Create a virtual environment
```bash
cd finance-app
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your .env file
```bash
cp .env.example .env
```
Then open `.env` and fill in:
- `PLAID_CLIENT_ID` and `PLAID_SECRET` from [dashboard.plaid.com](https://dashboard.plaid.com/signup)
- `APP_PASSWORD` — any password you choose (used when you host online)

### 5. Run the app
```bash
streamlit run app.py
```
Opens at http://localhost:8501

## Connecting Your Banks (Plaid)

1. Get free API keys at [dashboard.plaid.com/signup](https://dashboard.plaid.com/signup)
2. Add keys to `.env`
3. Run the bank linking script:
   ```bash
   python ../plaid_sync/1_setup_plaid.py
   ```
4. Click **+ Connect a Bank** and link Chase, Amex, PNC, Apple Card
5. Come back to the app → **🔗 Connect Accounts** → **Sync Now**

## Making Permanent Changes

All your financial data lives in `utils/data.py`. Open it in VS Code to:
- Update savings goal balances
- Change budget targets
- Add/remove debts
- Update RSU share count

## Use on iPhone

1. Run the app locally: `streamlit run app.py`
2. Find your Mac's local IP: System Settings → Wi-Fi → Details
3. On your iPhone Safari, go to: `http://YOUR_MAC_IP:8501`
4. Tap **Share → Add to Home Screen**

Or, to access from anywhere (not just home Wi-Fi), deploy to Render.com — see DEPLOY.md.

## Updating the App

Since this is in VS Code, you can edit any page and the app hot-reloads automatically.
Use Git to track your changes:
```bash
git init
git add .
git commit -m "Initial finance app"
```
