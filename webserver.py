from flask import Flask, request, render_template, session, redirect, url_for, g
from markupsafe import Markup

import sqlite3
import secrets
import hashlib

from configparser import ConfigParser
import logging

import sys

app = Flask(__name__)

logger = logging.getLogger(__name__)

try:
    parser = ConfigParser()
    parser.read('config.ini')
    password = parser.get('admin', 'password')
    app.secret_key = parser.get('admin', 'secret_key')
except Exception as e:
    logger.error(f"Could not parse config file. {e}")
    sys.exit()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("./db/database.db", timeout=10)
    return g.db

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'admin' not in session:
        session['admin'] = False
    if session['admin']:
        return redirect(url_for('database_page'))
    if request.method=='POST':
        if password == request.form['password']:
            session['admin'] = True
            return redirect(url_for('database_page'))
        else:
            return render_template("login.html", message = "Incorrect password, try again.")
    return render_template("login.html") 

@app.route('/db', methods=['GET', 'POST'])
def database_page():
    if session['admin']:
        if request.method=='POST':
            new_bot_name = request.form['bot_name']

            db = get_db()
            
            try:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM bots WHERE username = ?", (new_bot_name,))

                # Check to see if bot already exists
                if cursor.fetchone():
                    return render_template("database.html", message = "ERROR: Bot by that name already exists.")
                
                # Generate unique API key
                while True:
                    api_key = secrets.token_urlsafe(32).encode('utf-8')
                    cursor.execute(f"SELECT * FROM bots WHERE api_key = \'{hashlib.sha256(api_key).hexdigest()}\'")
                    if not cursor.fetchone():
                        break

                cursor.execute(f"INSERT INTO bots (username,api_key) VALUES(?,?)", (new_bot_name, hashlib.sha256(api_key).hexdigest()))
                db.commit()
                db.close()
                return render_template("database.html", message = Markup(f"Bot created. API KEY = {api_key.decode('utf-8')}<br>DO NOT LOSE THIS."))
            except Exception as e:
                return render_template("database.html", message = "An error has occured.")
            finally:
                db.close()
        return render_template("database.html")
    else:
        return "404 resource not found"

if __name__ == '__main__':
    app.run()