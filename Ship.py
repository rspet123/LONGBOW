class Ship:
    """Class to keep track of ship objects"""
    ship_name = ""
    ship_type = ""
    hull = ""

    def __init__(self, ship_name: str, ship_type: str, hull: str):
        """
        This function takes in three arguments, ship_name, ship_type, and hull, and assigns them to the instance variables
        of the same name

        :param ship_name: The name of the ship
        :type ship_name: str
        :param ship_type: This is the type of ship. It can be a "cruiser" or a "destroyer" etc
        :type ship_type: str
        :param hull: The hull of the ship. This is the base of the ship
        :type hull: str
        """
        self.ship_name = ship_name
        self.ship_type = ship_type
        self.hull = hull
