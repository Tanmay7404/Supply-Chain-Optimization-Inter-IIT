import math

def calculateEuclideanDistance(self, point):
        return math.sqrt(point[0] ** 2 + point[1] ** 2 + point[2] ** 2)


#Always LWH is default unless specified otherwise

def isIntersecting(package1,package2,x,y):
    d1 = package1.getDimensions()
    d2 = package2.getDimensions()

    cx1 = package1.position[x] + d1[x]/2
    cy1 = package1.position[y] + d1[y]/2
    cx2 = package2.position[x] + d2[x]/2
    cy2 = package2.position[y] + d2[y]/2

    ix = max(cx1, cx2) - min(cx1, cx2)
    iy = max(cy1, cy2) - min(cy1, cy2)

    return ix < (d1[x]+d2[x])/2 and iy < (d1[y]+d2[y])/2



class Rotation:
    LWH = 0
    LHW = 1
    WLH = 2
    WHL = 3
    HLW = 4
    HWL = 5

    ALL = [LWH,LHW,WLH,WHL,HLW,HWL]
 
class Axis:
    LENGTH = 0
    WIDTH = 1
    HEIGHT = 2

    ALL = [LENGTH, WIDTH, HEIGHT]

class Package:

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

    def getMaxBase(self):
        #already sorted
        return self.length*self.width

    def getVolume(self):
        return self.length*self.width*self.height
    

    def isIntersecting(self,other):
        return (isIntersecting(self,other,Axis.LENGTH,Axis.WIDTH) 
                and isIntersecting(self,other,Axis.HEIGHT,Axis.WIDTH)
                and isIntersecting(self,other,Axis.LENGTH,Axis.HEIGHT))


    def getDimensions(self):
        dim = []
        if self.rotation == Rotation.LWH: dim = [self.length,self.width,self.height]
        if self.rotation == Rotation.WLH: dim = [self.width,self.length,self.height]
        if self.rotation == Rotation.HLW: dim = [self.height,self.length,self.width]
        if self.rotation == Rotation.HWL: dim = [self.height,self.width,self.length]
        if self.rotation == Rotation.LHW: dim = [self.length,self.height,self.width]
        if self.rotation == Rotation.WHL: dim = [self.width,self.height,self.length]

        return dim

    def getCenterOfMass(self):
        return [self.position[0] + self.length/2, self.position[1] + self.width/2, self.position[2] + self.height/2]
    
class ULD:
    def __init__(self,length,width,height,weight_limit,id):
        self.length = int(length)
        self.width = int(width)
        self.height = int(height)
        self.weight_limit = int(weight_limit)
        self.id = id
        self.isPriority = False
        self.packages = []
    
    def weightLeft(self):
        curr = self.weight_limit
        for package in self.packages: curr-=package.weight
        return curr
    
    def getVolume(self):
        return self.length*self.width*self.height

    def addBox(self, currPackage, pivot, rotations = Rotation.ALL):
        prevPosition = currPackage.position
        currPackage.position = pivot
        valid = False
        if (self.weightLeft() < currPackage.weight) : 
            return valid
        
        bestRot = -1;
        minEucDist = 10000;

        for rotation in rotations:
            currPackage.rotation = rotation
            dimensions = currPackage.getDimensions()
            if (
                self.length < pivot[0] + dimensions[0] or
                self.width < pivot[1] + dimensions[1] or
                self.height < pivot[2] + dimensions[2] or
                pivot[0] < 0 or pivot[1] < 0 or pivot[2] < 0
            ): continue
            else : 
                if(minEucDist>calculateEuclideanDistance(self,[pivot[0] + dimensions[0],pivot[1] + dimensions[1], pivot[2] + dimensions[2]])) :
                    bestRot = rotation
                    continue

        if(bestRot != -1) : 
            valid = True
            currPackage.rotation = bestRot

        valid = True

        for package in self.packages:
            if package.isIntersecting(currPackage):
                valid = False
                break

        if valid:
            #check for stability?
            #update uld criteria if needed for solver
            currPackage.ULD = self.id
            #do we need to deepcopy this?
            self.packages.append(currPackage)
            if(currPackage.priority == "Priority"): self.isPriority = True
            return valid
            
        currPackage.position = prevPosition
        return valid
    
    def getNewCorners(self,package,corner):
        dimensions = package.getDimensions()
        new_corners = [
            [corner[0] + dimensions[0], corner[1], corner[2]],
            [corner[0], corner[1] + dimensions[1], corner[2]],
            [corner[0], corner[1], corner[2] + dimensions[2]],
            [corner[0] + dimensions[0], corner[1] + dimensions[1], corner[2]],
            [corner[0] + dimensions[0], corner[1], corner[2] + dimensions[2]],
            [corner[0], corner[1] + dimensions[1], corner[2] + dimensions[2]],
            [corner[0] + dimensions[0], corner[1] + dimensions[1], corner[2] + dimensions[2]]
        ]
        return new_corners

    def clearBin(self):
        for package in self.packages:
            package.ULD = -1
            package.position = [-1,-1,-1]
        self.packages = []
        self.isPriority = False
    


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