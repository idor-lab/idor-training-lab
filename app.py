import os
from datetime import timedelta
from functools import wraps
from flask import Flask, request, session, redirect, jsonify, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-demo-only-change-this-key")
app.permanent_session_lifetime = timedelta(days=7)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Render serves HTTPS; Flask will set secure cookies behind its proxy.
    SESSION_COOKIE_SECURE=os.environ.get("RENDER", "") == "true",
)

USERS = {
    "wiener": {"password": "peter", "role": "user", "email": "wiener@lab.test", "display_name": "Wiener"},
    "carlos": {"password": "montoya", "role": "user", "email": "carlos@lab.test", "display_name": "Carlos"},
    "alice": {"password": "wonderland", "role": "user", "email": "alice@lab.test", "display_name": "Alice"},
    "admin": {"password": "admin123", "role": "admin", "email": "admin@lab.test", "display_name": "Training Admin"},
}

ORDERS = {
    "1001": {"owner": "wiener", "item": "Laptop", "status": "Shipped"},
    "1002": {"owner": "carlos", "item": "Phone", "status": "Processing"},
    "1003": {"owner": "alice", "item": "Tablet", "status": "Delivered"},
}
INVOICES = {
    "INV-001": {"owner": "wiener", "amount": 120, "text": "Wiener training invoice"},
    "INV-002": {"owner": "carlos", "amount": 450, "text": "Carlos training invoice"},
    "INV-003": {"owner": "alice", "amount": 230, "text": "Alice training invoice"},
}
MESSAGES = {
    "501": {"owner": "wiener", "text": "Private training message for Wiener"},
    "502": {"owner": "carlos", "text": "Private training message for Carlos"},
    "503": {"owner": "alice", "text": "Private training message for Alice"},
}
FILES = {
    "file-01": {"owner": "wiener", "name": "wiener-document.txt", "content": "Fictional Wiener training document"},
    "file-02": {"owner": "carlos", "name": "carlos-document.txt", "content": "Fictional Carlos training document"},
    "file-03": {"owner": "alice", "name": "alice-document.txt", "content": "Fictional Alice training document"},
}

PAGE = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDOR Training Lab</title>
<style>
body{font-family:Arial,sans-serif;background:#eef2f7;color:#1f2937;margin:0;padding:24px}
main{max-width:900px;margin:20px auto;background:white;padding:24px;border-radius:12px;box-shadow:0 4px 18px #0001}
h1{margin-top:0} .note{background:#fff7d6;padding:12px;border-radius:8px}
button,a.btn{display:inline-block;margin:6px 6px 6px 0;padding:10px 14px;background:#2457a7;color:white;border:0;border-radius:6px;text-decoration:none;cursor:pointer}
code{background:#edf0f5;padding:3px 5px;border-radius:4px} li{margin:9px 0}
small{color:#586579}
</style></head><body><main>
<h1>🧪 IDOR Training Lab</h1>
<p class="note"><b>Authorized training only.</b> This lab intentionally contains access-control flaws and uses fictional data. Do not enter real personal information or reuse real passwords. Keep this demo private to your own learning group.</p>
{% if user %}
<p>Signed in as <b>{{ user }}</b> — role: <b>{{ role }}</b></p>
<a class="btn" href="/logout">Log out</a>
<h2>Endpoint map</h2>
<ul>
<li><code>GET /api/profile?user_id=wiener</code> — profile lookup</li>
<li><code>GET /api/orders/1001</code> — read order</li>
<li><code>POST /api/orders/1001/status</code> — change order status (JSON: {"status":"Processing"})</li>
<li><code>GET /api/invoices/INV-001</code> — read invoice</li>
<li><code>GET /api/messages/501</code> — read message</li>
<li><code>GET /api/files/file-01</code> — read file metadata/content</li>
<li><code>GET /api/admin/users</code> — admin user listing</li>
<li><code>GET /api</code> — endpoint inventory</li>
</ul>
<p>Use Burp Suite Proxy → HTTP history → Send to Repeater. Compare objects owned by different fictional users.</p>
<h2>Training accounts</h2>
<ul>{% for name in accounts %}<li><b>{{name}}</b> — demo password: <code>{{passwords[name]}}</code></li>{% endfor %}</ul>
{% else %}
<h2>Choose a fictional training account</h2>
<p>These quick-login buttons are provided to make the lab easy to use. They are not real accounts.</p>
{% for name in accounts %}
<form method="post" action="/login"><input type="hidden" name="username" value="{{name}}">
<button type="submit">Log in as {{name}}</button></form>
{% endfor %}
{% endif %}
<hr><small>Training build 1.0 · Fictional records only · No real customer data</small>
</main></body></html>
"""

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Login required"}), 401
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    user = session.get("user")
    role = USERS[user]["role"] if user in USERS else None
    return render_template_string(
        PAGE, user=user, role=role,
        accounts=list(USERS),
        passwords={name: data["password"] for name, data in USERS.items()}
    )

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    if username not in USERS:
        return "Unknown training user", 400
    session.clear()
    session.permanent = True
    session["user"] = username
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# INTENTIONALLY VULNERABLE training endpoint: no object-level authorization.
@app.route("/api/profile")
@login_required
def profile():
    user_id = request.args.get("user_id", "")
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user_id": user_id, **USERS[user_id]})

@app.route("/api/orders/<order_id>")
@login_required
def order(order_id):
    if order_id not in ORDERS:
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"order_id": order_id, **ORDERS[order_id]})

@app.route("/api/orders/<order_id>/status", methods=["POST"])
@login_required
def update_order(order_id):
    if order_id not in ORDERS:
        return jsonify({"error": "Order not found"}), 404
    payload = request.get_json(silent=True) or {}
    new_status = str(payload.get("status", "Processing"))[:40]
    ORDERS[order_id]["status"] = new_status
    return jsonify({"updated": True, "order_id": order_id, "status": new_status})

@app.route("/api/invoices/<invoice_id>")
@login_required
def invoice(invoice_id):
    if invoice_id not in INVOICES:
        return jsonify({"error": "Invoice not found"}), 404
    return jsonify({"invoice_id": invoice_id, **INVOICES[invoice_id]})

@app.route("/api/messages/<message_id>")
@login_required
def message(message_id):
    if message_id not in MESSAGES:
        return jsonify({"error": "Message not found"}), 404
    return jsonify({"message_id": message_id, **MESSAGES[message_id]})

@app.route("/api/files/<file_id>")
@login_required
def file(file_id):
    if file_id not in FILES:
        return jsonify({"error": "File not found"}), 404
    return jsonify({"file_id": file_id, **FILES[file_id]})

@app.route("/api/admin/users")
@login_required
def admin_users():
    return jsonify(USERS)

@app.route("/api")
@login_required
def api_index():
    return jsonify({
        "profile": "/api/profile?user_id=wiener",
        "orders": ["/api/orders/1001", "/api/orders/1002", "/api/orders/1003"],
        "invoices": ["/api/invoices/INV-001", "/api/invoices/INV-002", "/api/invoices/INV-003"],
        "messages": ["/api/messages/501", "/api/messages/502", "/api/messages/503"],
        "files": ["/api/files/file-01", "/api/files/file-02", "/api/files/file-03"],
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "IDOR Training Lab"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
