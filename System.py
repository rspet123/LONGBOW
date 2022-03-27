import Player

class System:
    name = ""
    system_id = ""
    x = 0
    y = 0
    z = 0
    common_players = {}
    gates = []

    def __init__(self, sysdata: dict, system_id: str):
        """Create system by ID"""
        # TODO
        self.system_id = system_id

    def __init__(self, sysdata_id: dict):
        """Create system by dict out of sysdata"""
        # TODO
        self.system_id = 1