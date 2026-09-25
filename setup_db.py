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
        )
    ''')

    cursor.execute('''
        CREATE TABLE bots_games (
            game_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            PRIMARY KEY (game_id, player_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id)
            FOREIGN KEY (player_id) REFERENCES bots(bot_id)
        )
    ''')

    db.commit()