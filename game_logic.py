from random import randint
import asyncio

class GameManager:
    def __init__(self, size: int = 6, total_games: int = 1000, starting_money: int = 250, big_blind = 10, sessions, sessions_lock):

        # Initiate starting values
        self.size = size
        self.total_games = total_games
        self.starting_money = starting_money
        self.big_blind = big_blind

        # Assign async shared memory
        self.queue = []
        self.queue_lock = asyncio.Lock()

        self.sessions = sessions
        self.sessions_lock = sessions_lock

        #self.games = {}
        #self.games_lock = asyncio.Lock()
    
    def append_queue(self, player_id)
        async with self.queue_lock:
            self.queue.append(player_id)
            if len(self.queue)>self.size:
                players = self.queue[:self.size].keys()
                for i in range(0, self.size):
                    del(queue[i])
                async with self.sessions_lock:
                    asyncio.run(Tournament(total_games, starting_money, big_blind, sessions, sessions_lock, players))
                
class Player:
    def __init__(self, player_id: int, money: int):
        self.player_id = player_id
        self.cards=[]
        self.money=money
    
    def deal(self, card):
        if not len(cards)>2:
            self.cards.append(card)

class Game:
    def __init__(self, starting_money, player_ids):
        self.player_ids = player_ids

        self.players = {player_id: Player(player_id, starting_money) for player_id in self.player_ids}
        self.available_cards = list(range(0, 52))
        self.river = []
    
    def advance_river(self):
        if len(self.river)==0:
            for i in range(0, 3): self.river.append(self._pull_card)
            return
        elif len(self.river) > 3 and len(self.river) <= 5:
            self.river.append(self._pull_card)
            return
        return
    
    def deal_to_all_players(self):
        for player in self.players:
            for i in range(0, 2): player.deal(self._pull_card)
    
    def check_hand(self, player):
        # Merge cards for player
        all_cards = sorted(self.river + player.cards)

        # Reduce cards to only number
        all_cards_flat = []
        for i in range(0, len(all_cards)):
            all_cards_flat[i] = all_cards[i]%13
        
        # Reduce cards to only suit
        all_cards_suit = []
        for i in range(0, len(all_cards)):
            all_cards_flat[i] = all_cards[i] // 13

        value = (0, 0)

    def _pull_card(self):
        card = randint(0, len(available_cards)-1)
        del(available_cards[card])
        return card

async def Tournament(total_games: int, starting_money: int, big_blind: int, sessions, sessions_lock, player_ids):
    small_blind = big_blind // 2
    while total_games > 1:
        game = Game(starting_money = starting_money, player_ids)
        game.deal_to_all_players()
        total_games-=1