from utils.structs import Axis

def updatePackages(packages,newPackages,ulds):
    def updatePackages(packages, newPackages, ulds):
        """
        Update the list of packages with new package information and adjust their positions within ULDs (Unit Load Devices).
        Args:
            packages (list): A list of current package objects.
            newPackages (list): A list of new package objects with updated information.
            ulds (list): A list of ULD objects.
        The function performs the following steps:
        1. Updates the attributes of packages in the `packages` list with the corresponding attributes from `newPackages`.
        2. Adds packages to the appropriate ULD's package list if they are not already present.
        3. Removes packages from ULDs if their ULD attribute is set to '-1'.
        4. Attempts to replace unpacked packages (ULD attribute is '-1') into ULDs by inflating and replacing existing packages.
        5. Sorts the packages within each ULD based on their position along each axis and adjusts their positions using the `projectFinal` method.
        """

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

    for unpacked_package in packages:
        if str(unpacked_package.ULD) == '-1':
            done = False
            for jj in range(6):
                ulds[jj].calculatePushLimit()
                for poss_replace in ulds[jj].packages:
                    if(ulds[jj].inflate_and_replace(unpacked_package,poss_replace,lpp=True)):
                       
                        done = True
                        break
                if done:
                    break   


    for uld in ulds:
        for axis in Axis.ALL:
            uld.packages.sort(key=lambda x: x.position[axis])
            for package in uld.packages:
                if uld.projectFinal(package,axis) != -1:
                    package.position[axis] = uld.projectFinal(package,axis)