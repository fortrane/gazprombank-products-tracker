from fastapi import APIRouter, HTTPException, Query
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from db import DBClient
from fastapi import Depends, Header, HTTPException, status
import os
from datetime import datetime
router = APIRouter(tags=["analytics"])

API_KEY=os.getenv("API_KEY")
names_dict={
        "debit": "Дебетовые карты",
        "credit": "Кредитные карты",
        "bonuses": "Акции и бонусы",
        "cash_loans": "Кредиты наличными",
        "deposits": "Вклады",
        "mortgage": "Ипотека",
        "auto_loans": "Автокредиты",
        "refinance_loans": "Рефинансирование кредитов",
        "refinance_mortgage": "Рефинансирование ипотеки",
        "currency_exchange": "Обмен валют",
        "conditions": "Условия",
        "money_transfers": "Денежные переводы",
        "mobile_app": "Мобильное приложение",
        "rko": "РКО",
        "acquiring": "Эквайринг",
        "service": "Обслуживание",
        "remote_service": "Дистанционное обслуживание",
        "support_chat": "Техподдержка и чат",
        "other": "Другие услуги"
    }
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

class chartdata(BaseModel):
    products: List[str]
    start: date
    end: date
    include: List[str]


@router.post("/chart_data")
async def sentiment_trends(
    data: chartdata,_: str = Depends(verify_api_key)
):

    products_trnsl = [names_dict[p] for p in data.products if p in names_dict]
    db = DBClient.get_instance()
    data = await db.get_sentiment_aggregation(products_trnsl, data.start, data.end, "day")
    summary=aggregate_reviews(data["candles"])
    data["summary"]=summary
    if not data:
        raise HTTPException(status_code=404, detail="Нет данных по этому продукту")
    return data

def aggregate_reviews(data):
    if not data:
        return {
            "period": None,
            "positive": 0,
            "positive_count": 0,
            "neutral": 0,
            "neutral_count": 0,
            "negative": 0,
            "negative_count": 0,
            "total_reviews": 0
        }
    dates = sorted([d["date"] for d in data], key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
    period = f"{dates[0]} - {dates[-1]}"

    total_reviews = sum(d["total_reviews"] for d in data)
    positive_count = sum(d["positive_count"] for d in data)
    neutral_count = sum(d["neutral_count"] for d in data)
    negative_count = sum(d["negative_count"] for d in data)
    positive = round(positive_count / total_reviews, 2) if total_reviews else 0
    neutral = round(neutral_count / total_reviews, 2) if total_reviews else 0
    negative = round(negative_count / total_reviews, 2) if total_reviews else 0

    return {
        "period": period,
        "positive": positive,
        "positive_count": positive_count,
        "neutral": neutral,
        "neutral_count": neutral_count,
        "negative": negative,
        "negative_count": negative_count,
        "total_reviews": total_reviews
    }




@router.get("/products")
async def get_products(_: str = Depends(verify_api_key)):
    return names_dict


@router.get("/statistics")
async def get_statistics(_: str = Depends(verify_api_key)):
    db = DBClient.get_instance()
    data= await db.get_all_stats()
    return data


@router.get("/last_review_id")
async def last_review_id(_: str = Depends(verify_api_key)):
    db = DBClient.get_instance()
    data= await db.get_last_review_id()
    return {"last_id": data}