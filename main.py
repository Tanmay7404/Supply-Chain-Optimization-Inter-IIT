import csv
from heuristics.solver2_withSpaceDefrag import Solver2
from utils.inputGetter import getPackages, getULD
from utils.cartons import cartons
from LPP.carton_to_package import sol_to_package
from utils.containers import containers, containers_specific, containers_specific_multiple
from LPP.model import all_swaps as solver, complete_LPP
from LPP.package_to_carton import get_from_greedy, get_specific_from_greedy, get_specific_from_greedy_multi, package_csv_to_sol
from binsearch.binsearch import binsearch
from utils.lpp_utils import are_cubes_intersecting, is_box_inside_container, plot
from utils.metrics import calculateCost, metrics, uldPlot
from utils.updatePackages import updatePackages
import sys
import time



def generateOutput(packages):
    """
    Generates an output CSV file with package details and calculates the total cost.
    Args:
        packages (list): A list of package objects. Each package object must have the attributes:
                         - id: Identifier of the package.
                         - ULD: Unit Load Device identifier.
                         - position: Position of the package.
                         - getDimensions(): Method to get the dimensions of the package.
                         - weight: Weight of the package.
                         - cost: Cost associated with the package.
                         - rotation: Rotation of the package.
                         - priority: Priority status of the package.
    The function performs the following steps:
    1. Sorts the packages based on ULD and position.
    2. Calculates the total cost, adding a fixed amount for priority containers.
    3. Writes the package details to a CSV file named with the total cost.
    4. Calls the generateFinalOutput function to perform further processing.
    """
    
    cost = 0
    packages.sort(key=lambda x: (str(x.ULD), list(x.position)))
    priority_containers = set()
    for package in packages:
        if str(package.ULD) == "-1":
            cost += package.cost
        elif int(package.cost) > 10000:
            priority_containers.add(package.ULD)
    cost += len(priority_containers)*5000
    f = open(f"{cost}.csv", mode="w")
    outputCSV = csv.writer(f)

    for package in packages:
        outputCSV.writerow(
            [package.id, package.ULD, package.position, package.getDimensions(), package.weight, package.cost,
             package.rotation, package.priority])
    generateFinalOutput(packages)



def generateFinalOutput(packages):
    """
    Generates the final output CSV file with package details and calculates the total cost.
    Args:
        packages (list): A list of package objects. Each package object should have the following attributes:
            - ULD (str or int): Unit Load Device identifier. If ULD is "-1", the package is considered unassigned.
            - cost (int): The cost associated with the package.
            - position (list): A list of three integers representing the position of the package.
            - id (int): The unique identifier of the package.
            - getDimensions (method): A method that sets the dimensions attribute of the package.
    The function performs the following steps:
        1. Sorts the packages based on ULD and position.
        2. Calculates the total cost by summing the cost of unassigned packages and adding a fixed cost for priority containers.
        3. Writes the total cost, number of packages, and number of priority containers to a CSV file.
        4. Writes the details of each package to the CSV file, including the package ID, ULD, and corner positions.
    """

    
    cost = 0
    packages.sort(key=lambda x: (str(x.ULD), list(x.position)))
    priority_containers = set()
    numPackages = len(packages)
    for package in packages:
        if str(package.ULD) == "-1":
            cost += package.cost
            numPackages -= 1
        elif int(package.cost) > 10000:
            priority_containers.add(package.ULD)
    cost += len(priority_containers)*5000
    f = open(f"finalOutput.csv", mode="w", newline='\n')
    outputCSV = csv.writer(f)

    outputCSV.writerow([int(cost),numPackages,len(priority_containers)])
    for package in packages:
        corner = package.position
        package.getDimensions()
        othercorner = [package.position[0] + package.dimensions[0], package.position[1] + package.dimensions[1],package.position[2] + package.dimensions[2]]
        if str(package.ULD) == "-1":
            corner = [-1,-1,-1]
            othercorner = [-1,-1,-1]
        uld = package.ULD if str(package.ULD) != "-1" else 'NONE'
        outputCSV.writerow(
            [package.id, uld, corner[0], corner[1], corner[2], othercorner[0], othercorner[1], othercorner[2]])

def run_all(ulds, packages,timeout = 300, stabilityThreshold = 0.5, k = 5000):

    """
    Executes the optimization process for loading packages into ULDs (Unit Load Devices).
    Args:
        ulds (list): List of ULD objects representing the containers.
        packages (list): List of package objects to be loaded into ULDs.
        timeout (int, optional): Total time allowed for the optimization process. Defaults to 300 seconds.
        stabilityThreshold (float, optional): Threshold for stability in the optimization process. Defaults to 0.5.
        k (int, optional): Parameter for the cost calculation. Defaults to 5000.
    Returns:
        float: The final cost after the optimization process.
    The function performs the following steps:
    1. Initializes the solver with the given packages and ULDs.
    2. Updates the packages and generates the initial output.
    3. Calculates and prints the initial metrics.
    4. Performs a binary search optimization if the initial time split is greater than 0.
    5. Iteratively updates the packages and recalculates the cost until it stabilizes.
    6. If the remaining time is sufficient, performs further optimization on specific ULDs.
    7. Generates the final output and returns the final cost.
    """


    solver2 = Solver2(packages,ulds)
    solver2.solve()

    updatePackages(packages,packages,ulds)
    generateOutput(packages)

    metrics(packages,ulds,k)
    cartonss = cartons()
    containerss = containers()

    time_split_1 = min(0,timeout/50)
    bin_timeout = 0.1
    if time_split_1 > 0:
        binsearchSolution = binsearch(packageArray=packages, uldArray=ulds,timeout=bin_timeout, time_split_1=time_split_1)
        newPackages = sol_to_package(binsearchSolution)


        updatePackages(packages,newPackages,ulds)  
        generateOutput(packages)

        metrics(packages,ulds,k)
        # uldPlot(ulds)
    solution = []
    time_split_2 = timeout - time_split_1
    cost = calculateCost(packages,ulds,5000)
    oldCost = 10000000000
    while cost != oldCost:
        oldCost = cost
        updatePackages(packages,packages,ulds)
        cost = calculateCost(packages,ulds,5000)
        print(cost,oldCost)
    if time_split_2 > 2:
        num_uld = 2
        if time_split_2 >= 600:
            num_uld = 3
        if time_split_2 >= 1200:
            num_uld = 4
        if time_split_2 >= 1800:
            num_uld = 5
        if time_split_2 >= 2400:
            num_uld = 6

        for uld in reversed(ulds[len(ulds)-num_uld:]):
            init,cartonss,assigned_solutions,_ = get_specific_from_greedy(uld.id,packageArray=packages)
            containerss = containers_specific(uld.id)
            solution = solver(cartons=cartonss, containers=containerss, init=init, assigned_solutions=assigned_solutions,timeout=time_split_2//num_uld)
            temp = sol_to_package(solution)
            updatePackages(packages,temp,ulds)
            cost = calculateCost(packages,ulds,5000)
            oldCost = 10000000000
            while cost != oldCost:
                oldCost = cost
                updatePackages(packages,packages,ulds)
                cost = calculateCost(packages,ulds,5000)
                print(cost,oldCost)

    generateOutput(sol_to_package(solution))
    finalsol = sol_to_package(solution)


    updatePackages(packages,finalsol,ulds)
        
    cost = calculateCost(packages,ulds,5000)
    oldCost = 10000000000
    while cost != oldCost:
        oldCost = cost
        updatePackages(packages,packages,ulds)
        cost = calculateCost(packages,ulds,5000)
        print(cost,oldCost)
    return cost



# To get the solution without running the streamlit app

if __name__ == "__main__":
    timeout = 300
    if len(sys.argv) > 2:
        print("Usage: python main.py <timeout>")
        sys.exit(1)
    if len(sys.argv) == 2:
        timeout = int(sys.argv[1])

    k = 5000
    ulds = []
    packages = []
    getPackages(packages)
    getULD(ulds)

    run_all(ulds, packages,timeout)
