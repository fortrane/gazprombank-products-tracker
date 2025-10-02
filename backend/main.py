# main.py

import asyncio
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # автоматически подхватывает .env из корня проекта
from worker import start_scheduler
from db import DBClient
from routers.reviews_router import router as reviews_router
from routers.analytics_router import router as analytics_router


app = FastAPI(title="Reviews Intelligence API")

# подключаем роутеры
app.include_router(reviews_router)
app.include_router(analytics_router)


scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_event():
    db = DBClient.get_instance()
    await db.init()

    await start_scheduler()
    print("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    db = DBClient.get_instance()
    scheduler.shutdown()
    print("Scheduler stopped")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000
    )