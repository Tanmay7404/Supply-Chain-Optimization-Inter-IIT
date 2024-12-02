import math

from utils.structs import Axis

class Solver2:
    def __init__(self, packages, ulds):
        self.packages = packages
        self.ulds = ulds
        self.priority = []
        self.economy = []
        self.takenPackages = []
        self.priorityULDs =  0

        for package in packages:
            if package.priority == "Priority":
                self.priority.append(package)
            else:
                self.economy.append(package)

    def calculateEuclideanDistance(self, point):
        return math.sqrt(point[0] ** 2 + point[1] ** 2 + point[2] ** 2)
    
    def sortPackagesAssignment(self, packages):

        k=4
        k2=3

        priority_packages = [p for p in packages if p.priority == "Priority"]
        non_priority_packages = [p for p in packages if p.priority != "Priority"]
        
        priority_packages.sort(key=lambda x: x.getVolume(), reverse=True)
        # priority_packages.sort(key=lambda x: (math.floor(x.getVolume()/10), min(x.getDimensions()[0], x.getDimensions()[1], x.getDimensions()[2])), reverse=True)
        non_priority_packages.sort(key=lambda x: x.cost**3/(x.getVolume()**2 + x.weight**2), reverse=True)
        
        packages[:] = priority_packages + non_priority_packages
   
    
    def sortULDPackages(self, packages):
        packages.sort(key=lambda x: (math.floor(x.getDimensions()[2]/10),(x.getVolume())/(x.getDimensions()[2])), reverse=True)

    def sortULDs(self):
        self.ulds.sort(key=lambda x: x.getWeight(), reverse=True)


    def fitPackages(self, packages, uld, corners, isassigning = 0):# P : this is fitpackagePriority
        takenPackages = []
      
        for package in packages:
            uld.calculatePushLimit()
            
            if package.ULD == -1: 
                done = False

                corners.sort(key=lambda corner: self.calculateEuclideanDistance(corner)) #sort on basis of euclidian
                for corner in corners:
                    if uld.addBox(package, corner):
                        # Remove this corner and add the other 7 new corners
                        corners.remove(corner)
                        new_corners = uld.getNewCorners(package)
                        corners.extend(new_corners)

                        # Re-sort corners by Euclidean distance for the next iteration
                        corners.sort(key=lambda x: self.calculateEuclideanDistance(x))
                        
                        takenPackages.append(package)
                        done = True
                        break
                    # elif(uld.pushAddBox(package, corner)):
                    #     done = True
                    #     takenPackages.append(package)
                    #     corners = uld.recalculate_corners()
                    #     corners.sort(key=lambda x: self.calculateEuclideanDistance(x))
                    #     break
        
                    
        # uld.plotULD()

        print(len(takenPackages))        
        return corners, takenPackages
    
    # P : we will define new fitpackageEconomy only difference will be we will iterate through uld,package,corner,rotation rest will be same

    def assignPackagesPriority(self):
        ulds = self.ulds[0:len(self.ulds)]
        cm = {}
        for i in ulds:
            cm[i.id] = [[0, 0, 0]]
            # print("Assigning Priorty ULD: ", uld.id)
            # [_, packagesInULD] = self.fitPackages(self.packages, uld, [[0, 0, 0]],True)
        [_,takenPackages] = self.fit_int_ulds(self.packages, ulds, cm,"Assigning Proirity", assigning = 1)
        self.takenPackages.extend(takenPackages)

        for uld in ulds:
            if(len(uld.packages)!=0):
                self.priorityULDs+=1
        for uld in ulds:
            uld.clearBin()

        return
    
    def assignPackagesNormal(self):

        # Initial fit for figuring out the assignment of packages to ULDs
        ulds = self.ulds[self.priorityULDs:len(self.ulds)]
        cm = {}
        for i in ulds:
            cm[i.id] = [[0, 0, 0]]
        [_,takenPackages] = self.fit_int_ulds(self.packages, ulds, cm,"Assigning Normal")
        self.takenPackages.extend(takenPackages)

        for uld in ulds:
            uld.clearBin()

        return
    
    

    def fit_int_ulds(self,packages,ulds,cornermap,mess, assigning = 0):
        takenPackages = []
        for ii,uld in enumerate(ulds):
            
            print(mess + " ULD: ", uld.id)
            [corners, taken_pck] = self.fitPackages(packages, uld, cornermap[uld.id])
            done = False
            cornermap[uld.id] = corners
            takenPackages.extend(taken_pck)
            for unpacked_package in packages:
                if unpacked_package.ULD == -1:
                    for jj in range(ii+1):
                        ulds[jj].calculatePushLimit()
                        for poss_replace in ulds[jj].packages:
                            if(ulds[jj].inflate_and_replace(unpacked_package,poss_replace)):
                                if(takenPackages.count(poss_replace) > 0):
                                    takenPackages.remove(poss_replace)
                                takenPackages.append(unpacked_package)
                                cornermap[uld.id] = ulds[jj].recalculate_corners()
                                cornermap[uld.id].sort(key=lambda x: self.calculateEuclideanDistance(x))
                                done = True
                                break
                        if done:
                            break   
                
            if(assigning==1):
                priority_done = True
                for pack in self.packages:
                    if (pack not in takenPackages) and (pack.priority == "Priority"):
                        priority_done = False
                        break
                if(priority_done):
                    break
        return cornermap,takenPackages

    def solve(self):

        self.sortPackagesAssignment(self.packages)
        self.sortULDs()

        self.assignPackagesPriority()

        cornermap = {}
        for uld in self.ulds:
            cornermap[uld.id] = [[0, 0, 0]]

        # Refit the packages into their respective ULD
        self.sortULDPackages(self.takenPackages)
        [cornermap,_] = self.fit_int_ulds(self.takenPackages, self.ulds, cornermap,"Fitting Proirity")
        # for uld in self.ulds:
        #     # self.sortULDPackages(uldMapping[uld.id])
        #     print("Fitting Priority ULD: ", uld.id)
        #     [corners, _] = self.fitPackages(self.takenPackages, uld, [[0, 0, 0]])
        #     cornermap[uld.id] = corners

        self.takenPackages = []
        self.assignPackagesNormal()
        self.sortULDPackages(self.takenPackages)
        
        [cornermap,_] = self.fit_int_ulds(self.takenPackages, self.ulds, cornermap,"Fitting Normal")

        self.sortULDPackages(self.packages)

        [cornermap,_] = self.fit_int_ulds(self.packages, self.ulds, cornermap,"Fitting Remaining")

        for uld in self.ulds:
            for package in uld.packages:
                for axis in Axis.ALL:
                    if uld.project(package,axis) != -1:
                        package.position[axis] = uld.project(package,axis)


        # self.ulds[0].plotULD()
        # self.ulds[1].plotULD()
        # self.ulds[2].plotULD()
        # self.ulds[3].plotULD()
        # self.ulds[4].plotULD()
        # self.ulds[5].plotULD()


