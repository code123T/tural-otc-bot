import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Telegram bot məlumatları
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "SƏNİN_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "SƏNİN_CHAT_ID")
SECRET_KEY = "TuralSecret2026"


def send_to_telegram(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=5)
  except Exception as e:
    print(f"Telegram xətası: {e}")


@app.route("/webhook", methods=["POST"])
def webhook():
  data = request.json

  # Təhlükəsizlik yoxlaması
  if not data or data.get("secret") != SECRET_KEY:
    return jsonify({"status": "error", "message": "Unauthorized"}), 401

  symbol = data.get("symbol", "EURUSD (OTC)")
  timeframe = data.get("timeframe", "M15")
  signal = data.get("signal", "CALL")
  price = data.get("price", "0.00000")
  score = data.get("score", "95")
  trend = data.get("trend", "MA Crossover")

  # Telegram üçün peşəkar mesaj formatı
  emoji = "🟢" if signal == "CALL" else "🔴"
  message = (
      f"🚀 *TURAL M15 TRADING SİQNALI* 🚀\n\n"
      f"📊 *Aktiv:* `{symbol}`\n"
      f"⏰ *Timeframe:* `{timeframe}`\n"
      f"{emoji} *İstiqamət:* *{signal}*\n"
      f"💰 *Giriş Qiyməti:* `{price}`\n"
      f"🎯 *Güvən Xalı:* `%`{score}\n"
      f"📈 *Trend:* {trend}\n\n"
      f"⚡ *Uğurlar, qardaş!*"
  )

  send_to_telegram(message)
  return jsonify({"status": "success", "message": "Signal sent to Telegram"}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))