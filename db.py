"""
Petrol Buddy – Database Helper
Uses mysql-connector-python with a simple per-request connection pattern.
All queries use parameterized statements to prevent SQL injection.
"""

import mysql.connector
from flask import current_app, g


def get_db():
    """Return a MySQL connection stored in Flask's request context (g)."""
    if "db" not in g:
        try:
            g.db = mysql.connector.connect(
                host     = current_app.config["DB_HOST"],
                port     = current_app.config["DB_PORT"],
                user     = current_app.config["DB_USER"],
                password = current_app.config["DB_PASSWORD"],
                database = current_app.config["DB_NAME"],
                charset  = "utf8mb4",
                autocommit = False,
            )
        except mysql.connector.Error as err:
            g.db_error = str(err)
            return None
    return g.db


def close_db(e=None):
    """Close DB connection at end of request."""
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()


def query(sql, params=(), one=False, commit=False):
    """
    Execute a SQL statement.
    - Returns a list of dicts (or a single dict when one=True).
    - Set commit=True for INSERT / UPDATE / DELETE.
    - Returns lastrowid when commit=True.
    """
    db = get_db()
    if db is None:
        err = getattr(g, "db_error", "Could not reach MySQL")
        raise RuntimeError(f"Database connection failed: {err}\n\n👉 Ensure MySQL is running (Start MySQL in XAMPP or Windows Services) and run 'python setup_db.py' to initialize tables.")

    cur = db.cursor(dictionary=True)
    cur.execute(sql, params)

    if commit:
        db.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id

    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def transaction(statements):
    """
    Execute a list of (sql, params) tuples as a single atomic transaction.
    Returns list of lastrowids.
    Rolls back on any error.
    """
    db = get_db()
    if db is None:
        raise RuntimeError("Database connection failed.")

    ids = []
    try:
        cur = db.cursor(dictionary=True)
        for sql, params in statements:
            cur.execute(sql, params)
            ids.append(cur.lastrowid)
        db.commit()
        cur.close()
        return ids
    except Exception:
        db.rollback()
        raise
