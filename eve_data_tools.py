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
                                    "sec_status":line[21]}
    return system_data

print(get_system_data()["30003135"])