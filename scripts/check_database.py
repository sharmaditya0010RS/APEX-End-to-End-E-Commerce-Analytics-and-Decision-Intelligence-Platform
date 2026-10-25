import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / ".env")

with psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_schema(), version()")
        result = cursor.fetchone()
        print(f"Database: {result[0]}")
        print(f"Schema: {result[1]}")
        print(f"Connection: PASS")
