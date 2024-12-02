from utils.structs import Axis

def updatePackages(packages,newPackages,ulds):
    for package in packages:
        for finalpackage in newPackages:
            if package.id == finalpackage.id:
                package.ULD = finalpackage.ULD if finalpackage.ULD != '-1' else -1
                package.position = finalpackage.position
                package.dimensions = finalpackage.dimensions
                package.rotation = -1
                break


    for uld in ulds:
        for package in uld.packages:
            for axis in Axis.ALL:
                if uld.project(package,axis) != -1:
                    package.position[axis] = uld.project(package,axis)