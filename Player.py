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
    num_recent_kills = 0
    sec_status = 0
    last_system = ""
    id_url = "https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en"
    notes = []
    last_report = ""
    times = []

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


    def __init__(self, name: str, char_id: str,last_system:str, last_seen, last_report):
        """Create Single Character, from list of multiple from systemreport"""
        self.name = name
        self.char_id = char_id
        self.last_seen = last_seen
        self.notes = []
        self.last_system = last_system
        self.last_report = last_report
        self.times = []
        self.common_systems = {}

    async def get_deaths(self, recent=5):
        """
        It takes the character ID of a player, and then uses the zKillboard API to get the most recent 5 kills of that
        player. It then uses the ESI to get the killmail for each of those kills, and then adds the killmail to a list of
        recent deaths. It also adds the solar system ID of the kill to a dictionary of common systems, and increments the
        value of that system by 1

        :param recent: How many recent deaths to get, defaults to 5 (optional)
        :return: A list of dictionaries, each dictionary is a killmail
        """
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
        """
        It takes the character ID of a player, and then uses the zKillboard API to get the most recent kills of that player.


        The function then takes the killmail ID and hash of each kill, and uses the ESI API to get the full killmail.

        The function then adds the killmail to a list of recent kills, and adds the solar system ID of the kill to a
        dictionary of common systems.

        The function then returns the list of recent kills.

        :param recent: How many kills to get, defaults to 5 (optional)
        :return: A list of dictionaries.
        """
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
        """
        It takes a character name, and returns a dictionary of the character's stats
        :return: A list of dictionaries.
        """
        """Gathers stats from zKillboard's API"""
        # We need to cast all ints etc to strings for storage on mongodb
        # Use this https://evewho.com/api/character/1633218082
        # TODO Really REALLY fix this

        print(self.name)
        evewho_response = requests.get(f"https://evewho.com/api/character/{self.name}")
        print(evewho_response.text)
        evewho_data = json.loads(evewho_response.text)
        print(evewho_data)
        self.corp_id = evewho_data["info"][0]["corporation_id"]
        self.alliance_id = evewho_data["info"][0]["alliance_id"]
        self.sec_status = evewho_data["info"][0]["sec_status"]

        # TODO FIX ZKILL
        #try:
        #    response = requests.get("https://zkillboard.com/api/stats/characterID/{id}/".format(id=self.char_id))
        #    stats_data = json.loads(response.text)
        #except Exception:
        #    print("Not on zKill")
        #    return -1
        #try:
        #    self.corp_id = stats_data["info"]["corporationID"]
        #    self.alliance_id = stats_data["info"]["allianceID"]
        #    self.sec_status = stats_data["info"]["secStatus"]
        #except KeyError:
        #    self.corp_id = "98494816"
        #    self.alliance_id = "99005678"
        ## TODO zkill api integration is busted
        ## Add common Ships
        #try:
        #    # Add common Systems
        #    for system in stats_data["topLists"][4]["values"]:
        #        print(system)
        #        self.common_systems[str(system["solarSystemID"])] = system["kills"]
        #    for ship in stats_data["topLists"][3]["values"]:
        #        print(ship)
        #        self.common_ship_types[str(ship["groupID"])] = str(ship["kills"])
        #        self.common_ships[str(ship["shipTypeID"])] = str(ship["kills"])
        #except KeyError:
        #    self.common_ship_types["NA"] = str({})
        #    self.common_ships["NA"] = str({})
        #    self.common_systems["NA"] = str({})
        #try:
        #    self.isk_lost = stats_data["iskLost"]
        #    self.isk_killed = stats_data["iskDestroyed"]
        #    self.danger = stats_data["dangerRatio"]
        #except KeyError:
        #    # No key? Default values
        #    self.isk_lost = 0
        #    self.isk_killed = 0
        #    self.danger = 0

        return 1

    def as_json(self):
        """
        It takes the data from the class and returns it as a dictionary
        :return: A dictionary of the class attributes.
        """
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
            "notes":self.notes,
            "last_system":self.last_system,
            "last_report":self.last_report,
            "times":self.times
        }

    def __hash__(self):
        """
        The hash function is used to hash the player class in a dict
        :return: The hash of the character id.
        """
        """Allows us to hash the player class in a dict"""
        return hash(self.char_id)

    def __str__(self):
        return self.name


