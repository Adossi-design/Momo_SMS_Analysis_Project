import json
import sqlite3
import re

# File paths
json_file_path = "backend/categorized_sms.json"
db_file_path = "backend/sms.db"

# Regex to extract date and amount
date_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
amount_pattern = re.compile(r'(?i)(?:(UGX|F CFA|₦)?\s?)([\d,]+\.\d{2}|\d{1,3}(?:,\d{3})*(?:\.\d{2})?)')

# Load the categorized SMS messages
with open(json_file_path, "r", encoding="utf-8") as f:
    sms_data = json.load(f)

print(f"Loaded {len(sms_data)} records from {json_file_path}")

# Connect to the SQLite database
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Create or recreate the 'transactions' table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        amount REAL,
        type TEXT,
        category TEXT
    )
""")

# Optional: Clear the table before inserting fresh data
cursor.execute("DELETE FROM transactions")

inserted = 0
skipped = 0

# Parse each SMS and insert
for record in sms_data:
    body = record.get("body", "")
    category = record.get("category", "Uncategorized")

    # Extract date
    date_match = date_pattern.search(body)
    date = date_match.group() if date_match else None

    # Extract amount
    amount_match = amount_pattern.search(body)
    try:
        amount = float(amount_match.group(2).replace(",", "")) if amount_match else None
    except:
        amount = None

    # Infer type (credit or debit)
    body_lower = body.lower()
    if "received" in body_lower or "deposit" in body_lower:
        txn_type = "credit"
    elif "sent" in body_lower or "paid" in body_lower or "withdraw" in body_lower:
        txn_type = "debit"
    else:
        txn_type = "unknown"

    # Only insert if date and amount are valid
    if date and amount is not None:
        cursor.execute("""
            INSERT INTO transactions (date, amount, type, category)
            VALUES (?, ?, ?, ?)
        """, (date, amount, txn_type, category))
        inserted += 1
    else:
        skipped += 1

# Commit and close
conn.commit()
conn.close()

print(f"Inserted: {inserted} records into 'transactions'")
print(f"Skipped: {skipped} records due to missing date or amount")
