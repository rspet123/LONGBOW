import csv
import math
from Player import Player
from datetime import datetime


def get_system_data():
    """
    It reads the mapSolarSystems.csv file and creates a dictionary of dictionaries
    :return: A dictionary of dictionaries.
    """
    system_data = {}

    # regionID,constellationID,solarSystemID,solarSystemName,x,y,z,xMin,xMax,yMin,yMax,zMin,zMax,luminosity,border,fringe,corridor,hub,international,regional,constellation,security,factionID,radius,sunTypeID,securityClass
    with open("resources/mapSolarSystems.csv") as systems:
        file = csv.reader(systems)
        for line in file:
            try:
                system_data[line[2]] = {"name": line[3],
                                        "constellation_id": line[1],
                                        "x_coord": float(line[4]),
                                        "y_coord": float(line[5]),
                                        "z_coord": float(line[6]),
                                        "x_coord_min": float(line[7]),
                                        "y_coord_min": float(line[9]),
                                        "z_coord_min": float(line[11]),
                                        "x_coord_max": float(line[8]),
                                        "y_coord_max": float(line[10]),
                                        "z_coord_max": float(line[12]),
                                        "sec_status": line[21],
                                        "gates": []}
            except Exception:
                print("Casting Error")

    return system_data


def get_system_data_by_name():
    """
    It opens the mapSolarSystems.csv file, reads it into a list, and then creates a dictionary with the system name as the
    key and the system id as the value
    :return: A dictionary of system names and their system_id
    """
    system_data = {}
    with open("resources/mapSolarSystems.csv") as systems:
        file = list(csv.reader(systems))
        for line in file[1:]:
            try:
                system_data[line[3]] = {"system_id": line[2]}
            except Exception:
                print("Casting Error")

    return system_data


def get_possible_drifter_systems():
    """
    It reads the file "JoveSystems.csv" and returns a dictionary of the systems, constellations, and regions
    :return: A dictionary of dictionaries.
    """
    drifter_systems = {}
    with open("resources/JoveSystems.csv") as drifters:
        file = csv.reader(drifters)
        for line in file:
            drifter_systems[line[0].strip()] = {"system": line[0].strip(),
                                                "constellation": line[1].strip(),
                                                "region": line[3].strip()}
    return drifter_systems


def get_system_jumps(system_data: dict):
    """
    It takes a dictionary of system data and adds a list of the systems that each system can jump to

    :param system_data: dict
    :type system_data: dict
    :return: A dictionary of dictionaries.
    """
    # fromRegionID, fromConstellationID, fromSolarSystemID, toSolarSystemID, toConstellationID, toRegionID
    with open("resources/mapSolarSystemJumps.csv") as gates:
        file = csv.reader(gates)
        for jump in file:
            try:
                jumps_to = system_data[jump[3]]["name"]

                system_data[jump[2]]["gates"].append(jump[3])
                # print(system_data[jump[2]]["name"] + "\t --> \t" + jumps_to)
            except KeyError:
                print("No Such System")

    return system_data


def get_system_distance(system_data: dict, system_1: str, system_2: str):
    """
    > Calculate the distance between two systems by taking the distance between the minimum and maximum coordinates of each
    system

    :param system_data: a dictionary of all the systems in EVE, with their coordinates and other data
    :type system_data: dict
    :param system_1: The name of the system you want to start from
    :type system_1: str
    :param system_2: str = "Jita"
    :type system_2: str
    :return: A dictionary of all the systems in the game.
    """
    """simple 3d distance calculation for jump range, returns *rough* distance in LY"""
    system_1_data = system_data[system_1]
    system_2_data = system_data[system_2]
    coords_1 = (system_1_data["x_coord_min"], system_1_data["y_coord_min"], system_1_data["z_coord_min"])
    coords_2 = (system_2_data["x_coord_max"], system_2_data["y_coord_max"], system_2_data["z_coord_max"])
    # TODO Something is slightly off with calculation, as im not sure exactly how EVE calculates jump distance
    dist = math.sqrt(
        (coords_2[0] - coords_1[0]) ** 2 + (coords_2[1] - coords_1[1]) ** 2 + (coords_2[2] - coords_1[2]) ** 2)
    return dist / (10 ** 16)


def get_path_to_system(system_data: dict, start: str, end: str):
    """
    BFS Search to find number of jumps to system

    If we run out of gates to visit, we return -1.

    :param system_data: a dictionary of all the systems in the game
    :type system_data: dict
    :param start: The system ID of the starting system
    :type start: str
    :param end: The system you want to get to
    :type end: str
    :return: The number of jumps from the start system to the end system.
    """
    """BFS to find gate jump min distance, returns -1 if no gate-to-gate route"""
    queue = []
    visited = []
    print("Finding route from " + system_data[start]["name"] + " to " + system_data[end]["name"])
    system_1_data = system_data[start]
    current = system_1_data["gates"]
    distance_to_target = get_system_distance(system_data, start, end)
    print("Distance To Target: " + str(distance_to_target))
    queue.append((current, 0, distance_to_target))
    while queue:
        system = queue.pop(0)
        visited.append(system[0])
        for gate in system[0]:
            if gate == end:
                return (system[1] + 1)
            else:
                if gate not in visited:
                    curr_dist = get_system_distance(system_data, gate, end)
                    queue.append((system_data[gate]["gates"], system[1] + 1, curr_dist))
                    print("System:" + system_data[gate]["name"] + " Current Distance " + str(curr_dist))
                    visited.append(gate)
                else:
                    # print("Already Visited " + system_data[gate]["name"])
                    pass

    return -1


def get_nearest_drifter_systems(drifters: list, system_data: dict, system: str, jumps: int):
    """
    > This function takes a list of drifter systems, a dictionary of system data, a system name, and a number of jumps, and
    returns a list of all drifter systems within x jumps

    :param drifters: list of drifter systems
    :type drifters: list
    :param system_data: This is the data from the system_data.json file
    :type system_data: dict
    :param system: The system you're starting from
    :type system: str
    :param jumps: The number of jumps you want to search for drifters
    :type jumps: int
    :return: A list of all drifter systems within x jumps
    """
    """Returns all drifter systems within x jumps"""
    # TODO Have this return a dict, with key of name, and value as #jumps
    drifters_nearby = []
    queue = []
    visited = []
    system_1_data = system_data[system]
    current = system_1_data["gates"]
    queue.append((current, 0))
    while queue:
        system = queue.pop(0)
        visited.append((system[0], system[1] + 1))
        for gate in system[0]:
            if system_data[gate]["name"] in drifters and gate not in drifters_nearby:
                drifters_nearby.append(gate)
            if system[1] >= jumps:
                return drifters_nearby
            else:
                if gate not in visited:
                    queue.append((system_data[gate]["gates"], system[1] + 1))
                    visited.append(gate)
