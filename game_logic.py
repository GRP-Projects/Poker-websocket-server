class Game:
    def __init__(self, game_id: int, starting_money: int, players: list):
        self.id = game_id
        self.starting_money = starting_money
        self.players = []