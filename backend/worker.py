from bs4 import BeautifulSoup
import asyncio
import requests
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import DBClient
from classifier import classify_review
from bert_summary import TopicSentimentSummarizer
import os

BASE_URL = "https://www.banki.ru/services/responses/list/ajax/"
BANK = "gazprombank"
async def fetch_data(page: int):
    """Запрос страницы отзывов"""
    params = {
        "page": page,
        "is_countable": "on",
        "bank": BANK
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print(f"[{datetime.now()}] ❌ Error fetching page {page}: {response.status_code}")
        return None

async def process_review(review: dict, db: DBClient):
    """Обработка одного отзыва: сохранение + классификация"""
    date_str = review.get("dateCreate")
    if date_str:
        try:
            review_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            review_date = None
    else:
        review_date = None
    soup = BeautifulSoup(review.get("text", ""), "html.parser")
    text = soup.get_text()
    review_data = {
        "product": BANK,
        "bank": BANK,
        "text": text,
        "date": datetime.fromtimestamp(review.get("date", 0)).date(),
        "dateCreate":review_date,
        "id":review.get("id", "")
    }
    review_id = await db.upsert_review(review_data)

    classification = await classify_review(review_data["text"])
    print("Classific",classification)
    aspects= TopicSentimentSummarizer().summarize_single_review(classification)
    print(aspects)
    await db.mark_review_classified(review_id, classification,aspects)

async def fetch_new_reviews_job():
    """Задача для подгрузки новых отзывов"""
    print(f"[{datetime.now()}] 🚀 Fetching new reviews...")

    db = DBClient.get_instance()
    # Убираем db.init() и db.close(), соединение уже инициализировано при старте

    for page in range(1,2):
        data = await fetch_data(page)

        if data:
            for r in data["data"]:
                try:
                    await process_review(r, db)
                except Exception as e:
                    print(f"Error processing review: {e}")
    print(f"[{datetime.now()}] ✅ Reviews updated.")


async def alerts_job():
    """Проверка алертов"""
    from alerts import check_alerts
    print(f"[{datetime.now()}] 🔔 Running alerts check...")
    db = DBClient.get_instance()
    await check_alerts(db)

async def start_scheduler():
    scheduler = AsyncIOScheduler()

    # каждые 10 минут — новые отзывы
    scheduler.add_job(lambda: asyncio.create_task(fetch_new_reviews_job()), 'interval', minutes=10)
    # каждые 5 минут — алерты
    scheduler.add_job(lambda: asyncio.create_task(alerts_job()), 'interval', minutes=5)

    scheduler.start()
    print("✅ Scheduler started")
    #await fetch_new_reviews_job()


