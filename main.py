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
from utils.metrics import metrics, uldPlot
from utils.updatePackages import updatePackages
import sys
import time






def generateOutput(packages):
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

    #from timeout, choose 4 parameters, time for 1st MIP, time for 2nd MIP, number of cartons in 1st MIP, number of ULDs in 2nd MIP
    #timeout = t1*6*c1 + t2*u2

    solver2 = Solver2(packages,ulds)
    solver2.solve()

    updatePackages(packages,packages,ulds)
    generateOutput(packages)

    metrics(packages,ulds,k)
    cartonss = cartons()
    containerss = containers()

    time_split_1 = min(1500,timeout/2)
    if time_split_1 < 450:
        bin_timeout = 15
    elif time_split_1 < 900:
        bin_timeout = 20
    else:
        bin_timeout = 30
    if time_split_1 > 0:
        binsearchSolution = binsearch(packageArray=packages, uldArray=ulds,timeout=bin_timeout, time_split_1=time_split_1)
        newPackages = sol_to_package(binsearchSolution)


        updatePackages(packages,newPackages,ulds)  
        generateOutput(packages)

        metrics(packages,ulds,k)
        # uldPlot(ulds)
    solution = []
    time_split_2 = timeout - time_split_1
    # ulds.sort(key=lambda x: (sum(p.cost for p in x.packages))**2*(sum(p.length*p.width*p.height for p in x.packages)))
    if time_split_2 > 2:
        for uld in reversed(ulds[4:]):
            init,cartonss,assigned_solutions,_ = get_specific_from_greedy(uld.id,packageArray=packages)
            containerss = containers_specific(uld.id)
            solution = solver(cartons=cartonss, containers=containerss, init=init, assigned_solutions=assigned_solutions,timeout=time_split_2//2)
            temp = sol_to_package(solution)
            updatePackages(packages,temp,ulds)

    generateOutput(sol_to_package(solution))
    finalsol = sol_to_package(solution)


    updatePackages(packages,finalsol,ulds)
        


    # generateOutput(packages)
    cost = metrics(packages,ulds,k)
    return cost
    # uldPlot(ulds)
    # package array plot here



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

    # solution = package_csv_to_sol(filename="28462.csv")
    # newPackages = sol_to_package(solution)
    # updatePackages(packages,newPackages,ulds)
    # metrics(packages,ulds,k)
    # # cartonss = cartons()
    # # containerss = containers()
    # myuld = ulds[0]
    # for uld in ulds:
    #     if uld.id == "U3":
    #         myuld = uld
    #         break
    # init,cartonss,assigned_solutions,_ = get_specific_from_greedy([myuld.id],packageArray=packages)
    # containerss = containers_specific(myuld.id)
    # solution = solver(cartonss, containerss, init, assigned_solutions,timeout=1000000)
    # temp = sol_to_package(solution)
    # updatePackages(packages,temp,ulds)
    # generateOutput(packages)
    # metrics(packages,ulds,k)

    run_all(ulds, packages,timeout)
