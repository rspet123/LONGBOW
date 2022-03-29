from Player import Player
from datetime import datetime
import requests
import json


class SystemReport:
    recent_kills = []
    # TODO integrate with zKill API
    players = []
    player_objects = []
    system_name = ""
    system_id = ""
    time = ""
    ships = {}
    id_url = "https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en"

    # TODO have the system report object build the list of player objects from the call
    # We supply it with the list of names and it should do the rest

    def __init__(self, players: list, system_name: str, system_id: str, time=datetime.now()):
        self.players = players
        self.system_name = system_name
        self.time = time
        self.system_id = system_id


    def get_player_ids(self):
        player_objects = []
        headers = {}
        headers["accept"] = "application/json"
        headers["Accept-Language"] = "en"
        headers["Content-Type"] = "application/json"
        headers["Cache-Control"] = "no-cache"

        query = str(self.players).replace("\'","\"")
        resp = requests.post(self.id_url, headers=headers, data=query)
        print(resp.text)
        char_ids = json.loads(resp.text)["characters"]
        for char_id in char_ids:
            print(char_id)
            curr_char = Player(char_id["id"],char_id["name"])
            curr_char.common_systems[self.system_id] = curr_char.common_systems.get(self.system_id,0)+1
            player_objects.append(curr_char)
