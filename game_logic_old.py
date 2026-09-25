import random
from phevaluator.evaluator import evaluate_cards

import asyncio

class Game:
    def __init__(self, game_id: int, starting_money: int, players: list, big_blind: int, small_blind: int):
        self.id = game_id

        self.starting_money = starting_money
        self.big_blind = big_blind
        self.small_blind = small_blind

        random.shuffle(players)

        self.available_cards = list(range(0, 52))
        self.cards = []
        self.river = []
        self.pot = 0
        self.current_bet = 0

        self.players = [Player(i, starting_money, self.river) for i in players]
        self.turn = 0 # Int between 0 and len(self.players), indicates who's turn it is
    
    def advance_turn(self):
        for player in self.players:
            if player.bet != self.current_bet and player.money > 0 and not player.folded:
                while True:
                    self.turn = (self.turn + 1) % len(self.players)
                    if not self.get_current_player.folded:
                        break
                return
        if len(self.river) < 5:
            self.advance_river()
            self.turn = 0
            return
        self.end_round()
    
    def advance_river(self):
        if len(self.river) == 0:
            for i in range(0, 3): self.river.append(self._pull_card())
        elif len(self.river) > 3 and len(self.river) <= 5:
            self.river.append(self._pull_card())
        return
    
    def deal_to_all_players(self):
        for player in self.players:
            for i in range(0, 2): player.deal(self._pull_card())
    
    def _pull_card(self):
        card = random.randint(0, len(self.available_cards)-1)
        del(self.available_cards[card])
        return card
    
    def _evaluate_player_ratings(self):
        if len(player.cards + self.river) in range(5, 8):
            ratings = {}
            for player in self.players:
                hand = player.cards + self.river
                value = evaluate_cards(*hand)
                ratings[value] = player
            return ratings
        raise Exception("Must have between 5 and 7 total cards in play to evaluate current rankings.")
    
    def end_round(self):
        # TODO: Add side-pot logic.

        ratings = _evaluate_player_ratings()
        rankings = rankings.keys().sort()
        split = rankings.count(rankings[0])
        share = self.pot/split

        for i in range(0, split):
            # TODO: Add arbitrary "odd chip" split logic.
            ratings[rankings[i]].money += share
        
        # Reset game
        self.pot = 0
        self.available_cards = list(range(0, 52))
        self.river = []
        self.turn = 0

        for player in self.players:
            player.bet = 0
        
        print("Round ended")
        input()
    
    def get_current_player(self):
        return self.players[self.turn].player_id
    
    def get_player_from_id(self, search_id: int):
        for p in self.players:
            if p.player_id == search_id:
                return p
        return None
    
    def fold(self):
        player = self.players[self.turn]
        player.fold()

        return True

    def call(self):
        player = self.players[self.turn]
        diff = self.current_bet - player.bet

        if player.money < diff:
            return False

        player.bet += diff
        player.money -= diff
        self.pot += diff

        return True

    def raise_bet(self, raise_quantity: int):
        player = self.players[self.turn]
        diff = (self.current_bet - player.bet) + raise_quantity

        if player.money < diff:
            return False

        player.bet += diff
        player.money -= diff
        self.pot += diff

        self.current_bet = player.bet

        return True
    
class Player:
    def __init__(self, player_id: int, money: int, river: list):
        self.player_id = player_id
        self.cards = []
        self.folded = False
        self.bet = 0 # amount already bet
        self.money = money # current money (doesn't include that which is in pot)
        self.river = river # reference to river object
    
    def deal(self, card):
        if not len(cards)>2:
            self.cards.append(card)
    
    def get_player_status(self):
        return (self.cards, self.bet, self.money, self.folded, self.river)
    
    def fold(self):
        self.folded=True