

# Strategy:
# greedily pack the boxes into the ULDs
# sort the ULDs by volume
# sort the boxes by volume
# sort the boxes by priority
# pack the boxes in the ULDs

class Solver:
    
    def __init__(self,packages,ulds):
        self.packages = packages
        self.ulds = ulds
        self.priorityDone = 0
        self.priority = []
        self.economy = []
        self.takenPackages = []

        for package in packages:
            if package.priority == "Priority":
                self.priority.append(package)
            else:
                self.economy.append(package)

    def sortPackages(self):
        self.takenPackages.sort(key=lambda x:
                        (x.priority,x.getVolume())
                                 ,reverse=True)

    def sortULDs(self):
        self.ulds.sort(key=lambda x: x.getVolume(),reverse=True)

    def selectPackages(self):
        self.takenPackages = self.priority + self.economy

    def solve(self):
        self.selectPackages()
        self.sortPackages()
        self.sortULDs()

        for uld in self.ulds:
            print("Considering ULD: ",uld.id)
            corners = [[0,0,0]]
            for package in self.takenPackages:
                if package.ULD == -1: 
                    done = False
                    for corner in corners:
                        if(uld.addBox(package,corner)):
                            #remove this corner and add the other 7 corner 
                            corners.remove(corner)
                            new_corners = uld.getNewCorners(package, corner)
                            corners.extend(new_corners)
                            # corners.sort(key=lambda x: x[0])
                            # corners.sort(key=lambda x: x[1])
                            corners.sort(key=lambda x: x[2])
                            done = True
                            break
                    if done and package.priority == "Priority":
                        self.priorityDone+=1

