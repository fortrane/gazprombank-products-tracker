CREATE TABLE reviews (
    id              integer PRIMARY KEY DEFAULT nextval('reviews_id_seq'::regclass),
    product         text DEFAULT 'bank',
    text            text,
    date            date,
    topics          jsonb,
    aspects         jsonb,
    embedding       vector(1536),
    id_gaz          bigint UNIQUE,
    topic_fragments jsonb,
    sentiment       text
);
