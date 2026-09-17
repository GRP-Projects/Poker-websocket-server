import sqlite3
import secrets
import hashlib

from setup_db import db_config

db = sqlite3.connect('./db/database.db')
cursor = db.cursor()

username = "whatever"

while True:
    api_key = secrets.token_urlsafe(32).encode('utf-8')
    cursor.execute(f"SELECT * FROM bots WHERE api_key = \'{hashlib.sha256(api_key).hexdigest()}\'")
    if not cursor.fetchone():
        break

print(f"API_KEY: {api_key.decode('utf-8')}")

cursor.execute(f"INSERT INTO bots (username,api_key) VALUES(?,?)", (username, hashlib.sha256(api_key).hexdigest()))
db.commit()