"""
init_aiven_schema.py — runs schema_mysql.sql against your Aiven MySQL instance.

Uses mysql-connector-python instead of the command-line mysql client,
because older bundled clients (like XAMPP's) don't support the newer
caching_sha2_password auth plugin or --ssl-mode flag that Aiven requires.

Run this ONCE, after your .env is filled in with real Aiven credentials.
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Connect WITHOUT specifying a database yet — the database doesn't exist
# until schema_mysql.sql creates it via "CREATE DATABASE IF NOT EXISTS uniboard"
config = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ["DB_PORT"]),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}

ca_cert_path = os.environ.get("DB_SSL_CA")
if ca_cert_path:
    config["ssl_ca"] = ca_cert_path
    config["ssl_verify_cert"] = True

print(f"Connecting to {config['host']}:{config['port']} ...")
conn = mysql.connector.connect(**config)
cur = conn.cursor()

with open("schema_mysql.sql", "r") as f:
    sql_script = f.read()

# multi=True lets us run a file containing several semicolon-separated statements
for result in cur.execute(sql_script, multi=True):
    if result.with_rows:
        result.fetchall()

conn.commit()
cur.close()
conn.close()

print("Schema created successfully on Aiven. The 'uniboard' database and its 4 tables now exist.")
print("Next: run 'python seed_data_mysql.py' to populate it with data.")
