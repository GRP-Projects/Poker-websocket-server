import random
from phevaluator.evaluator import evaluate_cards

from math import inf
from pokerkit import Automation, Mode, NoLimitTexasHoldem

import asyncio

class Game:
    def __init__(self, game_id: int, starting_money: int, players: list, big_blind: int, small_blind: int):
        self.id = game_id

        self.starting_money = starting_money
        self.big_blind = big_blind
        self.small_blind = small_blind
        self.pot = 0

        random.shuffle(players)
        self.players = [Player(i, starting_money) for i in players]
        self.players_id_persistent = players
        self.state = self._new_round()

        self._sync_players()
    
    def _new_round(self):
        state = NoLimitTexasHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.CARD_BURNING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
                Automation.RUNOUT_COUNT_SELECTION,
                Automation.BOARD_DEALING,
            ),
            True,
            0,
            (self.small_blind, self.big_blind),
            self.big_blind,
            self._generate_stacks(),
            len(self.players),
            mode=Mode.CASH_GAME,
        )
        
        while state.can_deal_hole():
            state.deal_hole()

        return state
    
    def _generate_stacks(self):
        stack = []
        for player in self.players:
            stack.append(player.money)
        return stack
    
    def _sync_players(self):
        for i in range(0, len(self.players)):
            # Personal stats
            self.players[i].folded = not self.state.statuses[i]
            self.players[i].money = self.state.stacks[i]
            self.players[i].cards = [f"{card.rank}{card.suit}" for card in self.state.hole_cards[i]]

            # Global stats
            self.players[i].river = [card for card in self.state.board_cards]
            self.players[i].current_bet = self.state.checking_or_calling_amount
            #self.players[i].minimum_bet = self.state.min_completion_betting_or_raising_to_amount - (self.state.checking_or_calling_amount + self.state.bets[i])
            print(f"{self.state.min_completion_betting_or_raising_to_amount} - ({self.state.checking_or_calling_amount} + {self.state.bets[i]})")
    
    def fold(self):
        player = self.players[self.state.actor_index]
        player_seat = self.state.actor_index
        
        if self.state.can_fold():

            self.state.fold()

            self._sync_players()
            return True
        return False

    def call(self):
        player = self.players[self.state.actor_index]
        player_seat = self.state.actor_index

        if self.state.can_check_or_call():

            self.state.check_or_call()

            # Sync the state
            self.pot = self.state.total_pot_amount
            
            self._sync_players()
            return True
        print("Failed to check or call?")
        input()
        return False

    def raise_bet(self, quantity: int):
        player = self.players[self.state.actor_index]
        player_seat = self.state.actor_index
        
        if self.state.can_complete_bet_or_raise_to(quantity + self.state.checking_or_calling_amount + self.state.bets[player_seat]):

            self.state.complete_bet_or_raise_to(quantity + self.state.checking_or_calling_amount + self.state.bets[player_seat])

            # Sync the state
            self.pot = self.state.total_pot_amount

            self._sync_players()
            return True
        return False

    def get_current_player(self):
        if not self.state.actor_index is None:
            return self.players[self.state.actor_index].player_id
    
    def get_player_ids(self):
        participants = []
        for p in self.players:
            participants.append(p.player_id)
        return participants
    
    def get_player_from_id(self, search_id: int):
        for p in self.players:
            if p.player_id == search_id:
                return p
        return None
    
    def get_player_seat_from_id(self, search_id: int):
        for p in range(0, len(self.players)):
            if self.players[p].player_id == search_id:
                return p
        return None
    
    def end_round(self):
        eliminated_players = []
        winner = None

        self._sync_players()
        for player in self.players:
            if player.money <= 0:
                eliminated_players.append(player.player_id)
                self.players.remove(player)
        if len(self.players) == 1:
            winner = self.players[0].player_id
        else:
            self.state = self._new_round()
            self._sync_players()

        return eliminated_players, winner
    
    def eliminate_and_distribute(self, player_id):
        player = self.get_player_from_id(player_id)
        if player:
            for i in self.players:
                i.money += player.money / len(self.players)
            self.players.remove(player)
        
class Player:
    def __init__(self, player_id: int, money: int):
        self.player_id = player_id

        self.raised = 0
        self.cards = []
        self.river = []
        self.folded = False
        self.money = money # current money (doesn't include that which is in pot)
        self.current_bet = 0
        self.minimum_bet = 0
    
    def deal(self, card):
        if not len(cards)>2:
            self.cards.append(card)
    
    def get_player_status(self):
        value = 7463
        if len(self.cards + self.river) >= 5:
            self.river = [f"{card[0].rank}{card[0].suit}" for card in self.river]
            value = evaluate_cards(*(self.cards + self.river))
        return (self.cards, self.current_bet, self.money, self.folded, self.river, value, self.minimum_bet)
    
    def fold(self):
        self.folded=True