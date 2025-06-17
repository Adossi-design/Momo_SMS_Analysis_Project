"""
Flask REST API for MTN MoMo SMS transaction dashboard.

The frontend (index.html / script.js / styles.css) is served by Flask itself,
so all API calls use relative URLs — no hardcoded localhost needed.

Endpoints:
    GET /                           → dashboard (index.html)
    GET /api/transactions           → paginated transactions list
    GET /api/search?query=...       → full-text search across type, party, amount
    GET /api/summary                → aggregated totals by type and month (charts)
    GET /api/stats                  → single-row KPIs (count, volume, max, avg)

Environment variables:
    FLASK_DEBUG=true   enable debug / reloader (default: false)
    PORT=5000          listening port (default: 5000)
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory
from flask_cors import CORS

_DIR = Path(__file__).parent
DB_PATH = _DIR / "db.sqlite3"
FRONTEND_DIR = (_DIR / ".." / "frontend").resolve()

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exc: Exception = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.exception("Unhandled exception")
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Frontend static files
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_frontend(filename: str):
    return send_from_directory(FRONTEND_DIR, filename)


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.route("/api/transactions")
def get_transactions():
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(200, max(1, request.args.get("per_page", 50, type=int)))
    type_filter = request.args.get("type", "").strip()
    offset = (page - 1) * per_page

    db = get_db()

    if type_filter:
        total = db.execute(
            "SELECT COUNT(*) FROM transactions WHERE type = ?", (type_filter,)
        ).fetchone()[0]
        rows = db.execute(
            "SELECT * FROM transactions WHERE type = ? ORDER BY date DESC LIMIT ? OFFSET ?",
            (type_filter, per_page, offset),
        ).fetchall()
    else:
        total = db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        rows = db.execute(
            "SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()

    return jsonify({
        "data": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    })


@app.route("/api/search")
def search_transactions():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    pattern = f"%{query}%"
    rows = get_db().execute(
        """SELECT * FROM transactions
           WHERE type LIKE ? OR party LIKE ? OR CAST(amount AS TEXT) LIKE ?
           ORDER BY date DESC""",
        (pattern, pattern, pattern),
    ).fetchall()

    return jsonify([dict(r) for r in rows])


@app.route("/api/summary")
def get_summary():
    db = get_db()

    by_type = db.execute(
        """SELECT type, SUM(amount) AS total, COUNT(*) AS count
           FROM transactions
           GROUP BY type
           ORDER BY total DESC"""
    ).fetchall()

    by_month = db.execute(
        """SELECT substr(date, 1, 7) AS month, SUM(amount) AS total
           FROM transactions
           WHERE date IS NOT NULL
           GROUP BY month
           ORDER BY month"""
    ).fetchall()

    return jsonify({
        "type_summary":   {r["type"]:  r["total"] for r in by_type},
        "monthly_summary": {r["month"]: r["total"] for r in by_month},
        "type_counts":    {r["type"]:  r["count"] for r in by_type},
    })


@app.route("/api/stats")
def get_stats():
    row = get_db().execute(
        """SELECT COUNT(*)              AS total,
                  SUM(amount)           AS volume,
                  MAX(amount)           AS max_tx,
                  CAST(AVG(amount) AS INTEGER) AS avg_tx
           FROM transactions"""
    ).fetchone()
    return jsonify(dict(row))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug, port=port)
