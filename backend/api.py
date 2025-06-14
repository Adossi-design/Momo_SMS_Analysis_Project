from flask import Flask, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

DB_PATH = 'sms.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/transactions', methods=['GET'])
def get_all_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, body, category, amount, date FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(debug=True)
