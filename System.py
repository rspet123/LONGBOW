import Player

class System:
    name = ""
    system_id = ""
    x = 0
    y = 0
    z = 0
    common_players = {}
    gates = []
    nearest_drifters = []

    def __init__(self, sys_name_data: dict, name: str,players:dict):
        """Create system by ID"""
        # TODO
        self.name = name
        self.system_id = sys_name_data[name]["system_id"]
        self.common_players = {}
        for player in players:
            self.common_players[player] = self.common_players.get(player,0)+1

    def update_players(self,players:list):
        for player in players:
            self.common_players[player] = self.common_players.get(player,0)+1

    def as_json(self):
        return{
            "name":self.name,
            "system_id":self.system_id,
            "common_players":self.common_players,
            "_id":self.name
        }
