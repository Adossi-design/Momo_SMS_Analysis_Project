from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM transactions").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/search', methods=['GET'])
def search_transactions():
    query = request.args.get('query', '').lower()
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM transactions").fetchall()
    conn.close()

    results = []
    for row in rows:
        r = dict(row)
        if (query in (r['type'] or '').lower() or
            query in (r['party'] or '').lower() or
            query in str(r['amount'])):
            results.append(r)

    return jsonify(results)

@app.route('/api/summary', methods=['GET'])
def get_summary():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM transactions WHERE date IS NOT NULL").fetchall()
    conn.close()

    summary_by_type = {}
    summary_by_month = {}

    for row in rows:
        r = dict(row)
        type_ = r['type']
        date = r['date'][:7]  # YYYY-MM
        amount = r['amount']

        summary_by_type[type_] = summary_by_type.get(type_, 0) + amount
        summary_by_month[date] = summary_by_month.get(date, 0) + amount

    return jsonify({
        "type_summary": summary_by_type,
        "monthly_summary": summary_by_month
    })

if __name__ == "__main__":
    app.run(debug=True)
