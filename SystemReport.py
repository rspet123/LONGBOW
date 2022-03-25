from Player import player
from datetime import datetime
class systemreport:
    players = {}
    system_name = {}
    time = ""
    ships = {}

    def __init__(self, players: dict,system_name: str, ships: dict, time = datetime.now()):
        self.players = players
        self.system_name = system_name
        self.time = time
        self.ships = ships
