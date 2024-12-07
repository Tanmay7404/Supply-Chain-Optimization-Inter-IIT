import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from utils.structs import getCube

def uldPlot(ulds):
    """
    Plots 3D visualizations of Unit Load Devices (ULDs) and their packages.
    Parameters:
    ulds (list): A list of ULD objects. Each ULD object should have the following attributes:
        - id (str): Identifier for the ULD.
        - length (float): Length of the ULD.
        - width (float): Width of the ULD.
        - height (float): Height of the ULD.
        - packages (list): A list of package objects. Each package object should have the following attributes:
            - position (tuple): A tuple (x, y, z) representing the position of the package within the ULD.
            - dimensions (tuple): A tuple (dx, dy, dz) representing the dimensions of the package.
    Returns:
    None
    This function creates a 3D plot for each ULD in the input list. Each ULD is plotted in a separate subplot
    within a single figure. The ULDs are represented as cyan-colored cuboids, and the packages within each ULD
    are represented as green-colored cuboids. The edges of the cuboids are highlighted in red.
    """
    

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
    """
    Calculate the total cost of packages and priority ULDs.
    This function computes the total cost by summing the costs of packages that are not assigned to any ULD 
    (indicated by ULD value '-1') and adding a fixed cost 'k' for each priority ULD.
    Args:
        packages (list): A list of package objects, where each package has attributes 'ULD' and 'cost'.
        ulds (list): A list of ULD (Unit Load Device) objects, where each ULD has an attribute 'isPriority'.
        k (int): The fixed cost added for each priority ULD.
    Returns:
        int: The total calculated cost.
    """

    cost = 0
    for package in packages:
        if str(package.ULD) == '-1': cost+=package.cost
    # print("Cost without accounting for priority uld (k) = ", cost)
    for uld in ulds:
        if uld.isPriority: cost+=k
    
    # print(" Total Cost = ", cost)
    return cost



def metrics(packages, ulds,k):

    """
    Calculate and print various metrics related to package handling and ULD (Unit Load Device) stability.
    Args:
        packages (list): A list of package objects. Each package object should have attributes 'ULD', 'priority', and 'cost'.
        ulds (list): A list of ULD objects. Each ULD object should have methods 'checkStability()' and an attribute 'isPriority'.
        k (int): The cost associated with priority ULDs.
    Returns:
        int: The total cost after accounting for priority ULDs.
    This function performs the following tasks:
    1. Counts the total number of packages, priority packages, and economy packages.
    2. Counts the number of packages taken, priority packages taken, and economy packages taken.
    3. Prints the counts of packages taken out of the total packages, priority packages, and economy packages.
    4. Checks the stability of each ULD.
    5. Calculates and prints the cost without accounting for priority ULDs.
    6. Adds the cost associated with priority ULDs to the total cost and prints the total cost.
    """


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
