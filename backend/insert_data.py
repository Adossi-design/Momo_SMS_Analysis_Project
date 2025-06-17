"""
Database population script: loads cleaned SMS data from JSON into SQLite.

Idempotent — safe to run multiple times; clears existing data before inserting.

Usage:
    python insert_data.py [json_path] [db_path]
"""
from __future__ import annotations

import json
import logging
import sqlite3
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

DB_FILE = Path(__file__).parent / "db.sqlite3"
JSON_FILE = Path(__file__).parent / "cleaned_data.json"

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    type   TEXT    NOT NULL,
    amount INTEGER,
    party  TEXT,
    tx_id  TEXT,
    date   TEXT
);
"""


def load_and_insert(db_path: Path, json_path: Path) -> int:
    if not json_path.exists():
        raise FileNotFoundError(f"{json_path} not found — run process_sms.py first")

    with json_path.open(encoding="utf-8") as fh:
        records = json.load(fh)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(SCHEMA)
        conn.execute("DELETE FROM transactions")
        conn.executemany(
            "INSERT INTO transactions (type, amount, party, tx_id, date) VALUES (?, ?, ?, ?, ?)",
            [
                (r["type"], r["amount"], r["party"], r.get("tx_id"), r.get("date"))
                for r in records
            ],
        )
        conn.commit()
        logger.info("Inserted %d records into %s", len(records), db_path)
        return len(records)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = sys.argv[1:]
    json_path = Path(args[0]) if args else JSON_FILE
    db_path = Path(args[1]) if len(args) > 1 else DB_FILE

    try:
        n = load_and_insert(db_path, json_path)
        print(f"Done: {n} transactions loaded into {db_path}")
    except (FileNotFoundError, json.JSONDecodeError, sqlite3.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
