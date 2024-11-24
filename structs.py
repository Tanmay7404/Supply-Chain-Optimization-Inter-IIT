


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
    WLH = 1
    HLW = 2
    HWL = 3
    LHW = 4
    WHL = 5

    ALL = [LWH,WLH,HLW,HWL,LHW,WHL]
 
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
        self.weight = int(weight)
        self.id = id
        self.priority = priority
        self.cost = int(cost)
        self.rotation = Rotation.LWH

    #to sort by cost
    def __lt__(self,other):
        return self.cost<other.cost

    def getVolume(self):
        return self.length*self.height*self.height
    

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

    
class ULD:
    def __init__(self,length,width,height,weight_limit,id):
        self.length = int(length)
        self.width = int(width)
        self.height = int(height)
        self.weight_limit = int(weight_limit)
        self.id = id
        self.packages = []
    
    def weightLeft(self):
        curr = self.weight_limit
        for package in self.packages: curr-=package.weight
        return curr
    
    def addBox(self, currPackage, pivot, rotations = Rotation.ALL):
        prevPosition = currPackage.position
        currPackage.position = pivot
        valid = False
        if (self.weightLeft() < currPackage.weight) : 
            return valid
        for rotation in rotations:
            currPackage.rotation = rotation
            dimensions = currPackage.getDimensions()
            if (
                self.length < pivot[0] + dimensions[0] or
                self.width < pivot[1] + dimensions[1] or
                self.height < pivot[2] + dimensions[2]
            ): continue

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
                return valid
            
        currPackage.position = prevPosition
        return valid
    
    def clearBin(self):
        self.packages = []
    
