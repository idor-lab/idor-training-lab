import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-only-change-me")
LAB_ACCESS_KEY = os.environ.get("LAB_ACCESS_KEY", "")

USERS = {
    "wiener": {"name": "Peter Wiener", "role": "user", "email": "wiener@example.test"},
    "carlos": {"name": "Carlos Montoya", "role": "user", "email": "carlos@example.test"},
    "alice": {"name": "Alice", "role": "manager", "email": "alice@example.test"},
    "admin": {"name": "Lab Admin", "role": "admin", "email": "admin@example.test"},
}
ORDERS = {
    "1001": {"owner": "wiener", "item": "Notebook Pro", "status": "Processing", "total": "€49.90", "delivery_address": "Testovací ulice 1"},
    "1002": {"owner": "carlos", "item": "Wireless Headphones", "status": "Shipped", "total": "€89.00", "delivery_address": "Testovací ulice 2"},
    "1003": {"owner": "alice", "item": "USB-C Dock", "status": "Delivered", "total": "€129.00", "delivery_address": "Testovací ulice 3"},
}
MESSAGES = {
    "501": {"owner": "wiener", "subject": "Welcome to the lab", "body": "This is Peter's fictional training message."},
    "502": {"owner": "carlos", "subject": "Order update", "body": "This is Carlos's fictional training message."},
}
LESSONS = [
    {"n": 1, "title": "Co je IDOR / BOLA", "level": "Začátečník", "desc": "Objekt, vlastník, identifikátor a kontrola oprávnění.", "status": "Připraveno"},
    {"n": 2, "title": "První test v Burp Repeater", "level": "Začátečník", "desc": "Zachycení požadavku a bezpečná změna identifikátoru.", "status": "Připraveno"},
    {"n": 3, "title": "Jeden objekt – mnoho endpointů", "level": "Mírně pokročilý", "desc": "Mapování všech operací nad jedním objektem.", "status": "Připraveno"},
    {"n": 4, "title": "ID v URL, query a JSON těle", "level": "Mírně pokročilý", "desc": "Hledání identifikátorů v různých částech HTTP požadavku.", "status": "Připravuje se"},
    {"n": 5, "title": "UUID a nepředvídatelné identifikátory", "level": "Mírně pokročilý", "desc": "Proč UUID nenahrazuje kontrolu oprávnění.", "status": "Připravuje se"},
]

def lab_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("lab_access"):
            return redirect(url_for("access"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/access", methods=["GET", "POST"])
def access():
    if request.method == "POST":
        if not LAB_ACCESS_KEY:
            flash("Laboratoř zatím není zabezpečena. Nastavte v Renderu proměnnou LAB_ACCESS_KEY.", "error")
        elif request.form.get("access_key", "") == LAB_ACCESS_KEY:
            session["lab_access"] = True
            flash("Přístup do výukové laboratoře povolen.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Přístupový klíč není správný.", "error")
    return render_template("access.html", configured=bool(LAB_ACCESS_KEY))

@app.route("/leave")
def leave():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@lab_required
def dashboard():
    return render_template("dashboard.html", users=USERS, orders=ORDERS, lessons=LESSONS)

@app.route("/lessons")
@lab_required
def lessons():
    return render_template("lessons.html", lessons=LESSONS)

@app.route("/lessons/<int:number>")
@lab_required
def lesson_detail(number):
    lesson = next((x for x in LESSONS if x["n"] == number), None)
    if not lesson:
        return "Lekce nebyla nalezena", 404
    return render_template("lesson.html", lesson=lesson)

@app.route("/lab")
@lab_required
def lab_home():
    return render_template("lab.html", users=USERS, orders=ORDERS)

@app.route("/lab/profile")
@lab_required
def profile():
    user_id = request.args.get("user_id", "wiener")
    # INTENTIONALLY VULNERABLE TRAINING ENDPOINT: missing ownership check.
    user = USERS.get(user_id)
    if not user:
        return "Profil nenalezen", 404
    return render_template("profile.html", user=user, user_id=user_id)

@app.route("/lab/orders/<order_id>")
@lab_required
def order_detail(order_id):
    # INTENTIONALLY VULNERABLE TRAINING ENDPOINT: missing ownership check.
    order = ORDERS.get(order_id)
    if not order:
        return "Objednávka nenalezena", 404
    return render_template("order.html", order=order, order_id=order_id)

@app.route("/api/orders/<order_id>", methods=["POST"])
@lab_required
def update_order(order_id):
    # INTENTIONALLY VULNERABLE TRAINING ENDPOINT: no object-ownership check.
    # This endpoint is available only after the separate lab access key is entered.
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "not_found"}), 404
    data = request.get_json(silent=True) or request.form
    allowed_statuses = {"Processing", "Shipped", "Delivered", "Cancelled"}
    new_status = data.get("status")
    new_address = data.get("delivery_address")
    if new_status:
        if new_status not in allowed_statuses:
            return jsonify({"error": "invalid_status"}), 400
        order["status"] = new_status
    if new_address:
        order["delivery_address"] = str(new_address)[:120]
    return jsonify({"message": "updated", "order_id": order_id, **order})

@app.route("/lab/messages/<message_id>")
@lab_required
def message_detail(message_id):
    # INTENTIONALLY VULNERABLE TRAINING ENDPOINT: missing ownership check.
    message = MESSAGES.get(message_id)
    if not message:
        return "Zpráva nenalezena", 404
    return render_template("message.html", message=message, message_id=message_id)

@app.route("/api/profile")
@lab_required
def api_profile():
    user_id = request.args.get("user_id", "wiener")
    # INTENTIONALLY VULNERABLE TRAINING ENDPOINT: missing ownership check.
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"user_id": user_id, **user})

@app.route("/api/orders/<order_id>")
@lab_required
def api_order(order_id):
    # INTENTIONALLY VULNERABLE TRAINING ENDPOINT: missing ownership check.
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"order_id": order_id, **order})

@app.route("/endpoint-map")
@lab_required
def endpoint_map():
    endpoints = [
        ("GET", "/lab/profile?user_id=...", "Profil uživatele", "IDOR – query parameter"),
        ("GET", "/lab/orders/<order_id>", "Detail objednávky", "IDOR – path parameter"),
        ("GET", "/lab/messages/<message_id>", "Detail zprávy", "IDOR – path parameter"),
        ("GET", "/api/profile?user_id=...", "JSON profil", "API / query parameter"),
        ("GET", "/api/orders/<order_id>", "JSON objednávka", "IDOR – čtení objektu"),
        ("POST", "/api/orders/<order_id>", "Změna stavu / doručovací adresy", "Write IDOR – záměrně zranitelné v oddělené laboratoři"),
    ]
    return render_template("endpoint_map.html", endpoints=endpoints)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "IDOR Training Lab PRO"})
@app.route("/api/orders/<order_id>", methods=["DELETE"])
@lab_required
def delete_order(order_id):
    # INTENTIONALLY VULNERABLE TRAINING ENDPOINT
    order = ORDERS.get(order_id)

    if not order:
        return jsonify({"error": "not_found"}), 404

    deleted_order = ORDERS.pop(order_id)

    return jsonify({
        "message": "deleted",
        "order_id": order_id,
        **deleted_order
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
