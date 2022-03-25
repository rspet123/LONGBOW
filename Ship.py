
class ship:
    ship_name = ""
    ship_type = ""
    hull = ""
    
    def __init__(self,ship_name: str,ship_type: str,hull:str):
        self.ship_name = ship_name
        self.ship_type = ship_type
        self.hull = hull