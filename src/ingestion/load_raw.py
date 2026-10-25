from pathlib import Path
import csv
import hashlib
import os

import psycopg
from psycopg import sql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

load_dotenv(ROOT / ".env")

files = [
    name.strip()
    for name in (ROOT / "config" / "expected_sources.txt").read_text(encoding="utf-8-sig").splitlines()
    if name.strip()
]

connection_args = {
    "host": "127.0.0.1",
    "port": 5433,
    "dbname": os.environ["POSTGRES_DB"],
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASSWORD"]
}

def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def inspect_source(path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        columns = next(reader)
        count = sum(1 for _ in reader)

    if not columns or len(columns) != len(set(columns)):
        raise ValueError(f"Invalid source columns: {path.name}")

    return columns, count

with psycopg.connect(**connection_args) as connection:
    for filename in files:
        path = RAW / filename
        name = path.stem
        columns, expected_rows = inspect_source(path)
        digest = file_sha256(path)

        with connection.transaction():
            with connection.cursor() as cursor:
                existing = cursor.execute(
                    "SELECT source_sha256, loaded_rows FROM audit.source_loads WHERE source_file = %s",
                    (filename,)
                ).fetchone()

                table_exists = cursor.execute(
                    "SELECT to_regclass(%s)",
                    (f"raw.{name}",)
                ).fetchone()[0]

                if existing and table_exists and existing[0] == digest:
                    actual = cursor.execute(
                        sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                            sql.Identifier("raw"),
                            sql.Identifier(name)
                        )
                    ).fetchone()[0]

                    if actual == expected_rows == existing[1]:
                        print(f"SKIP {name}: {actual:,} rows unchanged")
                        continue

                definition = sql.SQL(", ").join(
                    sql.SQL("{} TEXT").format(sql.Identifier(column))
                    for column in columns
                )

                cursor.execute(
                    sql.SQL("DROP TABLE IF EXISTS {}.{}").format(
                        sql.Identifier("raw"),
                        sql.Identifier(name)
                    )
                )

                cursor.execute(
                    sql.SQL("CREATE TABLE {}.{} ({})").format(
                        sql.Identifier("raw"),
                        sql.Identifier(name),
                        definition
                    )
                )

                statement = sql.SQL("COPY {}.{} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)").format(
                    sql.Identifier("raw"),
                    sql.Identifier(name)
                )

                with path.open("r", encoding="utf-8-sig", newline="") as source:
                    with cursor.copy(statement) as copy:
                        while block := source.read(1024 * 1024):
                            copy.write(block)

                actual = cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                        sql.Identifier("raw"),
                        sql.Identifier(name)
                    )
                ).fetchone()[0]

                if actual != expected_rows:
                    raise RuntimeError(
                        f"Row reconciliation failed for {name}: {expected_rows} versus {actual}"
                    )

                cursor.execute(
                    """
                    INSERT INTO audit.source_loads
                    (source_file, source_sha256, expected_rows, loaded_rows)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (source_file)
                    DO UPDATE SET
                        source_sha256 = EXCLUDED.source_sha256,
                        expected_rows = EXCLUDED.expected_rows,
                        loaded_rows = EXCLUDED.loaded_rows,
                        loaded_at = NOW()
                    """,
                    (filename, digest, expected_rows, actual)
                )

                print(f"LOADED {name}: {actual:,} rows")

print("RAW INGESTION COMPLETED")
