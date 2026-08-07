"""
db.py — single place that knows how to connect to the uniboard MySQL database.
Every route in app.py will call get_db_connection() instead of writing
connection code repeatedly.
"""

import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",       # same as your XAMPP MySQL password (empty by default)
    "database": "uniboard",
}


def get_db_connection():
    """Returns a fresh connection to the uniboard database."""
    return mysql.connector.connect(**DB_CONFIG)
