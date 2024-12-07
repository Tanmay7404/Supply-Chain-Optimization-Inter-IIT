import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from utils.structs import getCube

def uldPlot(ulds):
    

    fig = plt.figure(figsize=(10, 10))
    idx = 0
    for uld in ulds:
        ax = fig.add_subplot(math.ceil(len(ulds) / 3), 3, idx + 1, projection='3d')
        idx += 1
        ax.set_title(f"ULD {uld.id}")
        ax.set_xlim(0, uld.length)
        ax.set_ylim(0, uld.width)
        ax.set_zlim(0, uld.height)
        v, e, f = getCube(np.array([[0, uld.length], [0, uld.width], [0, uld.height]]))
        ax.add_collection3d(Poly3DCollection([v[f_] for f_ in f], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))
        for package in uld.packages:
            x, y, z = package.position[0], package.position[1], package.position[2]
            dx, dy, dz = package.dimensions[0], package.dimensions[1], package.dimensions[2]
            v, e, f = getCube(np.array([[x, x + dx], [y, y + dy], [z, z + dz]]))
            ax.plot(*v.T, marker='o', color='k', ls='')
            for i, j in e:
                ax.plot(*v[[i, j], :].T, color='r', ls='-')
                ax.add_collection3d(
                    Poly3DCollection([v[i] for i in f], facecolors='green', linewidths=1, edgecolors='r', alpha=.25))
    plt.tight_layout()
    plt.show()


def calculateCost(packages, ulds, k):
    cost = 0
    for package in packages:
        if str(package.ULD) == '-1': cost+=package.cost
    # print("Cost without accounting for priority uld (k) = ", cost)
    for uld in ulds:
        if uld.isPriority: cost+=k
    
    # print(" Total Cost = ", cost)
    return cost



def metrics(packages, ulds,k):


    packagesTotal = 0
    packagesPriority = 0
    packagesEconomy = 0
    packagesTotalTaken = 0
    packagesPriorityTaken = 0
    packagesEconomyTaken = 0

    for package in packages:
        packagesTotal+=1
        if str(package.ULD) != '-1': packagesTotalTaken+=1
        if package.priority == "Priority":
            packagesPriority+=1
            if str(package.ULD) != '-1': packagesPriorityTaken+=1
        else:
            packagesEconomy+=1
            if str(package.ULD) != '-1': packagesEconomyTaken+=1

    print("{0} out of {1} packages taken".format(packagesTotalTaken,packagesTotal))
    print("{0} out of {1} priority packages taken".format(packagesPriorityTaken,packagesPriority))
    print("{0} out of {1} economy packages taken".format(packagesEconomyTaken,packagesEconomy))

    for uld in ulds:
        uld.checkStability()
    
    
    cost = 0
    for package in packages:
        if str(package.ULD) == '-1': cost+=package.cost
    print("Cost without accounting for priority uld (k) = ", cost)
    for uld in ulds:
        if uld.isPriority: cost+=k
    
    print(" Total Cost = ", cost)
    return cost
