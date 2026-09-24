import sqlite3
import os

def db_config():
    if os.path.exists('./db/database.db'):
        return

    if not os.path.exists('./db/'):
        os.mkdir('./db/')

    db = sqlite3.connect('./db/database.db')
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE bots (
            bot_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            api_key TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE games (
            game_id INTEGER PRIMARY KEY,
            winner INTEGER,
            game TEXT,
            bot_1 INTEGER,
            bot_2 INTEGER,
            bot_3 INTEGER,
            bot_4 INTEGER,
            bot_5 INTEGER,
            bot_6 INTEGER,
            winner INTEGER
        )
    ''')

    db.commit()