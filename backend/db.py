import os
from typing import Any, Dict, List, Optional
import json
from collections import defaultdict
from datetime import datetime, date
import asyncpg

class DBClient:
    _instance = None

    def __init__(self):
        self.conn: Optional[asyncpg.Connection] = None
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')

        if not all([self.db_name, self.db_user, self.db_password, self.db_host, self.db_port]):
            raise EnvironmentError("One or more required environment variables are missing")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DBClient()
        return cls._instance

    async def init(self):
        try:
            self.conn = await asyncpg.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
        except asyncpg.PostgresError as e:
            raise e

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def upsert_review(self, review: Dict[str, Any]) -> int:
        """Insert or update review by id (if exists)."""
        query = """
        INSERT INTO reviews (product, bank, text, date,id_gaz)
        VALUES ($1, $2, $3, $4,$5)
        ON CONFLICT (id_gaz)
        DO UPDATE SET product = EXCLUDED.product,
                      bank = EXCLUDED.bank,
                      text = EXCLUDED.text,
                      date = EXCLUDED.date,
                      id_gaz = EXCLUDED.id_gaz
        RETURNING id;
        """
        #print(review.get("product"), review.get("bank"), review.get("dateCreate"), review.get("id"))
        return await self.conn.fetchval(query, review.get("product"), review.get("bank"), review.get("text"), review.get("dateCreate"), review.get("id"))

    async def get_review_by_id(self, review_id: int) -> Optional[Dict[str, Any]]:
        row = await self.conn.fetchrow("SELECT * FROM reviews WHERE id = $1", review_id)
        return dict(row) if row else None

    async def mark_review_classified(self, review_id: int, classification: Dict[str, Any], aspects: Dict):
        topics_json = json.dumps(classification.get("topics", []))
        topic_fragments_json = json.dumps(classification.get("topic_fragments", {}))
        aspects = json.dumps(aspects)
        query = """
        UPDATE reviews
        SET sentiment = $2,
            topics = $3,
            aspects = $4,
            topic_fragments = $5
        WHERE id = $1;
        """


        await self.conn.execute(
            query,
            review_id,
            classification.get("sentiment"),
            topics_json,
            aspects,
            topic_fragments_json
        )
    async def mark_review_aspect(self, review_id: int,  aspects: Dict):

        aspects = json.dumps(aspects)
        query = """
        UPDATE reviews
        SET 
            aspects = $2
        WHERE id = $1;
        """


        await self.conn.execute(
            query,
            review_id,
            aspects
        )
    # В DBClient

    async def get_sentiment_aggregation(self, topic_names: List[str], from_date: date, to_date: date,
                                               interval: str = "day"):

        query = """
            SELECT id, date, topic_fragments
            FROM reviews
            WHERE date BETWEEN $1 AND $2
        """
        rows = await self.conn.fetch(query, from_date, to_date)
        sentiment_by_period = defaultdict(lambda: defaultdict(int))
        total_by_period = defaultdict(int)
        for row in rows:
            review_date = row["date"]
            topic_fragments = json.loads(row["topic_fragments"])
            if interval == "day":
                period = review_date
            elif interval == "week":
                period = review_date.isocalendar()[0:2]
            elif interval == "month":
                period = (review_date.year, review_date.month)
            else:
                period = review_date

            if len(topic_names) > 0:
                for topic_name in topic_names:
                    if topic_name in topic_fragments:
                        sentiment = topic_fragments[topic_name].get("sentiment")
                        sentiment_by_period[period][sentiment] += 1
                        total_by_period[period] += 1

            else:

                for topic_name, info in topic_fragments.items():
                    sentiment = info.get("sentiment")
                    sentiment_by_period[period][sentiment] += 1
                    total_by_period[period] += 1
                    #print("+1", sentiment_by_period, total_by_period)

        trends = []
        for period, counts in sorted(sentiment_by_period.items()):
            total = total_by_period[period]
            trends.append({
                "date": str(period),
                "positive": round(counts.get("positive", 0) / total,2),
                "positive_count":counts.get("positive", 0),
                "neutral": round(counts.get("neutral", 0) / total,2),
                "neutral_count": counts.get("neutral", 0),
                "negative": round(counts.get("negative", 0) / total,2),
                "negative_count": counts.get("negative", 0),
                "total_reviews": total
            })

        return {
            "candles": trends
        }

    async def get_last_review_id(self):
        query = """
            SELECT MAX(id) AS last_id
            FROM reviews
        """
        row = await self.conn.fetchrow(query)
        return row["last_id"] if row else None
    async def get_all_stats(self):
        query = """
            SELECT id, date, sentiment
            FROM reviews
        """
        rows = await self.conn.fetch(query)
        sentiment_counts = defaultdict(int)
        total = 0

        for row in rows:
            sentiment = row["sentiment"]
            if sentiment:
                sentiment_counts[sentiment] += 1
                total += 1
        result = {
            "total_reviews": total,
            "positive": round(sentiment_counts.get("positive", 0) / total,2) if total else 0,
            "neutral": round(sentiment_counts.get("neutral", 0) / total,2) if total else 0,
            "negative": round(sentiment_counts.get("negative", 0) / total,2) if total else 0,
            "positive_count": sentiment_counts.get("positive", 0),
            "neutral_count": sentiment_counts.get("neutral", 0),
            "negative_count": sentiment_counts.get("negative", 0),
        }

        return result

    async def get_reviews(
            self,
            topic_name: str,
            themes: List,
            start: date = None,
            end: date = None,
            limit: int = 100,
            index: int = 0,
    ):
        conditions = []
        params = []
        if start=="" or end=="":
            start=None
            end=None
        if start and isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d").date()

        if end and isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d").date()
        if start and end:
            conditions.append("date BETWEEN $%d AND $%d" % (len(params) + 1, len(params) + 2))
            params.extend([start, end])
        if themes:
            for word in themes:
                conditions.append("text ILIKE $%d" % (len(params) + 1))
                params.append(f"%{word}%")

        query = """
            SELECT id, date, product, text, sentiment, topic_fragments, aspects
            FROM reviews
        """
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY date DESC"
        query += " OFFSET $%d LIMIT $%d" % (len(params) + 1, len(params) + 2)
        params.extend([index, limit])

        rows = await self.conn.fetch(query, *params)

        reviews = []

        for i, row in enumerate(rows, start=1):
            print(f"Row #{i}: {row}")
            topic_fragments = json.loads(row["topic_fragments"]) if row["topic_fragments"] else {}
            aspects_fragments = json.loads(row["aspects"]) if row["aspects"] else {}
            review_themes = list(topic_fragments.keys())
            positive_aspects = [v["summary"] for v in aspects_fragments.values() if v["sentiment"] == "positive"]
            negative_aspects = [v["summary"] for v in aspects_fragments.values() if v["sentiment"] == "negative"]
            if topic_name:
                if isinstance(topic_name, str):
                    topic_name_list = [topic_name]
                else:
                    topic_name_list = list(topic_name)

                if not any(name in topic_fragments for name in topic_name_list):
                    continue

            reviews.append({
                "polarity": row["sentiment"],
                "review_text": row["text"],
                "positive_aspects": positive_aspects,
                "negative_aspects": negative_aspects,
                "themes":[],
                "products": review_themes,
                "date": str(row["date"])
            })
        count_query = "SELECT COUNT(*) FROM reviews"
        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)
        total_count = await self.conn.fetchval(count_query, *params[:-2])

        return {
            "reviews": reviews,
            "metadata": {
                "total_count": total_count,
                "current_index": index,
                "has_more": index + limit < total_count
            }
        }

    async def get_reviews2(
            self,
            topic_name: str = None,
            themes: List = None,
            start: date = None,
            end: date = None,
            limit: int = 100,
            index: int = 0,
    ):
        conditions = []
        params = []

        # Преобразуем строки в даты
        if start == "" or end == "":
            start = None
            end = None
        if start and isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d").date()
        if end and isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d").date()

        # Фильтр по дате
        if start and end:
            conditions.append("date BETWEEN $%d AND $%d" % (len(params) + 1, len(params) + 2))
            params.extend([start, end])

        # Фильтр по темам (все слова должны быть в тексте)
        if themes:
            for word in themes:
                conditions.append("text ILIKE $%d" % (len(params) + 1))
                params.append(f"%{word}%")

        # Фильтр по topic_name через JSONB
        if topic_name:
            topic_name_list = [topic_name] if isinstance(topic_name, str) else list(topic_name)
            conditions.append("topic_fragments ?| ARRAY[%s]" % ",".join(f"'{t}'" for t in topic_name_list))

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        # Основной запрос
        query = f"""
            SELECT id, date, product, text, sentiment, topic_fragments, aspects
            FROM reviews
            {where_clause}
            ORDER BY date DESC
            OFFSET $%d LIMIT $%d
        """ % (len(params) + 1, len(params) + 2)

        params.extend([index, limit])

        rows = await self.conn.fetch(query, *params)

        reviews = []
        for row in rows:
            topic_fragments = json.loads(row["topic_fragments"]) if row["topic_fragments"] else {}
            aspects_fragments = json.loads(row["aspects"]) if row["aspects"] else {}

            positive_aspects = [v["summary"] for v in aspects_fragments.values() if v["sentiment"] == "positive"]
            negative_aspects = [v["summary"] for v in aspects_fragments.values() if v["sentiment"] == "negative"]

            review_themes = list(topic_fragments.keys())

            reviews.append({
                "polarity": row["sentiment"],
                "review_text": row["text"],
                "positive_aspects": positive_aspects,
                "negative_aspects": negative_aspects,
                "themes": [],
                "products": review_themes,
                "date": str(row["date"])
            })

        # total_count с учётом фильтров
        count_query = f"SELECT COUNT(*) FROM reviews {where_clause}"
        total_count = await self.conn.fetchval(count_query, *params[:-2])

        return {
            "reviews": reviews,
            "metadata": {
                "total_count": total_count,
                "current_index": index,
                "has_more": index + len(reviews) < total_count
            }
        }

    async def get_reviews_pag(
            self,
            topic_name: str = None,
            themes: List = None,
            start: date = None,
            end: date = None,
            limit: int = 100,
            index: int = 0,
    ):
        conditions = []
        params = []

        # Преобразуем строки в даты
        if start == "" or end == "":
            start = None
            end = None
        if start and isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d").date()
        if end and isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d").date()
        if start and end:
            conditions.append("date BETWEEN $%d AND $%d" % (len(params) + 1, len(params) + 2))
            params.extend([start, end])
        if themes:
            for word in themes:
                conditions.append("text ILIKE $%d" % (len(params) + 1))
                params.append(f"%{word}%")
        if topic_name:
            topic_name_list = [topic_name] if isinstance(topic_name, str) else list(topic_name)
            conditions.append("topic_fragments ?| ARRAY[%s]" % ",".join(f"'{t}'" for t in topic_name_list))

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        # Основной запрос с пагинацией
        query = f"""
            SELECT id, date, product, text, sentiment, topic_fragments, aspects
            FROM reviews
            {where_clause}
            ORDER BY date DESC
            OFFSET $%d LIMIT $%d
        """ % (len(params) + 1, len(params) + 2)
        params.extend([index, limit])

        rows = await self.conn.fetch(query, *params)

        reviews = []
        for row in rows:
            topic_fragments = json.loads(row["topic_fragments"]) if row["topic_fragments"] else {}
            aspects_fragments = json.loads(row["aspects"]) if row["aspects"] else {}

            positive_aspects = [v["summary"] for v in aspects_fragments.values() if v["sentiment"] == "positive"]
            negative_aspects = [v["summary"] for v in aspects_fragments.values() if v["sentiment"] == "negative"]

            review_themes = list(topic_fragments.keys())

            reviews.append({
                "polarity": row["sentiment"],
                "review_text": row["text"],
                "positive_aspects": positive_aspects,
                "negative_aspects": negative_aspects,
                "themes": [],
                "products": review_themes,
                "date": str(row["date"])
            })

        # total_count с учётом всех фильтров
        count_query = f"SELECT COUNT(*) FROM reviews {where_clause}"
        total_count = await self.conn.fetchval(count_query, *params[:-2])

        return {
            "reviews": reviews,
            "metadata": {
                "total_count": total_count,
                "current_index": index,
                "has_more": index + limit < total_count
            }
        }

    async def save_embedding(self, review_id: int, embedding: List[float]):
        query = """
        UPDATE reviews
        SET embedding = $2
        WHERE id = $1;
        """
        await self.conn.execute(query, review_id, embedding)

    async def get_latest_reviews(self, product: str, limit: int = 20):
        rows = await self.conn.fetch(
            "SELECT id, date, text, sentiment FROM reviews WHERE product=$1 ORDER BY date DESC LIMIT $2",
            product,
            limit,
        )
        return [dict(r) for r in rows]

    async def get_sentiment_aggregation2(self, product: str, from_date: date, to_date: date, interval: str):
        query = """
        SELECT date_trunc($4, date) as period,
               COUNT(*) FILTER (WHERE sentiment='positive')::float / COUNT(*) as positive,
               COUNT(*) FILTER (WHERE sentiment='neutral')::float / COUNT(*) as neutral,
               COUNT(*) FILTER (WHERE sentiment='negative')::float / COUNT(*) as negative,
               COUNT(*) as total_reviews
        FROM reviews
        WHERE product = $1
          AND date BETWEEN $2 AND $3
        GROUP BY period
        ORDER BY period;
        """
        rows = await self.conn.fetch(query, product, from_date, to_date, interval)
        return [dict(r) for r in rows]

    async def get_review_counts(self, product: str, from_date: date, to_date: date, interval: str):
        query = """
        SELECT date_trunc($4, date) as period,
               COUNT(*) as review_count
        FROM reviews
        WHERE product = $1
          AND date BETWEEN $2 AND $3
        GROUP BY period
        ORDER BY period;
        """
        rows = await self.conn.fetch(query, product, from_date, to_date, interval)
        return [dict(r) for r in rows]

    async def get_top_aspects(self, product: str, from_date: date, to_date: date, polarity: str, limit: int):
        query = """
        SELECT elem->>'aspect' as aspect, COUNT(*) as mentions
        FROM reviews, jsonb_array_elements(aspects) elem
        WHERE product = $1
          AND elem->>'polarity' = $2
          AND date BETWEEN $3 AND $4
        GROUP BY aspect
        ORDER BY mentions DESC
        LIMIT $5;
        """
        rows = await self.conn.fetch(query, product, polarity, from_date, to_date, limit)
        return [dict(r) for r in rows]

    async def search_by_embedding(self, embedding: List[float], product: Optional[str], from_date: Optional[date], to_date: Optional[date], limit: int, sentiment: Optional[str] = None):
        filters = []
        params = [embedding]
        idx = 2

        if product:
            filters.append(f"product = ${idx}")
            params.append(product)
            idx += 1
        if from_date and to_date:
            filters.append(f"date BETWEEN ${idx} AND ${idx+1}")
            params.extend([from_date, to_date])
            idx += 2
        if sentiment:
            filters.append(f"sentiment = ${idx}")
            params.append(sentiment)
            idx += 1

        where_clause = " AND ".join(filters) if filters else "TRUE"

        query = f"""
        SELECT id, text, date, sentiment,
               1 - (embedding <=> $1) as similarity
        FROM reviews
        WHERE {where_clause}
        ORDER BY embedding <=> $1
        LIMIT ${idx};
        """

        params.append(limit)
        rows = await self.conn.fetch(query, *params)
        return [dict(r) for r in rows]
