import csv
import math


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
                                        "sec_status": line[21],
                                        "gates": []}
            except Exception:
                print("Casting Error")

    return system_data

def get_system_data_by_name():
    system_data = {}
    # regionID,constellationID,solarSystemID,solarSystemName,x,y,z,xMin,xMax,yMin,yMax,zMin,zMax,luminosity,border,fringe,corridor,hub,international,regional,constellation,security,factionID,radius,sunTypeID,securityClass
    with open("resources/mapSolarSystems.csv") as systems:
        file = csv.reader(systems)
        for line in file:
            try:
                system_data[line[3]] = {"system_id": line[2],
                                        "x_coord": float(line[4]),
                                        "y_coord": float(line[5]),
                                        "z_coord": float(line[6]),}
            except Exception:
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
                print(system_data[jump[2]]["name"] + "\t --> \t" + jumps_to)
            except KeyError:
                print("No Such System")

    return (system_data)


def get_system_distance(system_data: dict, system_1: str, system_2: str):
    system_1_data = system_data[system_1]
    system_2_data = system_data[system_2]
    coords_1 = (system_1_data["x_coord"],system_1_data["y_coord"],system_1_data["z_coord"])
    coords_2 = (system_2_data["x_coord"], system_2_data["y_coord"], system_2_data["z_coord"])
    dist = math.sqrt((coords_2[0]-coords_1[0])**2+(coords_2[1]-coords_1[1])**2+(coords_2[2]-coords_1[2])**2)
    return dist


sysdata = get_system_data_by_name()

print(get_system_distance(sysdata, "1DQ1-A","T5ZI-S"))
