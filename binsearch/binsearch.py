import csv
from math import floor
import time
from binsearch.model_binsearch import container_loading_with_relative_constraints as solver
from utils.lpp_utils import are_cubes_intersecting, is_box_inside_container, plot
from LPP.carton_to_package import sol_to_package
from LPP.package_to_carton import make_solution

def package_csv_to_sol(filename):
    """
    Reads a CSV file containing package information and converts it into a solution format.
    Args:
        filename (str): The path to the CSV file containing package data.
    Returns:
        list: A list of solutions generated from the package data.
    The CSV file is expected to have the following columns:
        - Column 0: Package ID
        - Column 1: Package Type
        - Column 2: Package Dimensions (as a string representation of a list)
        - Column 3: Package Weight (as a string representation of a list)
        - Column 4: Destination
        - Column 5: Origin
        - Column 6: Additional Information
    The function reads each row from the CSV file, creates a `Package` object using the data,
    and then generates a solution for each package using the `make_solution` function.
    """

    import csv
    from utils.structs import CartonPackage as Package
    import ast
    packages = []
    sol = []
    ULDS = ["U1", "U2", "U3", "U4", "U5", "U6"]
    with open(filename, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:
                package = Package(row[0], row[1], ast.literal_eval(row[2]), ast.literal_eval(row[3]), row[4], row[5],
                                  row[6])
                sol.append(make_solution(package))
    return sol

file_path = 'output.csv'
# get_containers()

def binsearch(file_path = None, packageArray = None, uldArray = None, timeout = 30, time_split_1 = 6000):

    def get_more_packages(file_path = None, packageArray = None, uldArray = None):

        """
            Processes packages and containers to optimize package assignments.
            Args:
                file_path (str, optional): Path to the CSV file containing package data.
                packageArray (list, optional): List of package objects.
                uldArray (list, optional): List of container objects.
            Returns:
                tuple: A tuple containing:
                    - old_new_cartons (list): List of new cartons before sorting.
                    - new_cartons (list): List of new cartons after sorting.
                    - containers (list): List of containers with updated free space.
                    - new_solution (list): List of new solutions (currently empty).
                    - container_wise_solution (dict): Dictionary mapping container IDs to their respective solutions.
                    - same_assignment_cartons (list): List of container IDs with the same assignment.
                    - extra_fitted_cartons (list): List of IDs of extra fitted cartons.
            """
        
        new_cartons = []
        containers = []
        new_solution = []
        container_wise_solution = {}
        container_assigned = []
        same_assignment_cartons = []
        extra_fitted_cartons = []
        cost_reduction = 0

        # creating container objects and adding to list
        for container in uldArray:
            container = {
                "id": container.id,
                "length": container.length,
                "width": container.width,
                "height": container.height,
                "weight": container.weight_limit
            }
            container['free_space'] = container['length'] * container['width'] * container['height']
            same_assignment_cartons.append(container['id'])
            containers.append(container)
        

        container_assigned = {container['id']: [] for container in containers}
        container_lists = {container['id']: [] for container in containers}

        if file_path:
            soln=package_csv_to_sol(file_path)
            packageArray=sol_to_package(soln)

        for package in packageArray:
            package.dimensions = package.getDimensions()
            
            """If the package is not assigned to any container, add it to the new_cartons list."""

            if (package.ULD == -1 or package.ULD == '-1'):
                new_package = {
                        'id': package.id,
                        'length': package.dimensions[0],
                        'width': package.dimensions[1],
                        'height': package.dimensions[2],
                        'weight': package.weight,
                        'cost': package.cost,
                        'priority': package.priority
                    }
                new_cartons.append(new_package)
            else:

                """If the package is assigned to a container, add it to the container_assigned list."""

                new_package = {
                    "id": package.id,
                    "length": package.dimensions[0],
                    "width": package.dimensions[1],
                    "height": package.dimensions[2],
                    "weight": package.weight,
                    "cost": package.cost,
                    "priority": package.priority
                }
                container_assigned[package.ULD].append(new_package)
                for container in containers:
                    if container['id'] == package.ULD:
                        container['free_space'] -= package.dimensions[0] * package.dimensions[1] * package.dimensions[2]
        old_new_cartons = new_cartons

        # sort based on a metric to get those cartons first that have a higher chance of getting assigned
        
        new_cartons = sorted(new_cartons, key=lambda x: (floor((x['length']*x['width']*x['height'])/100),-x['cost'],min(x['length'],x['width'],x['height']),x['weight']))
        new_cartons = new_cartons[:]

        # get the original solution for each container to be used in the solver 

        for container in container_assigned:    
            original_solution = []
            for package in packageArray:
                if package.ULD != container:
                    continue
                package.dimensions = package.getDimensions()
                original_solution.append({
                    "carton_id": package.id,
                    "container_id": package.ULD,
                    "x": package.position[0],
                    "y": package.position[1],
                    "z": package.position[2],
                    "DimX": package.dimensions[0],
                    "DimY": package.dimensions[1],
                    "DimZ": package.dimensions[2],
                    "weight": package.weight,
                    "cost": package.cost,
                    "priority": package.priority
                })
            container_wise_solution[container] = original_solution

        x=0
        prev = [-1] * len(new_cartons)
        ind=0
        counter=0
        for i in new_cartons:                   # iterate over all cartons to try to fit them to containers
            containers=sorted(containers,key=lambda x: x['free_space'])         # sort containers based on free space
            for container in containers:                    
                starttime = time.time()
                container_assigned[container['id']].append(i)                   # temporarily add carton to container 
                obtained_solution = solver(container_assigned[container['id']], [container], timeout)
                if obtained_solution:
                    # if the carton fits in the container, add it to the container_lists and update the free space of the container
                    x+=1
                    extra_fitted_cartons.append(i['id'])                                    # keep track of new cartons added
                    container_lists[container['id']].append(i)  
                    cost_reduction += i['cost']                                             # update cost reduction
                    container['free_space'] -= i['length'] * i['width'] * i['height']       # update free space
                    print()
                    print()
                    print("------------------")
                    print("------------------")
                    print(i["id"])
                    print(container['id'])
                    print("------------------")
                    print("------------------")
                    print()
                    print()
                    print("###")
                    print("###")
                    current_container = obtained_solution[0]['container_id']
                    container_wise_solution[current_container] = obtained_solution
                    break
                else:                # infeasible solution is found, remove added from container
                    container_assigned[container['id']].pop()

                counter+=(time.time()-starttime)

            prev[ind]=x
            if((ind>=3 and prev[ind]==prev[ind-3]) or time_split_1<=counter):
                break
            ind+=1

        for container_id, packages in container_lists.items():
            print(f"Container {container_id} contains packages: {packages}")


        print(cost_reduction)
        return old_new_cartons, new_cartons, containers, new_solution, container_wise_solution, same_assignment_cartons, extra_fitted_cartons

    old_new_cartons, new_cartons, containers, new_solution, container_wise_solution, same_assignment_cartons, extra_fitted_cartons = get_more_packages(file_path, packageArray, uldArray)
    print("done")

    added_cartons = {}
    for every_container in container_wise_solution:
        print("Container ", every_container, "was modified")
        same_assignment_cartons.remove(every_container)
        added_cartons[every_container] = 1
        for assignment in container_wise_solution[every_container]:
            new_solution.append(assignment)

    # update the solution with the new cartons that are not assigned to any container
    for carton in old_new_cartons:
        if carton['id'] in extra_fitted_cartons:
            continue
        carton = {
            "carton_id": carton['id'],
            "container_id": '-1',
            "x": 0,
            "y": 0,
            "z": 0,
            "DimX": carton['length'],
            "DimY": carton['width'],
            "DimZ": carton['height'],
            "weight": carton['weight'],
            "cost": carton['cost'],
            "priority": carton['priority']
        }
        new_solution.append(carton)

    return new_solution
