import csv


def generateOutput(packages):
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
    f = open(f"output.csv", mode="w", newline='\n')
    outputCSV = csv.writer(f)

    outputCSV.writerow([int(cost),numPackages,len(priority_containers)])
    for package in packages:
        corner = package.position
        package.getDimensions()
        othercorner = [package.position[0] + package.dimensions[0], package.position[1] + package.dimensions[1],package.position[2] + package.dimensions[2]]
        othercorner = [int(x) for x in othercorner]
        corner = [int(x) for x in corner]
        if str(package.ULD) == "-1":
            corner = [-1,-1,-1]
            othercorner = [-1,-1,-1]
        uld = package.ULD if str(package.ULD) != "-1" else 'NONE'
        outputCSV.writerow(
            [package.id, uld, corner[0], corner[1], corner[2], othercorner[0], othercorner[1], othercorner[2]])
