import os
import psycopg2

# Read connection info from environment variables
db = os.getenv("POSTGRES_DB", "postgres-ttv")
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "postgres")
host = os.getenv("POSTGRES_HOST", "postgres-ttv")  # updated default to match your new host name
port = os.getenv("POSTGRES_PORT", "4432")

try:
    conn = psycopg2.connect(
        dbname=db,
        user=user,
        password=password,
        host=host,
        port=port
    )
    print("Connected to Postgres successfully!")
    conn.close()
except Exception as e:
    print("Failed to connect to Postgres:", e)
