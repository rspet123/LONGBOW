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
        """
        This function takes in a dictionary of system names and their corresponding system IDs, a system name, and a
        dictionary of players and their corresponding number of games played. It then creates a system object with the name
        and system ID of the system name passed in, and creates a dictionary of players and their corresponding number of
        spottings in the system

        :param sys_name_data: a dictionary of system names and their corresponding system IDs
        :type sys_name_data: dict
        :param name: The name of the system
        :type name: str
        :param players: a dictionary of players, with the key being the player's name and the value being the player's ID
        :type players: dict
        """
        """Create system by ID"""
        # TODO
        self.name = name
        self.system_id = sys_name_data[name]["system_id"]
        self.common_players = {}
        for player in players:
            self.common_players[player] = self.common_players.get(player,0)+1

    def update_players(self,players:list):
        """
        It takes a list of players and updates the dictionary of common players

        :param players: list of players
        :type players: list
        """
        for player in players:
            self.common_players[player] = self.common_players.get(player,0)+1

    def as_json(self):
        """
        The function takes in a system object and returns a dictionary with the system's name, system_id, common_players,
        and _id
        :return: A dictionary with the name, system_id, common_players, and _id of the game.
        """
        return{
            "name":self.name,
            "system_id":self.system_id,
            "common_players":self.common_players,
            "_id":self.name
        }
