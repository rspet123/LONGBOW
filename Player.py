class Player:
    """Class to store and analyze player data"""
    name = ""
    common_ships = []
    recent_deaths = []
    recent_kills = []
    common_systems = []
    uuid = ""

    def __init__(self, name: str):
        self.name = name
