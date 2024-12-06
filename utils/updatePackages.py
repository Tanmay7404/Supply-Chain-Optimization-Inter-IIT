from utils.structs import Axis

def updatePackages(packages,newPackages,ulds):
    for package in packages:
        for finalpackage in newPackages:
            if package.id == finalpackage.id:
                package.ULD = finalpackage.ULD
                if str(package.ULD) != '-1':
                    for uld in ulds:
                        if uld.id == package.ULD and package not in uld.packages:
                            uld.packages.append(package)
                package.position = finalpackage.position
                package.dimensions = finalpackage.dimensions
                package.rotation = -1
                break


    for uld in ulds:
        newpackages = [package for package in uld.packages if package.ULD == uld.id]
        uld.packages = newpackages
        for axis in Axis.ALL:
            uld.packages.sort(key=lambda x: x.position[axis])
            for package in uld.packages:
                if uld.projectFinal(package,axis) != -1:
                    package.position[axis] = uld.projectFinal(package,axis)