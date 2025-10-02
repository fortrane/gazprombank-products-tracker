from bert_summary import TopicSentimentSummarizer
import os
from fastapi import BackgroundTasks
from routers.analytics_router import names_dict
from datetime import timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional
from worker import fetch_data,process_review
from db import DBClient
from classifier import classify_review
from datetime import datetime
from fastapi import Depends, Header, HTTPException, status
import asyncio

BASE_URL = "https://www.banki.ru/services/responses/list/ajax/"
BANK = "gazprombank"
API_KEY=os.getenv("API_KEY")

parse_state = {
    "is_task": False,
    "last_parse_date": None,
}
class ReviewIn(BaseModel):
    product: str
    text: str
    date: date


class ReviewOut(BaseModel):
    id: int
    product: str
    bank: Optional[str]
    text: str
    date: date
    sentiment: Optional[str] = None
    topics: Optional[list] = None
    aspects: Optional[list] = None

class ReviewsPaginatedFilter(BaseModel):
    products: Optional[List[str]] = None
    themes: Optional[List[str]] = None
    start: Optional[str] = None
    end: Optional[str] = None
    page: int = 1
    per_page: int = 20

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )


router = APIRouter(tags=["reviews"])

# ----- Pydantic схемы для фильтрации -----
class ReviewsFilter(BaseModel):
    products: Optional[List[str]] = None
    themes: Optional[List[str]] = None
    start: Optional[str] = None
    end: Optional[str] = None
    limit: int = 10
    index: int = 0
class BulkReviewIn(BaseModel):
    id: int
    text: str

class BulkReviewsRequest(BaseModel):
    data: List[BulkReviewIn]

class ReviewOutFiltered(BaseModel):
    polarity: str
    review_text: str
    positive_aspects: List[str]
    negative_aspects: List[str]
    themes: List[str]
    product: str
    date: date


class ReviewsResponse(BaseModel):
    reviews: List[ReviewOutFiltered]
    metadata: dict


@router.post("/reviews")
async def get_reviews(filter: ReviewsFilter,_: str = Depends(verify_api_key)):
    products_trnsl = [names_dict[p] for p in filter.products if p in names_dict]
    db = DBClient.get_instance()

    result = await db.get_reviews2(
        products_trnsl,
        filter.themes,
        filter.start,
        filter.end,
        filter.limit,
        filter.index
    )

    if result is None or not result.get("reviews"):
        return {"reviews": [], "metadata": {"total_count": 0, "current_index": filter.index, "has_more": False}}

    return result

class ReviewsStart(BaseModel):
    pages: int = 10

@router.post("/bankiru")
async def start_parse_banki_ru(_: str = Depends(verify_api_key)):

    db = DBClient.get_instance()

    for page in range(1, 40):
        data = await fetch_data(page)

        if data:
            for r in data["data"]:
                try:
                    await process_review(r, db)
                except Exception as e:
                    print(f"Error processing review: {e}")

@router.get("/parse_status")
async def get_parse_status(_: str = Depends(verify_api_key)):
    return {
        "is_task": parse_state["is_task"],
        "last_parse_date": (
            (parse_state["last_parse_date"] + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
            if parse_state["last_parse_date"] else None
        )
    }

@router.post("/start_collecting")
async def start_collecting(_: str = Depends(verify_api_key)):
    if parse_state["is_task"]:
        return {
            "status": "already_running",
            "message": "Процесс сбора уже запущен"
        }
    asyncio.create_task(run_collecting())

    return {
        "status": "started",
        "message": "Процесс сбора отзывов запущен"
    }

async def run_collecting():
    parse_state["is_task"] = True
    parse_state["last_parse_date"] = datetime.now()

    db = DBClient.get_instance()
    for page in range(1, 2):
        data = await fetch_data(page)
        if data:
            for r in data["data"]:
                try:
                    await process_review(r, db)
                except Exception as e:
                    print(f"Error processing review: {e}")

    parse_state["is_task"] = False



@router.post("/reviews_paginated")
async def get_reviews_paginated(filter: ReviewsPaginatedFilter,_: str = Depends(verify_api_key)):
    db = DBClient.get_instance()
    products_trnsl = [names_dict[p] for p in filter.products if p in names_dict]
    offset = (filter.page - 1) * filter.per_page

    result = await db.get_reviews_pag(
        products_trnsl,
        filter.themes,
        filter.start,
        filter.end,
        filter.per_page,
        offset
    )

    if result is None or not result.get("reviews"):
        return {
            "reviews": [],
            "pagination": {
                "current_page": filter.page,
                "total_pages": 0,
                "total_count": 0,
                "per_page": filter.per_page
            }
        }

    total_count = result["metadata"]["total_count"]
    total_pages = (total_count + filter.per_page - 1) // filter.per_page

    return {
        "reviews": result["reviews"],
        "pagination": {
            "current_page": filter.page,
            "total_pages": total_pages,
            "total_count": total_count,
            "per_page": filter.per_page
        }
    }


@router.post("/add_single_review")
async def create_review(review: ReviewIn,background_tasks: BackgroundTasks,_: str = Depends(verify_api_key)):

    db = DBClient.get_instance()
    review_data = {
        "product": "gazprombank",
        "bank": "gazprombank",
        "text": review.text,
        "date": review.date,
        "dateCreate": review.date,
    }
    review_id = await db.upsert_review(review_data)

    classification = await classify_review(review_data["text"])
    aspects={}
    await db.mark_review_classified(review_id, classification, aspects)
    background_tasks.add_task(process_aspects, review_id, classification, db)

    return {"status": "success","message": "Отзыв добавлен"}


async def process_aspects(review_id, classification, db):
    aspects = TopicSentimentSummarizer().summarize_single_review(classification)
    print(aspects)
    await db.mark_review_aspect(review_id, aspects)


@router.post("/bulk_add_reviews")
async def bulk_add_reviews(request: BulkReviewsRequest, background_tasks: BackgroundTasks,_: str = Depends(verify_api_key)):
    db = DBClient.get_instance()
    reviews = request.data
    count = 0

    today = date.today()
    for review in reviews:
        review_data = {
            "product": "gazprombank",
            "bank": "gazprombank",
            "text": review.text,
            "date": today,
            "dateCreate": today,
        }

        review_id = await db.upsert_review(review_data)

        classification = await classify_review(review_data["text"])
        aspects = {}
        await db.mark_review_classified(review_id, classification, aspects)

        background_tasks.add_task(process_aspects, review_id, classification, db)

        count += 1

    return {
        "status": "success",
        "message": "Отзывы добавлены",
        "count": count
    }



@router.post("/predict")
async def predict_reviews(request: BulkReviewsRequest, _: str = Depends(verify_api_key)):
    reviews = request.data
    count = 0
    sentiment_map = {
        "positive": "положительно",
        "negative": "отрицательно",
        "neutral": "нейтрально"
    }
    today = date.today()
    predictions=[]
    for review in reviews:
        review_data = {

            "id": review.id,
            "text": review.text,
        }
        classification = await classify_review(review_data["text"])
        prediction = {
            "id": review.id,
            "topics": list(classification["topic_fragments"].keys()),
            "sentiments": [sentiment_map[v["sentiment"]] for v in classification["topic_fragments"].values()]
        }

        predictions.append(prediction)

        count += 1

    return {
        "predictions": predictions
    }