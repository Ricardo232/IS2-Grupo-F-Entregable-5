import playerstate

class Warrior(playerstate.Player):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
