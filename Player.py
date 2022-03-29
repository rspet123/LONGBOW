import requests
import json


class Player:
    name = ""
    common_ships = []
    recent_deaths = []
    recent_kills = []
    common_systems = {}
    char_id = ""
    id_url = "https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en"

    # https://esi.evetech.net/latest/universe/ids/?datasourc =tranquility&language=en
    # TODO integrate with zKill API

    def __init__(self, name: str):
        """Create Single Character"""
        self.name = name

        # Set up our request
        headers = {}
        headers["accept"] = "application/json"
        headers["Accept-Language"] = "en"
        headers["Content-Type"] = "application/json"
        headers["Cache-Control"] = "no-cache"
        data = '["{chname}"]'.format(chname=name)

        resp = requests.post(self.id_url, headers=headers, data=data)
        char_id = json.loads(resp.text)["characters"][0]["id"]
        print(char_id)
        self.char_id = char_id

    async def get_deaths(self, recent=5):
        response = requests.get("https://zkillboard.com/api/losses/characterID/{id}/".format(id=self.char_id))
        death_data = json.loads(response.text)
        for death in death_data[0:recent]:
            km_id = death["killmail_id"]
            km_hash = death["zkb"]["hash"]
            current_lossmail = requests.get("https://esi.evetech.net/latest/killmails/" + str(
                km_id) + "/" + km_hash + "/?datasource=tranquility").json()
            print(current_lossmail)
            self.recent_deaths.append(current_lossmail)
            self.common_systems[current_lossmail["solar_system_id"]] = self.common_systems.get(
                current_lossmail["solar_system_id"], 0) + 1
        return death_data

    async def get_kills(self, recent=5):
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
