from structs import ULD,Package
import csv



class Solver1:
    
    def __init__(self,packages,ulds):
        self.packages = packages
        self.ulds = ulds
        self.priorityDone = 0
        self.priority = []
        self.economy = []

        for package in packages:
            if package.priority == "Priority":
                self.priority.append(package)
            else:
                self.economy.append(package)
        #most expensive to ship first
        # self.ulds.sort(key=lambda x: x.weight_limit,reverse=True)
        self.ulds.sort(key=lambda x: x.getVolume(),reverse=True)
        self.priority.sort(key=lambda x: x.getVolume(),reverse=True)
        self.economy.sort(key=lambda x: x.getVolume(),reverse=True)

    def solve(self):
        for uld in self.ulds:
            print("ULD: ",uld.id)
            corners = [[0,0,0]]
            if self.priorityDone < 103:
                for package in self.priority:
                    if package.ULD == -1: 
                        done = False
                        for corner in corners:
                            if(uld.addBox(package,corner)):
                                #remove this corner and add the other 7 corner 
                                corners.remove(corner)
                                new_corners = uld.getNewCorners(package, corner)
                                corners.extend(new_corners)
                                #sort the corners by the z value
                                # corners.sort(key=lambda x: x[0])
                                # corners.sort(key=lambda x: x[1])
                                corners.sort(key=lambda x: x[2])

                                done = True
                                break
                        if done:
                            self.priorityDone+=1
            for package in self.economy:
                if package.ULD == -1: 
                    done = False
                    for corner in corners:
                        if(uld.addBox(package,corner)):
                            #remove this corner and add the other 7 corner 
                            corners.remove(corner)
                            new_corners = uld.getNewCorners(package, corner)
                            corners.extend(new_corners)
                            done = True
                            break
                    if done:
                        self.priorityDone+=1






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
        else:
            package = Package(p[1],p[2],p[3],p[4],p[0],p[5])
            packages.append(package)

def getULD():
    f = open("ULD.csv", mode="r")
    uldCSV = csv.reader(f)
    for u in uldCSV:
        uld = ULD(u[1],u[2],u[3],u[4],u[0])
        ulds.append(uld)

def metrics(ulds):
    freeSpace = 0
    totalSpace = 0
    freeWeight = 0
    totalWeight = 0
    for uld in ulds:
        uldfreeSpace = uld.getVolume()
        uldtotalSpace = uld.getVolume()
        totalSpace+=uld.getVolume()
        freeSpace+=uld.getVolume()
        totalWeight+=uld.weight_limit
        freeWeight+=uld.weight_limit
        uldfreeWeight = uld.weight_limit
        uldtotalWeight = uld.weight_limit
        for package in uld.packages:
            uldfreeSpace-=package.getVolume()
            freeSpace-=package.getVolume()
            uldfreeWeight-=package.weight
            freeWeight-=package.weight
        print(str(uldfreeSpace/uldtotalSpace*100)+"% free space in uld ",uld.id)
        print(str(uldfreeWeight/uldtotalWeight*100)+"% free weight in uld ",uld.id)
    print(str(freeSpace/totalSpace*100)+"% free uld space") 
    print(str(freeWeight/totalWeight*100)+"% free uld weight")   
    cost = 0
    for package in packages:
        if package.ULD == -1: cost+=package.cost
    print("Cost without accounting for priority uld (k) = ", cost)
    for uld in ulds:
        if uld.isPriority: cost+=k
    
    print(" Total Cost = ", cost)


getPackages()
getULD()


solver = Solver1(packages,ulds)
solver.solve()
metrics(ulds)