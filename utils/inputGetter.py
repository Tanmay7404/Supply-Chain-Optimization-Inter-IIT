import csv
from utils.structs import ULD,Package

def getPackages(packages,test=False,idx = 0):
    if test:
        f = open("Test_Data/dummy_data_"+str(idx)+".csv", mode="r")
    else:
        f = open("package.csv", mode="r")
    packageCSV = csv.reader(f)
    for p in packageCSV:
        if p[5] == "Economy":
            package = Package(p[1],p[2],p[3],p[4],p[0],p[5],p[6])
            packages.append(package)
        else:
            package = Package(p[1],p[2],p[3],p[4],p[0],p[5])
            packages.append(package)
    return packages

def getULD(ulds):
    f = open("ULD.csv", mode="r")
    uldCSV = csv.reader(f)
    for u in uldCSV:
        uld = ULD(u[1],u[2],u[3],u[4],u[0])
        ulds.append(uld)
    return ulds