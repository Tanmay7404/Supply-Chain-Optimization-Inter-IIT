from utils.structs import Axis

def updatePackages(packages,newPackages,ulds):
    for package in packages:
        for finalpackage in newPackages:
            if package.id == finalpackage.id:
                if package.position != finalpackage.position and (package.ULD != -1 or finalpackage.ULD != -1):
                    print(package.id,package.position,finalpackage.position)
                package.ULD = finalpackage.ULD if (finalpackage.ULD != '-1' and finalpackage.ULD != -1) else -1
                if package.ULD != -1:
                    for uld in ulds:
                        if uld.id == package.ULD and package not in uld.packages:
                            uld.packages.append(package)
                package.position = finalpackage.position
                package.dimensions = finalpackage.dimensions
                package.rotation = -1
                break


    for uld in ulds:
        for package in uld.packages:
            if package.ULD != uld.id:
                uld.packages.remove(package)
            else:
                for axis in Axis.ALL:
                    if uld.project(package,axis) != -1:
                        package.position[axis] = uld.project(package,axis)