
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TV_SECRET = os.environ["TV_SECRET"]

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    if data.get("secret") != TV_SECRET:
        return jsonify({"error": "Unauthorized"}), 401

    signal = data.get("signal", "UNKNOWN")
    symbol = data.get("symbol", "UNKNOWN")
    timeframe = data.get("timeframe", "M1")
    price = data.get("price", "N/A")
    score = data.get("score", "N/A")
    trend = data.get("trend", "N/A")

    if signal not in ("CALL", "PUT"):
        return jsonify({"error": "Invalid signal"}), 400

    emoji = "🟢" if signal == "CALL" else "🔴"

    message = (
        f"{emoji} ICT SMC OTC SIGNAL\n\n"
        f"Signal: {signal}\n"
        f"Asset: {symbol}\n"
        f"Timeframe: {timeframe}\n"
        f"Price: {price}\n"
        f"Score: {score}/100\n"
        f"M15 Trend: {trend}\n\n"
        "Status: Confirmed candle\n"
        "Risk: Demo testing recommended"
    )

    response = requests.post(
        TELEGRAM_URL,
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=10
    )

    if not response.ok:
        return jsonify({"error": "Telegram delivery failed"}), 502

    return jsonify({"status": "sent"})
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )