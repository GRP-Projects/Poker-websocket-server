import sqlite3
import bcrypt

from setup_db import db_config

db = sqlite3.connect('./db/database.db')
cursor = db.cursor()

username = "bingo"
password = 'dingo'.encode('utf-8')

salt = bcrypt.gensalt()
hash = bcrypt.hashpw(password, salt)

cursor.execute(f"INSERT INTO bots (username,password,salt) VALUES(?,?,?)", (username, hash, salt))
db.commit()