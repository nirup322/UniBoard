"""
db.py — single place that knows how to connect to the uniboard MySQL database.
Every route in app.py will call get_db_connection() instead of writing
connection code repeatedly.

Credentials come from environment variables (never hardcoded), loaded from
a local .env file during development, or set directly in Render's dashboard
in production.
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # reads .env file into environment variables, if present

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "uniboard"),
}

ca_cert_path = os.environ.get("DB_SSL_CA")
if ca_cert_path:
    DB_CONFIG["ssl_ca"] = ca_cert_path
    DB_CONFIG["ssl_verify_cert"] = True


def get_db_connection():
    """Returns a fresh connection to the uniboard database."""
    return mysql.connector.connect(**DB_CONFIG)