import requests
import json
from datetime import datetime, timezone
import db


class Player:
    name = ""
    corp_id = ""
    alliance_id = ""
    common_ships = {}
    common_ship_types = {}
    recent_deaths = []
    recent_kills = []
    kill_hashes = []
    last_seen = ""
    common_systems = {}
    cap_pilot = False
    char_id = ""
    isk_killed = 0
    isk_lost = 0
    danger = 0
    recent_kills = 0
    sec_status = 0
    id_url = "https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en"
    notes = []

    # TODO add images
    # https://zkillboard.com/api/stats/characterID/447073625/
    # https://images.evetech.net/characters/1338057886
    # https://esi.evetech.net/latest/universe/ids/?datasourc =tranquility&language=en
    @staticmethod
    def store_player(character: dict):
        # TODO Fix upsert etc
        db.Characters.update({"_id":character["_id"]},character,upsert=True)

    @staticmethod
    def store_players(characters: list):
        # TODO Fix upsert etc
        try:
            db.Characters.insert_many(characters)
        except Exception:
            1 == 1  # db.Characters.update_many(characters,upsert=True)


    def __init__(self, name: str, char_id: str):
        """Create Single Character, from list of multiple from systemreport"""
        self.name = name
        self.char_id = char_id
        self.last_seen = datetime.now(timezone.utc)
        self.notes = []

    async def get_deaths(self, recent=5):
        """Async calls to get deaths from zkb"""
        # Probably shouldn't use this
        response = requests.get("https://zkillboard.com/api/losses/characterID/{id}/".format(id=self.char_id))
        death_data = json.loads(response.text)
        for death in death_data[0:recent]:
            km_id = death["killmail_id"]
            km_hash = death["zkb"]["hash"]
            current_lossmail = requests.get("https://esi.evetech.net/latest/killmails/" + str(
                km_id) + "/" + km_hash + "/?datasource=tranquility").json()
            self.recent_deaths.append(current_lossmail)
            self.common_systems[current_lossmail["solar_system_id"]] = self.common_systems.get(
                current_lossmail["solar_system_id"], 0) + 1
        return death_data

    async def get_kills(self, recent=5):
        """Async calls to get deaths from zkb"""
        # Probably shouldn't use this
        response = requests.get("https://zkillboard.com/api/kills/characterID/{id}/".format(id=self.char_id))
        kills_data = json.loads(response.text)
        for kill in kills_data[0:recent]:
            km_id = kill["killmail_id"]
            km_hash = kill["zkb"]["hash"]
            current_killmail = requests.get("https://esi.evetech.net/latest/killmails/" + str(
                km_id) + "/" + km_hash + "/?datasource=tranquility").json()
            self.recent_kills.append(current_killmail)
            self.common_systems[current_killmail["solar_system_id"]] = self.common_systems.get(
                current_killmail["solar_system_id"], 0) + 1
            print(current_killmail)

        return kills_data

    def get_stats(self):
        """Gathers stats from zKillboard's API"""
        # We need to cast all ints etc to strings for storage on mongodb
        # TODO Really fix this
        try:
            response = requests.get("https://zkillboard.com/api/stats/characterID/{id}/".format(id=self.char_id))
            stats_data = json.loads(response.text)
        except Exception:
            print("Not on zKill")
            return -1
        try:
            self.corp_id = stats_data["info"]["corporationID"]
            self.alliance_id = stats_data["info"]["allianceID"]
            self.sec_status = stats_data["info"]["secStatus"]
        except KeyError:
            self.corp_id = "98494816"
            self.alliance_id = "99005678"
        # TODO zkill api integration is busted
        # Add common Ships
        try:
            # Add common Systems
            for system in stats_data["topLists"][4]["values"]:
                print(system)
                self.common_systems[str(system["solarSystemID"])] = system["kills"]
            for ship in stats_data["topLists"][3]["values"]:
                print(ship)
                self.common_ship_types[str(ship["groupID"])] = str(ship["kills"])
                self.common_ships[str(ship["shipTypeID"])] = str(ship["kills"])
        except KeyError:
            self.common_ship_types["NA"] = str({})
            self.common_ships["NA"] = str({})
            self.common_systems["NA"] = str({})
        try:
            self.isk_lost = stats_data["iskLost"]
            self.isk_killed = stats_data["iskDestroyed"]
            self.danger = stats_data["dangerRatio"]
        except KeyError:
            # No key? Default values
            self.isk_lost = 0
            self.isk_killed = 0
            self.danger = 0

        return 1

    def as_json(self):
        """Function to return as a dict/json for MondoDB storage"""
        return {
            "_id": self.char_id,
            "name": self.name,
            "danger": self.danger,
            "isk_killed": self.isk_killed,
            "corp_id": self.corp_id,
            "alliance_id": self.alliance_id,
            "common_ships": self.common_ships,
            "common_systems": self.common_systems,
            "common_ship_typs": self.common_ship_types,
            "sec_status": self.sec_status,
            "last_seen":self.last_seen,
            "notes":self.notes
        }

    def __hash__(self):
        """Allowing us to hash the player class in a dict"""
        return self.char_id

    def __str__(self):
        return self.name


