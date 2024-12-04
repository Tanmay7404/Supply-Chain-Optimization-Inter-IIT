import csv
from heuristics.solver2_withSpaceDefrag import Solver2
from utils.inputGetter import getPackages, getULD
from utils.cartons import cartons
from LPP.carton_to_package import sol_to_package
from utils.containers import containers, containers_specific
from LPP.model import all_swaps as solver
from LPP.package_to_carton import get_from_greedy, get_specific_from_greedy
from binsearch.binsearch import binsearch
from utils.lpp_utils import are_cubes_intersecting, is_box_inside_container, plot
from utils.metrics import metrics, uldPlot, metrics_test,metrics_test_print
from utils.updatePackages import updatePackages





k = 5000
ulds = []
packages = []



def generateOutput(packages):
    f = open("output.csv", mode="w")
    outputCSV = csv.writer(f)
    packages.sort(key=lambda x: (str(x.ULD),list(x.position)))
    for package in packages:
        outputCSV.writerow([package.id,package.ULD,package.position,package.getDimensions(),package.weight,package.cost,package.rotation,package.priority])

def run_tester():
    for i in range(1,11):
        packagest = []
        uldst = []
        getULD(uldst)
        getPackages(packagest,test=True,idx=i)
        solver2 = Solver2(packagest,uldst)
        solver2.solve()
        metrics_test(uldst,packagest)
        print(f"Test {i} done")

    getPackages(packages)
    getULD(ulds)

    solver2 = Solver2(packages,ulds)
    solver2.solve()
    metrics_test(ulds,packages)
    metrics_test_print("file_name")

getPackages(packages)
getULD(ulds)

solver2 = Solver2(packages,ulds)
solver2.solve()

generateOutput(packages)

metrics(packages,ulds,k)
cartons = cartons()
containerss = containers()


binsearchSolution = binsearch(packageArray=packages, uldArray=ulds, timeout=30,packageNum=10)
newPackages = sol_to_package(binsearchSolution)



updatePackages(packages,newPackages,ulds)  
generateOutput(packages)

metrics(packages,ulds,k)
# uldPlot(ulds)
solution = binsearchSolution

for uld in reversed(ulds[5:]):
    init,cartons,assigned_solutions,_ = get_specific_from_greedy(uld.id,packageArray=packages)
    containerss = containers_specific(uld.id)
    solution = solver(cartons=cartons, containers=containerss, init=init, assigned_solutions=assigned_solutions,timeout=600)
    temp = sol_to_package(solution)
    updatePackages(packages,temp,ulds)

generateOutput(sol_to_package(solution))
finalsol = sol_to_package(solution)


updatePackages(packages,finalsol,ulds)
    


generateOutput(packages)
metrics(packages,ulds,k)
uldPlot(ulds)
# package array plot here
