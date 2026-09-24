import aiosqlite
import hashlib
import json
import asyncio

from os.path import exists
from setup_db import db_config
from websockets.asyncio.server import serve

from game_logic import Game

import logging
from configparser import ConfigParser

logger = logging.getLogger(__name__)

# Config
try:
    parser = ConfigParser()
    parser.read('config.ini')

    game_size = parser.getint('gamedetails', 'players')
    starting_money = parser.getint('gamedetails', 'starting_money')
    big_blind = parser.getint('gamedetails', 'big_blind')
    small_blind = parser.getint('gamedetails', 'small_blind')
    max_fouls = parser.getint('gamedetails', 'max_fouls')
except Exception as e:
    logger.error("Could not parse config.ini file")

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

async def broadcast_player_turn(user: int, game: Game):
    player = game.get_player_from_id(user)
    status = player.get_player_status()

    send_dict = {
        'type' : 'game',
        'success' : True,
        'status' : 4,
        'cards' : status[0],
        'bet' : status[1],
        'money' : status[2],
        'folded' : status[3],
        'river' : status[4]
    }

    if player:
        await sessions[user].socket.send(json.dumps(send_dict))
        return True
    return False

def generate_game_id():
    for i in range(0, len(games.keys())):
        if not i in games.keys():
            return i
    return len(games)

async def handle_request_receive(websocket, db):
    user = 0
    accumulated_fouls = 0

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

            # Check if user is logged in
            elif user == 0:
                await websocket.send(json.dumps({'success': False, 'status': 0, 'info': 'You are not signed in'}))
                continue
            
            # Switch case for diffusing validated request types
            elif message['type'] == 'enter_matchmaking':
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
                    
                    new_game = Game(game_id, starting_money, players, big_blind, small_blind)
                    games[game_id] = new_game

                    await broadcast_to_all(players, json.dumps({'success': True, 'status': 3, 'info': f'In game {game_id}'}))
                    await broadcast_player_turn(new_game.get_current_player(), new_game)
                continue
            
            # Process play made by bot
            elif message['type'] == 'play':
                # Assuming user is logged in (above check), check if user is in game. If not, give appropriate error
                # according to whether user is queued.

                # Has responsibility for initating next player turn as well as executing current player's move.

                if sessions[user].current_game == -1 and (user not in queue):
                    await websocket.send(json.dumps({'success': False, 'status': 1, 'info': 'You are not currently in a game'}))
                    continue
                elif sessions[user].current_game == -1:
                    await websocket.send(json.dumps({'success': False, 'status': 2, 'info': 'You are not currently in a game'}))
                    continue
                
                game = games[sessions[user].current_game]

                if game.get_current_player() != user:
                    await websocket.send(json.dumps({'success': False, 'status': 3, 'info': 'It\'s not your turn'}))
                    continue
                
                player = game.get_player_from_id(user)
                
                legitimate = False
                # play : fold = 0, call = 1, raise = 2.
                print(f"Play by: {user}")
                match message['play']:
                    case 0:
                        legitimate = game.fold()
                    case 1:
                        legitimate = game.call()
                    case 2:
                        legitimate = game.raise_bet(message['raise_quantity'])
                
                # If played 3 illigitimate moves, fold.
                if not legitimate:
                    accumulated_fouls+=1
                    await broadcast_player_turn(user, game)
                    if accumulated_fouls >= max_fouls:
                        game.fold()
                        accumulated_fouls = 0
                    else:
                        continue
                
                print(game.turn)
                input()
                game.advance_turn()
                print(game.turn)
                input()
                await broadcast_player_turn(game.get_current_player(), game)


    #except Exception as e:
    #    logger.error(f"An error occured in handling user request. {e}")
    finally:
        # If condition here for being currently in-game - if so, TODO: abort entire game.
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