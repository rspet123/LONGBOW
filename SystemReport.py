from Player import Player
from System import System
from datetime import datetime, timezone
from eve_data_tools import get_system_data_by_name
import requests
import json
import db

name_data = get_system_data_by_name()

class SystemReport:
    recent_kills = []
    # TODO integrate with zKill API
    players = []
    player_ids = []
    # MAKE EACH PLAYER ID A DICT like {"name":x,"id":y}
    # SO THAT WE CAN DISPLAY PICTURES BY EACH CHARACTER
    player_objects = []
    system_name = ""
    system_id = ""
    time = ""
    ships = {}
    id_url = "https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en"


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
        # TODO fix above, it's messed up
        resp = requests.post(self.id_url, headers=headers, data=query)
        print(resp.text)
        char_ids = json.loads(resp.text)["characters"]
        for char_id in char_ids:
            print(char_id)
            curr_char = Player(char_id["id"],
                               char_id["name"],
                               self.system_name,
                               self.time,
                               (str(self.time) + "," + self.system_id))
            curr_char.common_systems[self.system_id] = curr_char.common_systems.get(self.system_id, 0) + 1
            self.player_objects.append(curr_char)
            self.player_ids.append(char_id["name"])

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
        return "System Report at {time} in system {name}".format(time=self.time, name=self.system_name)

    def store_report(self):
        db.SystemReport.insert_one(self.as_json())
        print(self.player_objects)
        system = db.Systems.find_one({"name": self.system_name})
        if not system:
            # System doesnt exist, so we're gonna make a new one
            system = System(name_data,self.system_name,{})
            system = system.as_json()

        for player in self.player_objects:
            player.get_stats()
            pjson = player.as_json()
            print(pjson)
            system["common_players"][pjson["_id"]] =system["common_players"].get(pjson["_id"],0)+1
            db.Characters.update_one({"_id": pjson["_id"]}, { "$set":pjson}, upsert=True)
        db.Systems.update_one({"name": system["name"]}, {"$set": system}, upsert=True)



    def __del__(self):
        self.player_objects = []
