import aiosqlite
import hashlib
import json
import asyncio

from os.path import exists
from setup_db import db_config
from websockets.asyncio.server import serve

from game_logic import Game

import logging

logger = logging.getLogger(__name__)

game_size = 2
starting_money = 500

class Session:
    def __init__(self, socket, bot_id: bot_id, current_game: int):
        self.socket = socket
        self.bot_id = bot_id
        self.current_game = current_game

db_config()

# Set up global session dictionary
sessions = {}

# Set up games list
games = {}

# Set up queue
queue = []

# Broadcasts given string to all sockets list
async def broadcast_to_all(participants, message):
    try:
        participants = [sessions[i] for i in participants]
        for user in participants:
            await user.socket.send(message)
    except Exception as e:
        logger.error("Could not distribute message to all participants.")

def generate_game_id():
    for i in range(0, len(games.keys())):
        if not i in games.keys():
            return i
    return len(games)

async def handle_request_receive(websocket, db):
    user = 0

    try:
        async for message in websocket:
            message = json.loads(message)

            if message['type'] == 'login':
                # Handle logins
                api_key = hashlib.sha256(message['api_key'].encode('utf-8')).hexdigest()

                entry = None
                async with db.execute(f"SELECT * FROM bots WHERE api_key = \'{api_key}\'") as cursor:
                    entry = await cursor.fetchone()

                if entry[0] in sessions.keys():
                    await websocket.send(json.dumps({'success': False, 'status': 0, 'info': 'Already signed in somewhere else'}))
                    continue

                if not entry:
                    await websocket.send(json.dumps({'success': False, 'status': 0, 'info': 'Incorrect API key'}))
                    continue
                
                # Perform user sign-in by attributing ownership of current
                # process and imputing into persistent sessions list.
                
                user = entry[0]
                sessions[user] = Session(socket = websocket, bot_id = user, current_game=-1)
                await websocket.send(json.dumps({'success': True, 'status': 1, 'info' : f'API Key accepted, welcome {entry[1]}'}))
                continue

            elif user == 0:
                await websocket.send(json.dumps({'success': False, 'status': 0, 'info': 'You are not signed in'}))
                continue
            
            # Switch case for diffusing validated request types
            match message['type']:
                case 'enter_matchmaking':
                    
                    # Adds bot to queue if bot isn't already in queue
                    if user in queue:
                        await websocket.send(json.dumps({'success': False, 'status': 2, 'info': 'Already in queue'}))
                        continue
                    queue.append(user)
                    await websocket.send(json.dumps({'success': True, 'status': 2, 'info': 'Joined queue'}))

                    # Creates new game if queue size > given game size
                    if len(queue) >= game_size:
                        players = [queue[i] for i in range(0, game_size)]
                        game_id = generate_game_id()
                        for i in players:
                            sessions[i].current_game = game_id
                            del queue[queue.index(i)]
                        games[game_id] = Game(game_id, starting_money, players)
                        await broadcast_to_all(players, json.dumps({'success': True, 'status': 3, 'info': f'In game {game_id}'}))
                    continue
    finally:
        # If condition here for being currently in-game
        del sessions[user]
        if user in queue:
            del queue[queue.index(user)]

async def main():
    # Setup and connect to DB
    db = await aiosqlite.connect('./db/database.db')

    server = await serve(lambda ws: handle_request_receive(ws, db), "", 8801)
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())