import csv
from heuristics.solver2_withSpaceDefrag import Solver2
from utils.inputGetter import getPackages, getULD
from utils.cartons import cartons
from LPP.carton_to_package import sol_to_package
from utils.containers import containers, containers_specific, containers_specific_multiple
from LPP.model import all_swaps as solver
from LPP.package_to_carton import get_from_greedy, get_specific_from_greedy, get_specific_from_greedy_multi
from binsearch.binsearch import binsearch
from utils.lpp_utils import are_cubes_intersecting, is_box_inside_container, plot
from utils.metrics import metrics, uldPlot
from utils.updatePackages import updatePackages





k = 5000
ulds = []
packages = []



def generateOutput(packages):
    cost = 0
    packages.sort(key=lambda x: (str(x.ULD), list(x.position)))
    priority_containers = set()
    for package in packages:
        if str(package.ULD) == "-1":
            cost += package.cost
        elif package.cost > 10000:
            priority_containers.add(package.ULD)
    cost += len(priority_containers)*5000
    f = open(f"{cost}.csv", mode="w")
    outputCSV = csv.writer(f)

    for package in packages:
        outputCSV.writerow(
            [package.id, package.ULD, package.position, package.getDimensions(), package.weight, package.cost,
             package.rotation, package.priority])

getPackages(packages)
getULD(ulds)

def run_all(ulds, packages):
    solver2 = Solver2(packages,ulds)
    solver2.solve()

    updatePackages(packages,packages,ulds)
    generateOutput(packages)

    metrics(packages,ulds,k)
    cartonss = cartons()
    containerss = containers()


    binsearchSolution = binsearch(packageArray=packages, uldArray=ulds, timeout=1, packageNum=5)
    newPackages = sol_to_package(binsearchSolution)


    updatePackages(packages,newPackages,ulds)  
    generateOutput(packages)

    metrics(packages,ulds,k)
    solution = binsearchSolution

    for uld in reversed(ulds[5:]):
        init,cartonss,assigned_solutions,_ = get_specific_from_greedy(uld.id,packageArray=packages)
        containerss = containers_specific(uld.id)
        solution = solver(cartons=cartonss, containers=containerss, init=init, assigned_solutions=assigned_solutions,timeout=60)
        temp = sol_to_package(solution)
        updatePackages(packages,temp,ulds)

    generateOutput(sol_to_package(solution))
    finalsol = sol_to_package(solution)


    updatePackages(packages,finalsol,ulds)
        


    generateOutput(packages)
    metrics(packages,ulds,k)
    # uldPlot(ulds)
    # package array plot here
