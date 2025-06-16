import sqlite3
import json
import os

DB_FILE = "db.sqlite3"
JSON_FILE = "cleaned_data.json"

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        amount INTEGER,
        party TEXT,
        tx_id TEXT,
        date TEXT
    );
    """
    conn.execute(sql)
    conn.commit()

def insert_transaction(conn, txn):
    sql = """
    INSERT INTO transactions (type, amount, party, tx_id, date)
    VALUES (?, ?, ?, ?, ?);
    """
    data = (txn['type'], txn['amount'], txn['party'], txn['tx_id'], txn['date'])
    conn.execute(sql, data)

def load_data(conn, json_file):
    with open(json_file, 'r') as f:
        transactions = json.load(f)
        for txn in transactions:
            insert_transaction(conn, txn)
        conn.commit()

def main():
    if not os.path.exists(JSON_FILE):
        print(f"{JSON_FILE} not found. Please run process_sms.py first.")
        return

    conn = create_connection(DB_FILE)
    create_table(conn)
    load_data(conn, JSON_FILE)
    conn.close()
    print("Database created and populated successfully.")

if __name__ == "__main__":
    main()
