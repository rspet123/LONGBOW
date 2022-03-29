from Player import Player
from datetime import datetime
import requests
class systemreport:
    recent_kills = []
    # TODO integrate with zKill API
    players = {}
    system_name = ""
    system_id = ""
    time = ""
    ships = {}
    # TODO have the system report object build the list of player objects from the call
    # We supply it with the list of names and it should do the rest

    def __init__(self, players: list,system_name: str,system_id:str, time = datetime.now()):
        self.players = players
        self.system_name = system_name
        self.time = time
        self.system_id = system_id
        self.time = time


    def __init__(self, players: list,system_name: str, ships: dict,system_id:str, time = datetime.now()):
        self.players = players
        self.system_name = system_name
        self.time = time
        self.ships = ships
        self.system_id = system_id
        self.time = time



