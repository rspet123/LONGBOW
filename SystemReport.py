from Player import Player
from datetime import datetime, timezone
import requests
import json
import db


class SystemReport:
    recent_kills = []
    # TODO integrate with zKill API
    players = []
    player_ids = []
    player_objects = []
    system_name = ""
    system_id = ""
    time = ""
    ships = {}
    id_url = "https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en"

    # TODO have the system report object build the list of player objects from the call
    # We supply it with the list of names and it should do the rest

    def __init__(self, players: list, system_name: str, system_id: str, time=datetime.now(timezone.utc)):
        self.players = players
        self.system_name = system_name
        self.time = time
        self.system_id = system_id
        self.player_objects = []
        self.player_ids = []

    def get_player_ids(self):
        headers = {}
        headers["accept"] = "application/json"
        headers["Accept-Language"] = "en"
        headers["Content-Type"] = "application/json"
        headers["Cache-Control"] = "no-cache"

        query = str(self.players).replace("\'", "\"")
        resp = requests.post(self.id_url, headers=headers, data=query)
        print(resp.text)
        char_ids = json.loads(resp.text)["characters"]
        for char_id in char_ids:
            print(char_id)
            curr_char = Player(char_id["id"], char_id["name"])
            curr_char.common_systems[self.system_id] = curr_char.common_systems.get(self.system_id, 0) + 1
            self.player_objects.append(curr_char)
            self.player_ids.append(char_id["id"])

    def as_json(self):
        """Returns a json for mongodb"""
        return {
            "_id": (str(self.time) + "," + self.system_id),
            "player_ids": self.player_ids,
            "time": self.time,
            "system_name": self.system_name,
            "system_id": self.system_id
        }

    def __str__(self):
        return ("System Report at {time} in system {name}".format(time=self.time, name=self.system_name))

    def store_report(self):
        db.SystemReport.insert_one(self.as_json())
        print(self.player_objects)
        for player in self.player_objects:
            player.get_stats()
            pjson = player.as_json()
            print(pjson)
            db.Characters.update_one({"_id": pjson["_id"]}, { "$set":pjson}, upsert=True)

    def __del__(self):
        self.player_objects = []
