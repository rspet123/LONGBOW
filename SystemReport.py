from Player import Player
from datetime import datetime
import requests
class systemreport:
    recent_kills = []
    # TODO integrate with zKill API
    players = {}
    system_name = {}
    system_id = {}
    time = ""
    ships = {}

    def __init__(self, players: dict,system_name: str, ships: dict,system_id:str, time = datetime.now()):
        self.players = players
        self.system_name = system_name
        self.time = time
        self.ships = ships
        self.system_id = system_id

