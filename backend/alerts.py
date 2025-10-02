# alerts.py

from datetime import datetime, timedelta
import httpx
from db import DBClient
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEGATIVE_THRESHOLD = 0.3


async def check_alerts(db: DBClient):
    to_date = datetime.now().date()
    from_date = to_date - timedelta(days=1)
    products = ["Кредитные карты", "Дебетовые карты"]

    for product in products:
        sentiment_data = await db.get_sentiment_aggregation(product, from_date, to_date, interval="hour")
        if not sentiment_data:
            continue

        for period in sentiment_data:
            negative_ratio = period.get("negative", 0)
            if negative_ratio >= NEGATIVE_THRESHOLD:
                message = (
                    f"ALERT: резкий рост негатива для {product}\n"
                    f"Период: {period['period']}\n"
                    f"Доля негативных отзывов: {negative_ratio*100:.1f}%\n"
                )
                await send_telegram(message)


async def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            print("Telegram send failed:", resp.text)
        else:
            print("Telegram alert sent")
