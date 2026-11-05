
import os
import hmac
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TV_SECRET = os.getenv("TV_SECRET")

TELEGRAM_URL = (
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    if BOT_TOKEN else None
)


# CORS
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type,Authorization"
    )
    response.headers["Access-Control-Allow-Methods"] = (
        "GET,POST,OPTIONS"
    )
    return response


# Server health
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "bot": "TURAL OTC SIGNAL BOT",
        "status": "online",
        "timeframe": "M15"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "telegram_configured": bool(
            BOT_TOKEN and CHAT_ID
        ),
        "timeframe": "M15"
    })


# Telegram message sender
def send_telegram(message):
    if not TELEGRAM_URL or not CHAT_ID:
        return False

    try:
        response = requests.post(
            TELEGRAM_URL,
            json={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=15
        )

        return (
            response.ok
            and response.json().get("ok", False)
        )

    except requests.RequestException as error:
        print("Telegram error:", error)
        return False


# TradingView webhook
@app.route("/webhook", methods=["POST", "OPTIONS"])
def webhook():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    if not all([BOT_TOKEN, CHAT_ID, TV_SECRET]):
        return jsonify({
            "error": "Missing environment variables"
        }), 500

    data = request.get_json(silent=True) or {}

    received_secret = str(data.get("secret", ""))

    if not hmac.compare_digest(received_secret, TV_SECRET):
        return jsonify({
            "error": "Unauthorized"
        }), 401

    signal = str(data.get("signal", "WAIT")).upper()
    symbol = data.get("symbol", "EUR/USD OTC")
    timeframe = data.get("timeframe", "M15")
    price = data.get("price", "N/A")
    score = data.get("score", "N/A")
    trend = data.get("trend", "N/A")
    rsi = data.get("rsi", "N/A")
    adx = data.get("adx", "N/A")
    macd = data.get("macd", "N/A")

    if signal not in ("CALL", "PUT", "WAIT"):
        return jsonify({
            "error": "Invalid signal"
        }), 400

    emoji = {
        "CALL": "🟢",
        "PUT": "🔴",
        "WAIT": "🟡"
    }[signal]

    message = (
        f"{emoji} TURAL OTC SIGNAL BOT\n\n"
        f"Signal: {signal}\n"
        f"Asset: {symbol}\n"
        f"Timeframe: {timeframe}\n"
        f"Price: {price}\n\n"
        f"Score: {score}/100\n"
        f"Trend: {trend}\n"
        f"RSI: {rsi}\n"
        f"ADX: {adx}\n"
        f"MACD: {macd}\n\n"
        "Expiry: 15 minutes\n"
        "Risk: Demo testing recommended\n"
        "No profit guarantee"
    )

    if not send_telegram(message):
        return jsonify({
            "error": "Telegram delivery failed"
        }), 502

    print("Telegram signal sent:", signal)

    return jsonify({
        "status": "sent",
        "signal": signal,
        "timeframe": timeframe
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
