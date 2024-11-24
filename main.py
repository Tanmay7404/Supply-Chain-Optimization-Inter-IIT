import csv


k = 5000
uld = []
packages_p = []
packages_e = []

def getPackages():
    f = open("package.csv", mode="r")
    packageCSV = csv.reader(f)
    for package in packageCSV:
        if package[5] == "Economy": packages_e.append(package)
        else: packages_p.append(package)

def getULD():
    f = open("ULD.csv", mode="r")
    uldCSV = csv.reader(f)
    for uldItem in uldCSV:
        uld.append(uldItem)

getPackages()
getULD()



