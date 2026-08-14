import sqlite3
import bcrypt
import json
import asyncio

from os.path import exists
from setup_db import db_config
from websockets.asyncio.server import serve

from game_logic import GameManager

class Session:
    def __init__(self, socket, username: str, current_game: int):
        self.socket = socket
        self.username = username
        self.current_game = current_game

db_config()

# Set up global session dictionary
sessions = {}
sessions_lock = asyncio.Lock()

# Set up Game Manager
manager = GameManager(sessions = sessions, sessions_lock = sessions_lock)

# Setup and connect to DB
db = sqlite3.connect('./db/database.db')
cursor = db.cursor()

#async def game():

async def handle_request_receive(websocket):
    user = 0

    try:
        while True:
            async for message in websocket:
                message = json.loads(message)

                if message['type'] == 'login':
                    # Handle logins
                    cursor.execute(f"SELECT * FROM bots WHERE username = \'{message['username']}\'")
                    entry = cursor.fetchone()

                    if entry[0] in sessions.keys():
                        await websocket.send(json.dumps({'success': False, 'info': 'Already signed in somewhere else'}))
                        continue

                    if not entry:
                        await websocket.send(json.dumps({'success': False, 'info': 'No such bot'}))
                        continue

                    password = message['password'].encode('utf-8')

                    if entry[2] == bcrypt.hashpw(password, entry[3]):
                        user = entry[0]
                        async with sessions_lock:
                            sessions[entry[0]] = Session(socket = websocket, username = message['username'], current_game=-1)
                        await websocket.send(json.dumps({'success': True, 'info' : 'Successful sign-in'}))
                        continue
                    await websocket.send(json.dumps({'success': False, 'info': 'Wrong password'}))
                    continue
                elif user == 0:
                    await websocket.send(json.dumps({'info': 'You are not signed in'}))
                    continue
                
                # Switch case for diffusing validated request types
                match message['type']:
                    case 'enter_matchmaking':
                        async with manager.queue_lock:
                            if user in manager.queue.keys():
                                await websocket.send(json.dumps({'success': False, 'info': 'Already in queue'}))
                                continue
                            manager.queue.append(user)
                        await websocket.send(json.dumps({'success': True, 'info': 'Joined queue'}))
                        continue
    finally:
        async with sessions_lock:
            del sessions[user]

async def main():
    server = await serve(handle_request_receive, "", 8801)
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())