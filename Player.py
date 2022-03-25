
class player:
    name =""
    common_ships = []
    recent_deaths = []
    recent_kills = []
    common_systems = []
    uuid = ""

    def __init__(self,name:str):
        self.name = name