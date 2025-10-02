# backend
# Проект **Reviews (Gazprom)**

Этот проект предназначен для **сбора, анализа и обработки отзывов** с использованием **PostgreSQL**, **Python 3.11** и различных **NLP-моделей**.

---

## 1. Установка на Linux

### PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Запуск и автозагрузка:

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

Создание пользователя и базы данных:

```bash
sudo -u postgres psql
CREATE USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE reviews_db OWNER postgres;
\q
```

---

### Python 3.11 и виртуальное окружение

```bash
sudo apt install python3.11 python3.11-venv python3-pip
```

Создание и активация окружения:

```bash
cd /Users/kirillpogozih/Downloads/gazprom
python3.11 -m venv venv
source venv/bin/activate
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

---

## 2. Конфигурация (.env)

В корне проекта (`gazprom/.env`) создайте файл с переменными:

```env
DB_NAME=reviews_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

---

## 3. Инициализация базы данных

Примените миграции из `init.sql`:

```bash
psql -U postgres -d reviews_db -f init.sql
```

Схема таблицы:

```sql
CREATE TABLE reviews (
    id              integer PRIMARY KEY DEFAULT nextval('reviews_id_seq'::regclass),
    product         text DEFAULT 'bank',
    text            text,
    date            date,
    topics          jsonb,
    aspects         jsonb,
    id_gaz          bigint UNIQUE,
    topic_fragments jsonb,
    sentiment       text
);
```

---

## 4. Запуск проекта

Запустите основной файл:

```bash
python main.py
```

### Дополнительно
- `worker.py` — модуль фоновых задач (например, Celery/Threads).
- `routers/` — API-маршруты (`analytics_router.py`, `reviews_router.py`).
- `models/` — ML/NLP-модели (например, `model3.pth`).

---

## 5. Структура проекта

```
gazprom/
│── models/                # ML/NLP модели
│── routers/               # API роутеры
│── venv/                  # виртуальное окружение
│── alerts.py              # модуль оповещений
│── bert_summary.py        # суммаризация
│── classifier.py          # классификатор
│── db.py                  # работа с БД
│── embeddings.py          # эмбеддинги
│── init.sql               # схема базы
│── main.py                # точка входа
│── reports.py             # отчёты
│── requirements.txt       # зависимости
│── worker.py              # воркер фоновых задач
│── .env                   # переменные окружения
```
