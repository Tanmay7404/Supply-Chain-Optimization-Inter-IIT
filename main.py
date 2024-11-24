from structs import ULD,Package
import csv



class Solver1:
    
    def __init__(self,packages,ulds):
        self.packages = packages
        self.ulds = ulds
        self.priority = []
        self.economy = []

        for package in packages:
            if package.priorty == "Priority":
                self.priority.append(package)
            else:
                self.economy.append(package)
        #most expensive to ship first
        self.economy.sort(reverse=True)



k = 5000
ulds = []
packages = []

def getPackages():
    f = open("package.csv", mode="r")
    packageCSV = csv.reader(f)
    for p in packageCSV:
        if p[5] == "Economy":
            package = Package(p[1],p[2],p[3],p[4],p[0],p[5],p[6])
            packages.append(package)

def getULD():
    f = open("ULD.csv", mode="r")
    uldCSV = csv.reader(f)
    for u in uldCSV:
        uld = ULD(u[1],u[2],u[3],u[4],u[0])
        ulds.append(uld)

getPackages()
getULD()
