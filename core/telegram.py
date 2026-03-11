import requests
import os

def send_telegram(message: str):
    token   = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram not configured")
        return

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text":    message,
            "parse_mode": "Markdown"   # supports *bold* and _italic_
        })
        return response.json()
    except Exception as e:
        print(f"Telegram error: {e}")
