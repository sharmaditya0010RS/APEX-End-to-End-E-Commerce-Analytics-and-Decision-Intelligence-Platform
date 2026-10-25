from pathlib import Path
import os

import pandas as pd
import psycopg
from psycopg import sql
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[2]
load_dotenv(root / ".env")

profile = pd.read_csv(root / "reports" / "quality" / "table_profile.csv")
results = []

with psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"]
) as connection:
    with connection.cursor() as cursor:
        for row in profile.itertuples(index=False):
            actual = cursor.execute(
                sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                    sql.Identifier("raw"),
                    sql.Identifier(row.table)
                )
            ).fetchone()[0]

            results.append({
                "table": row.table,
                "expected": int(row.rows),
                "actual": actual,
                "status": "PASS" if actual == row.rows else "FAIL"
            })

result = pd.DataFrame(results)

print(result.to_string(index=False))

if len(result) != 9 or result["status"].ne("PASS").any():
    raise RuntimeError("Source-to-raw reconciliation failed")

if result["actual"].sum() != 1550922:
    raise RuntimeError("Unexpected aggregate row count")

print("ALL NINE SOURCE TABLES RECONCILED")
