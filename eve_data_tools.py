import csv
import math
from datetime import datetime


def get_system_data():
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
    system_data = {}
    with open("resources/mapSolarSystems.csv") as systems:
        file = csv.reader(systems)
        for line in file:
            try:
                system_data[line[3]] = {"system_id": line[2]}
            except ValueError:
                print("Casting Error")

    return system_data


def get_possible_drifter_systems():
    drifter_systems = {}
    with open("resources/drifter_holes.csv") as drifters:
        file = csv.reader(drifters)
        for line in file:
            drifter_systems[line[0].strip()] = {"system": line[0].strip(),
                                                "constellation": line[1].strip(),
                                                "region": line[2].strip()}
    return drifter_systems


def get_system_jumps(system_data: dict):
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
    """simple 3d distance calculation for jump range, returns *rough* distance in LY"""
    system_1_data = system_data[system_1]
    system_2_data = system_data[system_2]
    coords_1 = (system_1_data["x_coord_min"], system_1_data["y_coord_min"], system_1_data["z_coord_min"])
    coords_2 = (system_2_data["x_coord_max"], system_2_data["y_coord_max"], system_2_data["z_coord_max"])
    # TODO Something is slightly off with calculation, as im not sure exactly how EVE calculates jump distance
    dist = math.sqrt(
        (coords_2[0] - coords_1[0]) ** 2 + (coords_2[1] - coords_1[1]) ** 2 + (coords_2[2] - coords_1[2]) ** 2)
    return dist / (10 ** 16)


def get_path_to_system(system_data: dict, start: str, end: str, debug=False):
    """BFS to find gate jump min distance, returns -1 if no gate-to-gate route"""
    queue = []
    visited = []
    system_1_data = system_data[start]
    current = system_1_data["gates"]
    distance_to_target = get_system_distance(system_data, start, end)
    start_time = datetime.now()
    if debug:
        print("Distance To Target: " + str(distance_to_target))
        print("Finding route from " + system_data[start]["name"] + " to " + system_data[end]["name"])
    queue.append((current, 0, distance_to_target))
    while queue:
        system = queue.pop(0)
        visited.append(system[0])
        for gate in system[0]:
            if gate == end:
                if debug:
                    print("Found Route from " + system_data[start]["name"] + " to " + system_data[end]["name"] + " in " + str(datetime.now() - start_time))
                return system[1] + 1
            else:
                if gate not in visited:
                    curr_dist = get_system_distance(system_data, gate, end)
                    queue.append((system_data[gate]["gates"], system[1] + 1, curr_dist))
                    if debug:
                        print("System:" + system_data[gate]["name"] + " Current Distance " + str(curr_dist))
                    visited.append(gate)
                else:
                    if debug:
                        print("Already Visited " + system_data[gate]["name"])
                    pass

    return -1
def get_drifter_systems():
    """Returns list of all drifter systems"""
    systems = []
    with open("resources/drifter_holes.csv") as data:
        file = csv.reader(data)
        for line in file:
            systems.append(line[0].strip())
    return systems


def get_nearest_drifter_systems(drifters:list, system_data: dict,system:str, jumps: int):
    """Returns all drifter systems within x jumps"""
    drifters_nearby = []
    queue = []
    visited = []
    system_1_data = system_data[system]
    current = system_1_data["gates"]
    start_time = datetime.now()
    queue.append((current, 0))
    while queue:
        system = queue.pop(0)
        visited.append((system[0],system[1]+1))
        for gate in system[0]:
            if system_data[gate]["name"] in drifters and gate not in drifters_nearby:
                drifters_nearby.append(gate)
            if system[1]>=jumps:
                return drifters_nearby
            else:
                if gate not in visited:
                    queue.append((system_data[gate]["gates"], system[1] + 1))
                    visited.append(gate)


name_data = get_system_data_by_name()
sysdata = get_system_jumps(get_system_data())
# print(get_system_distance(sysdata, name_data["1DQ1-A"]["system_id"], name_data["T5ZI-S"]["system_id"]))
print(get_path_to_system(sysdata, name_data["1DQ1-A"]["system_id"], name_data["Jita"]["system_id"], False))
drifters_near_1dq = get_nearest_drifter_systems(get_drifter_systems(),sysdata,name_data["1DQ1-A"]["system_id"],3)

for hole in drifters_near_1dq:
    print(sysdata[hole]["name"])