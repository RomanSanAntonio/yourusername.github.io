from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import random
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

companies = {
    1: {"id": 1, "name": "Quantum Pizza", "ticker": "QPZ", "price": 10.0, "max_shares": 100000, "available": 100000},
    2: {"id": 2, "name": "FrogCoin Labs", "ticker": "FROG", "price": 5.0, "max_shares": 200000, "available": 200000}
}

holdings = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/companies")
def get_companies():
    return jsonify(list(companies.values()))

@app.route("/api/trade", methods=["POST"])
def trade():
    data = request.json
    user = data["user"]
    cid = int(data["company_id"])
    action = data["action"]
    amount = int(data["amount"])

    c = companies[cid]

    holdings.setdefault(user, {})
    holdings[user].setdefault(cid, 0)

    if action == "buy":
        if amount > c["available"]:
            return jsonify({"error": "Not enough shares"}), 400
        c["available"] -= amount
        holdings[user][cid] += amount
        c["price"] *= 1 + (amount / c["max_shares"]) * 0.02

    elif action == "sell":
        if holdings[user][cid] < amount:
            return jsonify({"error": "Not enough owned"}), 400
        holdings[user][cid] -= amount
        c["available"] += amount
        c["price"] *= 1 - (amount / c["max_shares"]) * 0.02

    socketio.emit("update", companies)
    return jsonify({"ok": True})

def market_loop():
    while True:
        time.sleep(1)
        for c in companies.values():
            drift = random.uniform(-0.5, 0.5)
            c["price"] *= (1 + drift / 100)
            c["price"] = max(0.1, c["price"])
        socketio.emit("update", companies)

threading.Thread(target=market_loop, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, debug=True)
