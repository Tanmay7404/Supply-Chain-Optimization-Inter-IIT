# cartons = cartons()
# containerss = containers()


# binsearchSolution = binsearch(packageArray=packages, uldArray=ulds, timeout=45)
# newPackages = sol_to_package(binsearchSolution)



# updatePackages(packages,newPackages,ulds)  
# generateOutput(packages)

# metrics(packages,ulds,k)
# uldPlot(ulds)
# solution = binsearchSolution

# for uld in reversed(ulds):
#     init,cartons,assigned_solutions = get_specific_from_greedy(uld.id,packageArray=packages)
#     containerss = containers_specific(uld.id)
#     solution = solver(cartons=cartons, containers=containerss, init=init, assigned_solutions=assigned_solutions,timeout=900)
#     temp = sol_to_package(solution)
#     updatePackages(packages,temp,ulds)

# generateOutput(sol_to_package(solution))
# finalsol = sol_to_package(solution)


# updatePackages(packages,finalsol,ulds)
    


# generateOutput(packages)
# metrics(packages,ulds,k)