import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

#CONTAIN CLASSES FOR PACKAGES AND ULDs ALONG WITH UTILITY CLASSES (ROTATION, AXIS) AND FUNCTIONS


def calculateEuclideanDistance(point):
    return math.sqrt(point[0] ** 2 + point[1] ** 2 + point[2] ** 2)

#Check Instersection of two packages along a particular axis
def isIntersecting(package1,package2,d1,d2,x):

    x1 = package1.position[x]
    x2 = x1+d1[x]
    x3 = package2.position[x]
    x4 = x3+d2[x]

    return max(x1,x3) < min(x2,x4)

#Get the overlap of two rectangles
def getOverlap(rect1,rect2):
    x1 = max(rect1[0],rect2[0])
    x2 = min(rect1[2],rect2[2])
    y1 = max(rect1[1],rect2[1])
    y2 = min(rect1[3],rect2[3])
    return max(0,x2-x1)*max(0,y2-y1)


#get the vertices, edges, and faces of a cuboid defined by its limits
def getCube(limits = None):
    if limits is None:
        limits = np.array([[0, 1], [0, 1], [0, 1]])
    v = np.array([[x, y, z] for x in limits[0] for y in limits[1] for z in limits[2]])
    e = np.array([[0, 1], [1, 3], [3, 2], [2, 0],
                  [4, 5], [5, 7], [7, 6], [6, 4],
                  [0, 4], [1, 5], [2, 6], [3, 7]])
    f = np.array([[0, 1, 3, 2], [4, 5, 7, 6],
                  [0, 1, 5, 4], [2, 3, 7, 6],
                  [0, 2, 6, 4], [1, 3  , 7, 5]])
    

    return v, e, f


#Class for Rotation of a package
class Rotation:
    LWH = 0
    LHW = 1
    WLH = 2
    WHL = 3
    HLW = 4
    HWL = 5

    ALL = [LWH,LHW,WLH,WHL,HLW,HWL]

 
#Class for Axis of a package
class Axis:
    LENGTH = 0
    WIDTH = 1
    HEIGHT = 2

    ALL = [HEIGHT, WIDTH, LENGTH]


#Package Class
class Package:

    #Initialisation Function for a Package
    def __init__(self, length, width, height, weight,id,priority,cost = 10000000):
        self.position = [-1,-1,-1] #default if not placed
        self.ULD = -1 #default when ULD not chosen
        self.length = int(length)
        self.width = int(width)
        self.height = int(height)
        [self.length,self.width,self.height] = sorted([self.length,self.width,self.height])
        self.weight = int(weight)
        self.id = id
        self.priority = priority
        self.cost = int(cost)
        self.rotation = Rotation.LWH
        self.pqPriority = 0
        self.stable = True
        self.pushLim = [-1,-1,-1]
        self.dimensions = [self.length,self.width,self.height]

    #Get the Base Area of the Package
    def getMaxBase(self):
        return self.length*self.width

    #Get the Volume of the Package
    def getVolume(self):
        return self.length*self.width*self.height
    
    #Check if the package is intersecting with another package
    def isIntersecting(self,other):
        d1 = self.getDimensions()
        d2 = other.getDimensions()
        return (isIntersecting(self,other,d1,d2,0) and isIntersecting(self,other,d1,d2,1) and isIntersecting(self,other,d1,d2,2))

    #Get Dimensions Based on Rotation
    def getDimensions(self):
        dim = []
        if self.rotation == -1: return self.dimensions
        if self.rotation == Rotation.LWH: dim = [self.length,self.width,self.height]
        if self.rotation == Rotation.WLH: dim = [self.width,self.length,self.height]
        if self.rotation == Rotation.HLW: dim = [self.height,self.length,self.width]
        if self.rotation == Rotation.HWL: dim = [self.height,self.width,self.length]
        if self.rotation == Rotation.LHW: dim = [self.length,self.height,self.width]
        if self.rotation == Rotation.WHL: dim = [self.width,self.height,self.length]

        self.dimensions = dim

        return dim
    
    #Get the Center of Mass of the Package
    def getCenterOfMass(self):
        return [self.position[0] + self.length/2, self.position[1] + self.width/2, self.position[2] + self.height/2]
    

#ULD CLASS   
class ULD:

    #Initialisation Function for a ULD
    def __init__(self,length,width,height,weight_limit,id):
        self.length = int(length)
        self.width = int(width)
        self.height = int(height)
        self.weight_limit = int(weight_limit)
        self.id = id
        self.isPriority = False
        self.packages = []
    
    #Get the Weight Left in the ULD before exceeding Weight Limit
    def weightLeft(self):
        curr = self.weight_limit
        for package in self.packages: curr-=package.weight
        return curr
    
    #Get the Volume of the ULD
    def getVolume(self):
        return self.length*self.width*self.height
    
    #Get the Weight Limit of the ULD
    def getWeight(self):
        return self.weight_limit
    
    #Clear the ULD of all Packages
    def clearBin(self):
        for package in self.packages:
            package.ULD = -1
            package.position = [-1,-1,-1]
        self.packages = []
        self.isPriority = False

    #Plot the ULD packages in 3D
    def plotULD(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim([0,self.length])
        ax.set_ylim([0,self.width])
        ax.set_zlim([0,self.height])
        for package in self.packages:
            [x,y,z] = package.position
            [dx,dy,dz] = package.getDimensions()
            v,e,f = getCube(np.array([[x,x+dx],[y,y+dy],[z,z+dz]]))
            ax.plot(*v.T, marker='o', color='k', ls='')
            for i, j in e:
                ax.plot(*v[[i, j], :].T, color='r', ls='-')
            for i in f:
                if package.stable == -1:
                    ax.add_collection3d(Poly3DCollection([v[i]], facecolors='red', linewidths=1, edgecolors='r', alpha=.25))
                elif package.stable:
                    ax.add_collection3d(Poly3DCollection([v[i]], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))
                else:
                    ax.add_collection3d(Poly3DCollection([v[i] for i in f], facecolors='green', linewidths=1, edgecolors='r', alpha=.25))
        plt.show()

    #INSERTION

    #Add a Package to the ULD
    def addBox(self, currPackage, pivot, rotations = Rotation.ALL):
        prevPosition = currPackage.position
        currPackage.position = list(pivot)

        # Check weight limits
        if self.weightLeft() < currPackage.weight:
            currPackage.position = prevPosition
            return False

        for rotation in rotations:
            currPackage.rotation = rotation
            dimensions = currPackage.getDimensions()

            # Check boundary limits
            if (
                pivot[0] + dimensions[0] > self.length or
                pivot[1] + dimensions[1] > self.width or
                pivot[2] + dimensions[2] > self.height
            ):
                continue

	        # Check for intersections
            if any(package.isIntersecting(currPackage) for package in self.packages):
                continue
        
            for axis in Axis.ALL:
                project = self.project(currPackage,axis)
                if project != -1:
                    currPackage.position[axis] = project

            
            currPackage.ULD = self.id
            self.packages.append(currPackage)
            if(currPackage.priority == "Priority"): self.isPriority = True
            return True
        
        currPackage.position = prevPosition
        return False
    
    
    
    #Get the New Extreme Points of the ULD after adding a Package, by projecting 3 corners of the package along the 3 axes
    def getNewCorners(self,package):
        extreme_points = set()

        [x, y, z] = package.position
        [dx, dy, dz] = package.getDimensions()
        L = self.length
        W = self.width
        H = self.height

        def project_along_axis(fixed_axis, variable_axis1, variable_axis2,x1,y1,z1):
            
            if fixed_axis == "x":
                fd = 0
                fixed, dim, limit = x1, dx, L
                var1, var2 = y1, z1
            elif fixed_axis == "y":
                fd = 1
                fixed, dim, limit = y1, dy, W
                var1, var2 = x1, z1
            elif fixed_axis == "z":
                fd = 2
                fixed, dim, limit = z1, dz, H
                var1, var2 = x1, y1
            else:
                raise ValueError("Invalid axis!")

           
            max_extent =  0

            for pkg in self.packages:
                
                px, py, pz = pkg.position
                pdx,pdy,pdz = pkg.getDimensions()

                pkg_min = {"x": px, "y": py, "z": pz}
                pkg_max = {"x": px + pdx, "y": py + pdy, "z": pz + pdz}

                if pkg_min[variable_axis1] <= var1 < pkg_max[variable_axis1] and \
                pkg_min[variable_axis2] <= var2 < pkg_max[variable_axis2]:
                    if pkg_max[fixed_axis] <= fixed:
                        max_extent = max(max_extent, pkg_max[fixed_axis])
            return max_extent

        
        ex1 = project_along_axis("x", "y", "z", x,y+dy,z)  
        extreme_points.add((ex1, y+dy, z))

        ez1 = project_along_axis("z", "x", "y", x,y+dy,z)  
        extreme_points.add((x, y+dy, ez1))          

        ex2 = project_along_axis("x", "y", "z", x,y,z+dz)  
        extreme_points.add((ex2, y,z+dz))

        ey1 = project_along_axis("y", "z", "x", x,y,z+dz)  
        extreme_points.add((x,ey1,z+dz))     

        ey2 = project_along_axis("y", "z", "x", x+dx,y,z)  
        extreme_points.add((x+dx,ey2,z))

        ez2 = project_along_axis("z", "x", "y", x+dx,y,z)  
        extreme_points.add((x+dx, y, ez2))     

        extreme_points.add((x+dx,y,z))
        extreme_points.add((x,y+dy,z))
        extreme_points.add((x,y,z+dz))
        
        return extreme_points
    

    #STABILITY CHECKS

    #Check if a Package is Stable in the ULD by checking overlap of its base with other packages
    def checkStabilityPackage(self, package, minOverlapReq = 0.5):
        packageDimensions = package.getDimensions()
        packageRectangle = [package.position[0],package.position[1],package.position[0]+packageDimensions[0],package.position[1]+packageDimensions[1]]
        packageBase = package.position[2]
        packageBaseArea = packageDimensions[0]*packageDimensions[1]
        maxOverlap = 0
        for otherPackage in self.packages:
            if package == otherPackage: continue
            otherPackageDimensions = otherPackage.getDimensions()
            if packageBase != otherPackage.position[2] + otherPackageDimensions[2]: continue
            otherPackageRectangle = [otherPackage.position[0],otherPackage.position[1],otherPackage.position[0]+otherPackageDimensions[0],otherPackage.position[1]+otherPackageDimensions[1]]
            maxOverlap += getOverlap(packageRectangle,otherPackageRectangle)
        
        maxOverlap = maxOverlap/packageBaseArea
        if package.position[2] == 0:
            package.stable = True
            return True
        if maxOverlap == 0:
            package.stable = -1
            return False
        if (
            package.position[0] == 0 or
            package.position[1] == 0 or
            package.position[0] + package.getDimensions()[0] == self.length or
            package.position[1] + package.getDimensions()[1] == self.width
        ):
            package.stable = True
            return True
        if maxOverlap < minOverlapReq:
            package.stable = False
            return False
        package.stable = True
        return True
    
    #Get stability of the ULD by checking stability of all packages
    def checkStability(self, minOverlapReq = 0.5, unstableAllowed = 0):    
        numUnstable = 0
        totalPackages = len(self.packages)

        for package in self.packages:
            for otherPackage in self.packages:
                if package == otherPackage: continue
                if package.isIntersecting(otherPackage):
                    print("Package ",package.id," is intersecting with ",otherPackage.id)
                    print("Coordinates ",package.position)
                    print("Dimensions ",package.getDimensions())
                    print("Coordinates ",otherPackage.position)
                    print("Dimensions ",otherPackage.getDimensions())
                    

        for package in self.packages:
            if not self.checkStabilityPackage(package, minOverlapReq):
                numUnstable+=1
        print("ULD ",self.id," has ",numUnstable,"out of ",totalPackages," unstable packages")
        return (numUnstable <= unstableAllowed)

    #Get Centre of Mass of ULD by averaging the Centre of Mass of all packages
    def getLoadCenterOfMass(self):
        x = 0
        y = 0
        z = 0
        for package in self.packages:
            com = package.getCenterOfMass()
            weight = package.weight
            x+=com[0]*weight
            y+=com[1]*weight
            z+=com[2]*weight
        totalWeight = sum([package.weight for package in self.packages])
        return [x/totalWeight,y/totalWeight,z/totalWeight]
    
    
    #PROJECT ALONG ORIGIN TO INCREASE STABILITY

    def project(self, package, axis = Axis.HEIGHT):
        maxxx = -1
        axis1 = (axis+1)%3
        axis2 = (axis+2)%3
        packageDimensions = package.getDimensions()
        packageRectangle = [package.position[axis1],package.position[axis2],package.position[axis1]+packageDimensions[axis1],package.position[axis2]+packageDimensions[axis2]]
        for otherPackage in self.packages:
            otherPackageDimensions = otherPackage.getDimensions()
            otherPackageRectangle = [otherPackage.position[axis1],otherPackage.position[axis2],otherPackage.position[axis1]+otherPackageDimensions[axis1],otherPackage.position[axis2]+otherPackageDimensions[axis2]]
            if (package.position[axis] >= otherPackage.position[axis]+ otherPackageDimensions[axis]):
                if (getOverlap(packageRectangle,otherPackageRectangle) > 0):
                    maxxx = max(maxxx,otherPackage.position[axis]+otherPackageDimensions[axis])
        return maxxx    
    
    def projectFinal(self, package, axis = Axis.HEIGHT):
        maxxx = 0
        axis1 = (axis+1)%3
        axis2 = (axis+2)%3
        packageDimensions = package.getDimensions()
        packageRectangle = [package.position[axis1],package.position[axis2],package.position[axis1]+packageDimensions[axis1],package.position[axis2]+packageDimensions[axis2]]
        for otherPackage in self.packages:
            otherPackageDimensions = otherPackage.getDimensions()
            otherPackageRectangle = [otherPackage.position[axis1],otherPackage.position[axis2],otherPackage.position[axis1]+otherPackageDimensions[axis1],otherPackage.position[axis2]+otherPackageDimensions[axis2]]
            if (package.position[axis] >= otherPackage.position[axis]+ otherPackageDimensions[axis]):
                if (getOverlap(packageRectangle,otherPackageRectangle) > 0):
                    maxxx = max(maxxx,otherPackage.position[axis]+otherPackageDimensions[axis])
        return maxxx   
    

    #SPACE DEFRAGMENTATION FUNCTIONS

    # Calculate the amount a package can be pushed in each direction without ever intersecting with any other package
    def calculatePushLimit(self):
        for i in range(3):
            sortedPos = []
            for j in self.packages:
                sortedPos.append([j.position[i],1,j])
                dim = j.getDimensions()[i]
                sortedPos.append([j.position[i]+dim,0,j])

            sortedPos.sort(key=lambda x: (x[0], x[1]), reverse=True)
            
            x0 = self.length
            if(i==1):
                x0 = self.width
            elif(i==2):
                x0 = self.height
            for j in sortedPos:
                if(j[1]==1):
                    x0 = min(x0,j[0] + j[2].pushLim[i])
                else:
                    j[2].pushLim[i] = x0 - j[0]
        
    
    #Push out the packages beyond x,y,z in the ULD to make space for a new package according to their PushLim
    def pushOut(self,x,y,z):
        for i in self.packages:
            if(i.position[0]>=x):
                i.position[0]+= i.pushLim[0]
            if(i.position[1]>=y):
                i.position[1]+= i.pushLim[1]
            if(i.position[2]>=z):
                i.position[2]+= i.pushLim[2]
    
    #Normalize the ULD back after PushOut when finished inerting a package
    def normalize(self):
        packages = self.packages
        moved = True

        while moved:
            moved = False

            for axis in range(3):
        
                packages.sort(key=lambda package: package.position[axis])

                for i, package in enumerate(packages):
                    # Find the minimum position the packet can move to along the current axis
                    min_position = 0

                    for j in range(i):
                        op = packages[j].position
                        pp = package.position
                        od = packages[j].getDimensions()
                        pd = package.getDimensions()

                        # Ensure no overlap: check the other two axes
                        a1 = (axis+1)%3
                        a2 = (axis+2)%3
                        if(((pp[a1]+pd[a1]<=op[a1]) or (op[a1]+od[a1]<=pp[a1])) and ((pp[a2]+pd[a2]<=op[a2]) or (op[a2]+od[a2]<=pp[a2]))):
                            continue
                            # No overlap, update minimum position if needed
                        min_position = max(min_position, op[axis] + od[axis])

                    # Move the packet if possible
                    if package.position[axis] > min_position:
                        package.position[axis] = min_position
                        moved = True

    #Recalculate the Extreme Points of the ULD after Normalising
    def recalculate_corners(self):
        corners = []
        corners.append((0,0,0))
        for i in self.packages:
            corners.extend(self.getNewCorners(i))

        return corners
            
    #Replace a Higher Cost, Higher Volume unplaced package with a packed package, by pushing out other packages and normalising back
    def inflate_and_replace(self,pck,rep,lpp = False):

        if(pck.priority != rep.priority):
            return False
        if(pck.cost < rep.cost):
            return False
        if((not lpp)and(pck.getVolume() < rep.getVolume())):
            return False
        
        currpack = self.packages.copy()

        self.packages.remove(rep)

        if(self.pushAddBox(pck,rep.position)):
            rep.ULD = -1
            rep.pos = [-1,-1,-1]
            rep.pushLim = [-1,-1,-1]
            self.packages.remove(pck)
            for i,p in enumerate(currpack):
                if(p == rep):
                    currpack[i] = pck
                    break
            self.packages = currpack
            # print("YAYY")
            return True
        
        self.packages = currpack
        return False
    

    #Check is its possible to insert a package at a pivot point by pushing all other boxes as far as possible
    def pushAddBox(self, currPackage, pivot, rotations = Rotation.ALL):
        prevPosition = currPackage.position
        currPackage.position = list(pivot)
        valid = False
        if (self.weightLeft() < currPackage.weight) : 
            return valid
        for rotation in rotations:
            currPackage.rotation = rotation
            dimensions = currPackage.getDimensions()
            if (
                self.length < pivot[0] + dimensions[0] or
                self.width < pivot[1] + dimensions[1] or
                self.height < pivot[2] + dimensions[2] or
                pivot[0] < 0 or pivot[1] < 0 or pivot[2] < 0
            ): continue
           
            valid = True

            for pck in self.packages:
                
                pos = pck.position.copy()
                if(pck.position[0]>=pivot[0]):
                    pck.position[0] = pck.position[0] + pck.pushLim[0]
                if(pck.position[1]>=pivot[1]):
                    pck.position[1] = pck.position[1] + pck.pushLim[1]
                if(pck.position[2]>=pivot[2]):
                    pck.position[2] = pck.position[2] + pck.pushLim[2]
                    
                if pck.isIntersecting(currPackage):
                    pck.position = pos
                    valid = False
                    break
                pck.position = pos

            if valid:
                self.pushOut(pivot[0],pivot[1],pivot[2])
                currPackage.ULD = self.id
                self.packages.append(currPackage)
                self.normalize()

                if(currPackage.priority == "Priority"): self.isPriority = True
                return valid                           
                
        currPackage.position = prevPosition
        return valid



# Package Class for MIPSolver
class CartonPackage:
    
    def __init__(self, id, uldid, position, dimensions, weight, cost, rotation):
        self.id = id
        self.ULD = uldid
        self.position = position
        self.dimensions = dimensions
        self.weight = weight
        self.cost = cost
        self.rotation = rotation
        self.priority = 1 if uldid == "priority" else 0
    
    def getDimensions(self):
        return self.dimensions