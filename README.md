# IDOR Training Lab

A deliberately vulnerable web application for **authorized, isolated security training**. All records and accounts are fictional.

## Demo accounts

| Username | Password | Role |
|---|---|---|
| wiener | peter | user |
| carlos | montoya | user |
| alice | wonderland | user |
| admin | admin123 | admin |

The login page provides quick-login buttons for convenience. Do not reuse real passwords.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:10000

## Deploy to Render

1. Create a GitHub repository and upload these files to its root.
2. In Render, create a **New Web Service** and connect the repository.
3. Runtime: Python. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variable `SECRET_KEY` with a long random value you keep private.
6. Deploy. Render assigns the public URL.

For a public deployment, only use this lab with fictional data. Anyone who can reach the URL may be able to exercise its intentionally vulnerable endpoints. Do not deploy this alongside real services or real data.

## Important behavior

- The session cookie is configured as permanent for 7 days.
- A stable `SECRET_KEY` is required for sessions to remain valid across server restarts/deploys.
- The free hosting tier may sleep while idle; the first request after sleep can be delayed.
- Demo objects are stored in memory and reset when the process restarts. This is intentional for a disposable training lab.
- This first build focuses on horizontal IDOR and multiple endpoints. Later lessons can add UUID, GraphQL, multi-tenant cases, blind/second-order scenarios, and safe-vs-vulnerable comparisons.

## Endpoint map

- `GET /api/profile?user_id=wiener`
- `GET /api/orders/1001`
- `POST /api/orders/1001/status` with JSON body `{"status":"Processing"}`
- `GET /api/invoices/INV-001`
- `GET /api/messages/501`
- `GET /api/files/file-01`
- `GET /api/admin/users`
- `GET /api`
