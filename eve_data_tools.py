import csv

def get_system_data():
    system_data = {}
    #regionID,constellationID,solarSystemID,solarSystemName,x,y,z,xMin,xMax,yMin,yMax,zMin,zMax,luminosity,border,fringe,corridor,hub,international,regional,constellation,security,factionID,radius,sunTypeID,securityClass
    with open("resources/mapSolarSystems.csv") as systems:
        file = csv.reader(systems)
        for line in file:
            system_data[line[2]] = {"name":line[3],
                                    "constellation_id":line[1],
                                    "x_coord":line[4],
                                    "y_coord":line[5],
                                    "z_coord":line[6],
                                    "sec_status":line[21],
                                    "gates":[]}

    return system_data

def get_possible_drifter_systems():
    drifter_systems = {}
    with open("resources/drifter_holes.csv") as drifters:
        file = csv.reader(drifters)
        for line in file:
            drifter_systems[line[0].strip()] = {"system":line[0].strip(),
                                        "constellation":line[1].strip(),
                                        "region":line[2].strip()}
    return drifter_systems

def get_system_jumps(system_data: dict):
    #fromRegionID, fromConstellationID, fromSolarSystemID, toSolarSystemID, toConstellationID, toRegionID
    with open("resources/mapSolarSystemJumps.csv") as gates:
        file = csv.reader(gates)
        for jump in file:
            try:
                jumps_to = system_data[jump[3]]["name"]

                system_data[jump[2]]["gates"].append(jumps_to)
                print(system_data[jump[2]]["name"] + " --> "+jumps_to)
            except KeyError:
                print("No Such System")

    return(system_data)

def get_system_distance(system_data:dict,system_1:str,system_2:str):
    system_1_data = system_data[system_1]
    system_2_data = system_data[system_2]
    return("WIP")

(get_system_jumps(get_system_data()))