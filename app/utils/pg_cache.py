import os
import psycopg2
import json
from datetime import datetime

def get_pg_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )

def ensure_cache_table():
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pexels_cache (
                    id SERIAL PRIMARY KEY,
                    video_name TEXT NOT NULL,
                    theme TEXT,
                    topic TEXT,
                    aspect_ratio TEXT,
                    query TEXT,
                    response JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

def get_cached_response(video_name, theme, topic, aspect_ratio, query):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT response FROM pexels_cache
                WHERE video_name=%s AND theme=%s AND topic=%s AND aspect_ratio=%s AND query=%s
                ORDER BY created_at DESC LIMIT 1
            """, (video_name, theme, topic, aspect_ratio, query))
            row = cur.fetchone()
            return row[0] if row else None

def insert_cache(video_name, theme, topic, aspect_ratio, query, response):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pexels_cache (video_name, theme, topic, aspect_ratio, query, response)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (video_name, theme, topic, aspect_ratio, query, json.dumps(response)))
            conn.commit()
