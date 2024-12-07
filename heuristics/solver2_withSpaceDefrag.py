import math
from utils.metrics import calculateCost
from utils.structs import Axis, calculateEuclideanDistance

class Solver2:

    #Solver Initialisation
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
    
    # SORTING FUNCTIONS
    
    # Sort Packages For Assignment. Priority Packages first, sorted by Volume and Economy Packages sorted by a cost function
    def sortPackagesAssignment(self, packages):

        priority_packages = [p for p in packages if p.priority == "Priority"]
        non_priority_packages = [p for p in packages if p.priority != "Priority"]
        
        priority_packages.sort(key=lambda x: x.getVolume(), reverse=True)
        non_priority_packages.sort(key=lambda x: x.cost**3/(x.getVolume()**2 + x.weight**2) , reverse=True)
        packages[:] = priority_packages + non_priority_packages
   
    
    # Sort Packages for Fitting. Sort by Clustered Height-Area
    def sortPackagesFitting(self, packages):
        packages.sort(key=lambda x: (math.floor(x.getDimensions()[2]/10),(x.getVolume())/(x.getDimensions()[2])), reverse=True)

    # Sort ULDs. Either Sort By Volume of Brute Force all permutations to find most optimal sorting
    permuationsAll = [[6,4,5,2,1,3],[4, 5, 6, 2, 3, 1],[6, 4, 5, 2, 3, 1],[5, 6, 4, 2, 3, 1],[4, 6, 5, 2, 3, 1],[6, 5, 4, 2, 3, 1], [5, 4, 6, 3, 2, 1], [4, 5, 6, 3, 2, 1], [6, 4, 5, 3, 2, 1], [5, 6, 4, 3, 2, 1], [4, 6, 5, 3, 2, 1], [6, 5, 4, 3, 2, 1], [5, 4, 6, 2, 1, 3], [4, 5, 6, 2, 1, 3], [6, 4, 5, 2, 1, 3], [5, 6, 4, 2, 1, 3], [4, 6, 5, 2, 1, 3], [6, 5, 4, 2, 1, 3], [5, 4, 6, 3, 1, 2], [4, 5, 6, 3, 1, 2], [6, 4, 5, 3, 1, 2], [5, 6, 4, 3, 1, 2], [4, 6, 5, 3, 1, 2], [6, 5, 4, 3, 1, 2]]
    def sortULDs(self,permutation):
        currPermutation=self.permuationsAll[permutation]
       
        if(len(self.ulds)==6):
            newUld = []
            for i in range(6):
                newUld.append(self.ulds[currPermutation[i]-1])
            self.ulds = newUld
        else:
            self.ulds.sort(key=lambda x: x.getVolume(), reverse=True)
    
    #FITTING PACKAGES

    #Try to fit given packages in a ULD by sorting extreme points by Euclidean Distance and trying to fit the package in the corner
    def fitPackages(self, packages, uld, corners, isassigning = 0):
        takenPackages = []
      
        for package in packages:            
            if str(package.ULD) == '-1': 
                done = False

                corners.sort(key=lambda corner: calculateEuclideanDistance(corner)) 
                for corner in corners:
                    if uld.addBox(package, corner):
                        # Remove this corner and add the other 7 new corners
                        corners.remove(corner)
                        new_corners = uld.getNewCorners(package)
                        corners.extend(new_corners)                        
                        takenPackages.append(package)
                        done = True
                        break

        print(len(takenPackages))        
        return corners, takenPackages
    

    #Fit packages in ULDs and Implementing Space Defragmentation by trying to replace unplaced packages in other ULDs
    def fit_into_ulds(self,packages,ulds,cornermap,mess, assigning = 0):
        takenPackages = []
        for ii,uld in enumerate(ulds):
            
            print(mess + " ULD: ", uld.id)
            [corners, taken_pck] = self.fitPackages(packages, uld, cornermap[uld.id])
            done = False
            cornermap[uld.id] = corners
            takenPackages.extend(taken_pck)
            for unpacked_package in packages:
                if str(unpacked_package.ULD) == '-1':
                    for jj in range(ii+1):
                        ulds[jj].calculatePushLimit()
                        for poss_replace in ulds[jj].packages:
                            if(ulds[jj].inflate_and_replace(unpacked_package,poss_replace)):
                                if(takenPackages.count(poss_replace) > 0):
                                    takenPackages.remove(poss_replace)
                                takenPackages.append(unpacked_package)
                                cornermap[uld.id] = ulds[jj].recalculate_corners()
                                done = True
                                break
                        if done:
                            break   
                
        return cornermap,takenPackages    
    

    #Assign Priority Packages to ULDs by trying to fit them in the ULDs. Then clearing the ULD    
    def assignPackagesPriority(self):
        ulds = self.ulds[0:len(self.ulds)]
        cm = {}
        for i in ulds:
            cm[i.id] = [[0, 0, 0]]
            print("Assigning Priorty ULD: ", i.id)
            [_, packagesInULD] = self.fitPackages(self.packages, i, [[0, 0, 0]],True)
            self.takenPackages.extend(packagesInULD)
            priority_done = True
            for pack in self.packages:
                if (pack not in self.takenPackages) and (pack.priority == "Priority"):
                    priority_done = False
                    break
            if(priority_done):
                break
        

        for uld in ulds:
            if(len(uld.packages)!=0):
                self.priorityULDs+=1
        for uld in ulds:
            uld.clearBin()

        return
    
    #Assign Normal Packages to ULDs by trying to fit them in the ULDs. Then clearing the ULD
    def assignPackagesNormal(self):
        ulds = self.ulds[self.priorityULDs:len(self.ulds)]
        for i in ulds:
            print("Assigning Normal ULD: ", i.id)
            [_, packagesInULD] = self.fitPackages(self.packages, i, [[0, 0, 0]],True)
            self.takenPackages.extend(packagesInULD)

        for uld in ulds:
            uld.clearBin()

        return
    

    #Apply Space Defragmentation and Projection to increase stability and reduce extra space, until cost is being reduced
    def defragAndProject(self):

        #Projecting Packages 
        for uld in self.ulds:
            for package in uld.packages:
                for axis in Axis.ALL:
                    if uld.project(package,axis) != -1:
                        package.position[axis] = uld.project(package,axis)
        cost = calculateCost(self.packages,self.ulds,5000)
        oldCost = 10000000000
        while cost != oldCost:
            oldCost = cost
            #Space Defragmentation
            for unpacked_package in self.packages:
                if str(unpacked_package.ULD) == '-1':
                    done = False
                    for jj in range(len(self.ulds)):
                        self.ulds[jj].calculatePushLimit()
                        for poss_replace in self.ulds[jj].packages:
                            if(self.ulds[jj].inflate_and_replace(unpacked_package,poss_replace)):
                            
                                done = True
                                break
                        if done:
                            break

            #Projecting Packages
            for uld in self.ulds:
                for axis in Axis.ALL:
                    uld.packages.sort(key=lambda x: x.position[axis])
                    for package in uld.packages:
                        if uld.projectFinal(package,axis) != -1:
                            package.position[axis] = uld.projectFinal(package,axis)

            cost = calculateCost(self.packages,self.ulds,5000)

    

    def solve(self):
        
        #Sort the packages in the order we want to assign them
        self.sortPackagesAssignment(self.packages)
        
        #Sort ULDS in appropriate Order
        self.sortULDs(0)

        #Assign Packages to Priority ULDs
        self.assignPackagesPriority()

        #CornerMap maintains list of extreme points of each ULDs, initialised from origin [0,0,0]
        cornermap = {}
        for uld in self.ulds:
            cornermap[uld.id] = [[0, 0, 0]]

        #Assigned Packages are fitted in the ULDs sorted by the fitting order
        self.sortPackagesFitting(self.takenPackages)
        [cornermap,_] = self.fit_into_ulds(self.takenPackages, self.ulds, cornermap,"Fitting Proirity")
       
        #Assigning Packages to the remaining ULDS, higher cost first
        self.takenPackages = []
        self.assignPackagesNormal()

        #Assigened Packages are sorted by fitting order and fitted in the ULDs
        self.sortPackagesFitting(self.takenPackages)
        [cornermap,_] = self.fit_into_ulds(self.takenPackages, self.ulds, cornermap,"Fitting Normal")

        #Unassigned Packages are then tried to fit into the ULDs
        self.sortPackagesFitting(self.packages)
        [cornermap,_] = self.fit_into_ulds(self.packages, self.ulds, cornermap,"Fitting Remaining")


        #Applying Space Defragmentation and Projection 
        self.defragAndProject()
        
