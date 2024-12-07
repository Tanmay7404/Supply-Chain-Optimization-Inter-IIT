import csv
from heuristics.solver2_withSpaceDefrag import Solver2
from utils.generateOutput import generateOutput
from utils.inputGetter import getPackages, getULD
from utils.cartons import cartons
from MIP1.carton_to_package import sol_to_package
from utils.containers import containers, containers_specific, containers_specific_multiple
from MIP1.model import all_swaps as solver, complete_LPP
from MIP1.package_to_carton import get_from_greedy, get_specific_from_greedy, get_specific_from_greedy_multi, package_csv_to_sol
from MIP2.binsearch import binsearch
from utils.metrics import calculateCost, metrics, uldPlot
from utils.updatePackages import updatePackages
import sys
import time




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
    cost = calculateCost(packages,ulds,5000)
    oldCost = 10000000000
    while cost != oldCost:
        oldCost = cost
        updatePackages(packages,packages,ulds)
        cost = calculateCost(packages,ulds,5000)
        print(cost,oldCost)
    time_split_1 = min(100,timeout/5)
    bin_timeout = 5
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
    print("----------------------------------------------------------------------------")
    print("Successfully Ran the Optimization Process, check output.csv for the results")
    print("Final Cost: ",cost)
    print("----------------------------------------------------------------------------")
    return cost




#Running using command line
if __name__ == "__main__":
    timeout = 300 #default timeout
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
