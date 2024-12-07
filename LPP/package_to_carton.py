def get_from_greedy(filename = None, packageArray = None):
    """
    Generates an initial solution for package placement using a greedy approach.
    This function reads package data from a CSV file or a provided package array, 
    and generates initial placement and orientation information for each package 
    in a set of predefined ULDs (Unit Load Devices).
    Args:
        filename (str, optional): The path to the CSV file containing package data. 
                                    If None, packageArray must be provided.
        packageArray (list, optional): A list of Package objects. If None, filename must be provided.
    Returns:
        dict: A dictionary containing the initial solution with the following keys:
            - 'sij': A dictionary indicating whether a package is in a specific ULD.
            - 'xi': A dictionary with the x-coordinates of each package.
            - 'yi': A dictionary with the y-coordinates of each package.
            - 'zi': A dictionary with the z-coordinates of each package.
            - 'relative_position': A dictionary indicating the relative positions of packages.
            - 'orientation': A dictionary indicating the orientation of each package.
    Raises:
        ValueError: If both filename and packageArray are None.
    Notes:
        - The function assumes that the CSV file has the following columns:
            id, ULD, dimensions, position, and other relevant fields.
        - The dimensions and positions are expected to be in a specific format 
            that can be evaluated using ast.literal_eval.
    """
    import csv
    from utils.structs import CartonPackage as Package
    import ast
    packages = []
    ULDS = ["U1", "U2", "U3", "U4", "U5", "U6"]
    if filename is None:
        packages = packageArray
    else:
        with open(filename, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                package = Package(row[0], row[1], ast.literal_eval(row[2]), ast.literal_eval(row[3]), row[4], row[5],
                                row[6])
                packages.append(package)

    initialsij = {}
    for package in packages:
        for uld in ULDS:
            initialsij[(package.id, uld)] = 0
            if package.ULD == uld:
                initialsij[(package.id, uld)] = 1
    initialxi = {}
    initialyi = {}
    initialzi = {}
    for package in packages:
        package.dimensions = package.getDimensions()
        # print(package.id, package.position[0])
        initialxi[package.id] = package.position[0]
        initialyi[package.id] = package.position[1]
        initialzi[package.id] = package.position[2]
        if package.position[0] == -1:
            initialxi[package.id] = 0
            initialyi[package.id] = 0
            initialzi[package.id] = 0
    initialrelative_position = {}
    for package in packages:
        for other_package in packages:
            if package.id >= other_package.id:
                continue
            dict = {}
            if package.ULD != other_package.ULD :
                dict["aik"] = 0
                dict["bik"] = 0
                dict["cik"] = 0
                dict["dik"] = 0
                dict["eik"] = 0
                dict["fik"] = 0
                initialrelative_position[(package.id, other_package.id)] = dict
                continue

            if (package.position[0] + package.dimensions[0] <= other_package.position[0]):
                dict["aik"] = 1
                dict["bik"] = 0
            elif (package.position[0] >= other_package.position[0] + other_package.dimensions[0]):
                dict["aik"] = 0
                dict["bik"] = 1
            else:
                dict["aik"] = 0
                dict["bik"] = 0
            if (package.position[1] + package.dimensions[1] <= other_package.position[1]):
                dict["cik"] = 1
                dict["dik"] = 0
            elif (package.position[1] >= other_package.position[1] + other_package.dimensions[1]):
                dict["cik"] = 0
                dict["dik"] = 1
            else:
                dict["cik"] = 0
                dict["dik"] = 0
            if (package.position[2] + package.dimensions[2] <= other_package.position[2]):
                dict["eik"] = 1
                dict["fik"] = 0
            elif (package.position[2] >= other_package.position[2] + other_package.dimensions[2]):
                dict["eik"] = 0
                dict["fik"] = 1
            else:
                dict["eik"] = 0
                dict["fik"] = 0
            initialrelative_position[(package.id, other_package.id)] = dict

    initialorientation = {}
    for package in packages:
        [len, wid, hei] = sorted([package.dimensions[0], package.dimensions[1], package.dimensions[2]])
        dict = {}

        if len == package.dimensions[0] and wid == package.dimensions[1] and hei == package.dimensions[2]:
            dict["lx"] = 1
            dict["ly"] = 0
            dict["lz"] = 0
            dict["wx"] = 0
            dict["wy"] = 1
            dict["wz"] = 0
            dict["hx"] = 0
            dict["hy"] = 0
            dict["hz"] = 1
        elif len == package.dimensions[0] and wid == package.dimensions[2] and hei == package.dimensions[1]:
            dict["lx"] = 1
            dict["ly"] = 0
            dict["lz"] = 0
            dict["wx"] = 0
            dict["wy"] = 0
            dict["wz"] = 1
            dict["hx"] = 0
            dict["hy"] = 1
            dict["hz"] = 0
        elif len == package.dimensions[1] and wid == package.dimensions[0] and hei == package.dimensions[2]:
            dict["lx"] = 0
            dict["ly"] = 1
            dict["lz"] = 0
            dict["wx"] = 1
            dict["wy"] = 0
            dict["wz"] = 0
            dict["hx"] = 0
            dict["hy"] = 0
            dict["hz"] = 1
        elif len == package.dimensions[1] and wid == package.dimensions[2] and hei == package.dimensions[0]:
            dict["lx"] = 0
            dict["ly"] = 1
            dict["lz"] = 0
            dict["wx"] = 0
            dict["wy"] = 0
            dict["wz"] = 1
            dict["hx"] = 1
            dict["hy"] = 0
            dict["hz"] = 0
        elif len == package.dimensions[2] and wid == package.dimensions[0] and hei == package.dimensions[1]:
            dict["lx"] = 0
            dict["ly"] = 0
            dict["lz"] = 1
            dict["wx"] = 1
            dict["wy"] = 0
            dict["wz"] = 0
            dict["hx"] = 0
            dict["hy"] = 1
            dict["hz"] = 0
        else:
            dict["lx"] = 0
            dict["ly"] = 0
            dict["lz"] = 1
            dict["wx"] = 0
            dict["wy"] = 1
            dict["wz"] = 0
            dict["hx"] = 1
            dict["hy"] = 0
            dict["hz"] = 0
        initialorientation[package.id] = dict
    # print sij,xi,yi,zi,relative_position,orientation for 2 packages
    package1 = packages[-1]
    package2 = packages[-2]
    initial_solution = {'sij': initialsij, 'xi': initialxi, 'yi': initialyi, 'zi': initialzi,
                        'relative_position': initialrelative_position, 'orientation': initialorientation}
    return initial_solution
def make_carton(package):
    """
    Converts a package object into a carton dictionary with sorted dimensions.
    Args:
        package (object): An object representing a package with attributes:
            - dimensions (list): A list of three dimensions [length, width, height].
            - id (str): The unique identifier of the package.
            - weight (float): The weight of the package.
            - priority (int): The priority level of the package.
            - cost (float): The cost associated with the package.
            - ULD (str): The container ID for the package.
    Returns:
        dict: A dictionary representing the carton with the following keys:
            - id (str): The unique identifier of the package.
            - length (float): The smallest dimension of the package.
            - width (float): The middle dimension of the package.
            - height (float): The largest dimension of the package.
            - weight (float): The weight of the package.
            - Priority (int): The priority level of the package.
            - cost (float): The cost associated with the package.
            - container_id (str): The container ID for the package.
    """

    v = [float(package.dimensions[0]), float(package.dimensions[1]), float(package.dimensions[2])]
    v.sort()
    carton = {
        "id": package.id,
        "length": float(v[0]),
        "width": float(v[1]),
        "height": float(v[2]),
        "weight": float(package.weight),
        "Priority": package.priority,
        "cost": float(package.cost),
        "container_id": package.ULD
    }
    return carton


def make_solution(package):
    """
    Converts a package object into a solution dictionary with position and dimension details.
    Args:
        package (object): An object representing a package with attributes:
            - dimensions (list): A list of three dimensions [length, width, height].
            - position (list): A list of three coordinates [x, y, z].
            - id (str): The unique identifier of the package.
            - weight (float): The weight of the package.
            - priority (int): The priority level of the package.
            - cost (float): The cost associated with the package.
            - ULD (str): The container ID for the package.
    Returns:
        dict: A dictionary representing the solution with the following keys:
            - carton_id (str): The unique identifier of the package.
            - x (float): The x-coordinate of the package.
            - y (float): The y-coordinate of the package.
            - z (float): The z-coordinate of the package.
            - DimX (float): The smallest dimension of the package.
            - DimY (float): The middle dimension of the package.
            - DimZ (float): The largest dimension of the package.
            - weight (float): The weight of the package.
            - Priority (int): The priority level of the package.
            - cost (float): The cost associated with the package.
            - container_id (str): The container ID for the package.
    """
    v = [float(package.dimensions[0]), float(package.dimensions[1]), float(package.dimensions[2])]
    x = float(package.position[0])
    y = float(package.position[1])
    z = float(package.position[2])
    container_id = package.ULD
    carton = {
        "carton_id": package.id,
        "x": x,
        "y": y,
        "z": z,
        "DimX": float(v[0]),
        "DimY": float(v[1]),
        "DimZ": float(v[2]),
        "weight": float(package.weight),
        "Priority": package.priority,
        "cost": float(package.cost),
        "container_id": package.ULD
    }
    return carton

def are_base_area_intersecting(package1, package2):
    """
    Determines if the base areas of two packages are intersecting.
    Args:
        package1: An object representing the first package, which has 'position' and 'dimensions' attributes.
                  'position' is a tuple (x, y) representing the bottom-left corner of the package.
                  'dimensions' is a tuple (width, height) representing the size of the package.
        package2: An object representing the second package, which has 'position' and 'dimensions' attributes.
                  'position' is a tuple (x, y) representing the bottom-left corner of the package.
                  'dimensions' is a tuple (width, height) representing the size of the package.
    Returns:
        bool: True if the base areas of the two packages intersect, False otherwise.
    The function checks if the base areas of two packages overlap by comparing their positions and dimensions.
    """

    if package1.position[0] + package1.dimensions[0] <= package2.position[0] or package2.position[0] + package2.dimensions[0] <= package1.position[0]:
        return False
    if package1.position[1] + package1.dimensions[1] <= package2.position[1] or package2.position[1] + package2.dimensions[1] <= package1.position[1]:
        return False
    return True


def get_specific_from_greedy( container_ids, filename= None, packageArray = None):

    import csv
    from utils.structs import CartonPackage as Package
    import ast
    packages = []
    rem_packages = []
    specific_packages = []
    ULDS = ["U1", "U2", "U3", "U4", "U5", "U6"]
    if filename is None:
        packages = packageArray
    else:
        with open(filename, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row:
                    f = 1
                else:
                    continue
                package = Package(row[0], row[1], ast.literal_eval(row[2]), ast.literal_eval(row[3]), row[4], row[5],
                                row[6])
                packages.append(package)

    initialsij = {}
    Pcij = {}
    wi = {}
    wij = {}
    pos = []
    cartons = []
    assigned_solutions = []
    for package in packages:
        if package.ULD == "-1" or package.ULD == -1:
            cartons.append(make_carton(package))
            pos.append(package)
        elif package.ULD in container_ids:
            cartons.append(make_carton(package))
            pos.append(package)
        else:
            assigned_solutions.append(make_solution(package))
        if str(package.ULD) not in container_ids and str(package.ULD) != "-1":
            continue
        for uld in ULDS:
            if uld not in container_ids:
                continue
            initialsij[(package.id, uld)] = 0
            if package.ULD == uld:
                initialsij[(package.id, uld)] = 1

    initialxi = {}
    initialyi = {}
    initialzi = {}

    for container_id in container_ids:
        for package1 in pos:
            for package2 in pos:
                if package1.id == package2.id:
                    continue
                Pcij[(package1.id, package2.id, container_id)] = 0
                wij[(package1.id, package2.id)] = 0
                if package1.ULD != package2.ULD or package1.ULD != container_id:
                    continue
                Pcij[(package1.id, package2.id, container_id)] = 1
                if are_base_area_intersecting(package1, package2) and package1.position[2] == package2.position[2] + package2.dimensions[2]:
                        wij[(package1.id, package2.id)] = 1


    for package in pos:
        # print(package.id, package.position[0])
        initialxi[package.id] = package.position[0]
        initialyi[package.id] = package.position[1]
        initialzi[package.id] = package.position[2]
        wi[package.id] = 0
        if package.position[2] == 0:
            wi[package.id] = 1
        if package.ULD == -1 or package.ULD == "-1":
            initialxi[package.id] = 0
            initialyi[package.id] = 0
            initialzi[package.id] = 0
    initialrelative_position = {}
    for package in pos:
        for other_package in pos:
            if package.id >= other_package.id:
                continue
            dict = {}
            if package.ULD != other_package.ULD or str(package.ULD) == '-1':
                dict["aik"] = 0
                dict["bik"] = 0
                dict["cik"] = 0
                dict["dik"] = 0
                dict["eik"] = 0
                dict["fik"] = 0
                initialrelative_position[(package.id, other_package.id)] = dict
                continue

            if package.position[0] + package.dimensions[0] <= other_package.position[0]:
                dict["aik"] = 1
                dict["bik"] = 0
            elif package.position[0] >= other_package.position[0] + other_package.dimensions[0]:
                dict["aik"] = 0
                dict["bik"] = 1
            else:
                dict["aik"] = 0
                dict["bik"] = 0
            if package.position[1] + package.dimensions[1] <= other_package.position[1]:
                dict["cik"] = 1
                dict["dik"] = 0
            elif package.position[1] >= other_package.position[1] + other_package.dimensions[1]:
                dict["cik"] = 0
                dict["dik"] = 1
            else:
                dict["cik"] = 0
                dict["dik"] = 0
            if package.position[2] + package.dimensions[2] <= other_package.position[2]:
                dict["eik"] = 1
                dict["fik"] = 0
            elif package.position[2] >= other_package.position[2] + other_package.dimensions[2]:
                dict["eik"] = 0
                dict["fik"] = 1
            else:
                dict["eik"] = 0
                dict["fik"] = 0
            initialrelative_position[(package.id, other_package.id)] = dict

    initialorientation = {}
    for package in pos:
        [len, wid, hei] = sorted([package.dimensions[0], package.dimensions[1], package.dimensions[2]])
        dict = {}

        if len == package.dimensions[0] and wid == package.dimensions[1] and hei == package.dimensions[2]:
            dict["lx"] = 1
            dict["ly"] = 0
            dict["lz"] = 0
            dict["wx"] = 0
            dict["wy"] = 1
            dict["wz"] = 0
            dict["hx"] = 0
            dict["hy"] = 0
            dict["hz"] = 1
        elif len == package.dimensions[0] and wid == package.dimensions[2] and hei == package.dimensions[1]:
            dict["lx"] = 1
            dict["ly"] = 0
            dict["lz"] = 0
            dict["wx"] = 0
            dict["wy"] = 0
            dict["wz"] = 1
            dict["hx"] = 0
            dict["hy"] = 1
            dict["hz"] = 0
        elif len == package.dimensions[1] and wid == package.dimensions[0] and hei == package.dimensions[2]:
            dict["lx"] = 0
            dict["ly"] = 1
            dict["lz"] = 0
            dict["wx"] = 1
            dict["wy"] = 0
            dict["wz"] = 0
            dict["hx"] = 0
            dict["hy"] = 0
            dict["hz"] = 1
        elif len == package.dimensions[1] and wid == package.dimensions[2] and hei == package.dimensions[0]:
            dict["lx"] = 0
            dict["ly"] = 1
            dict["lz"] = 0
            dict["wx"] = 0
            dict["wy"] = 0
            dict["wz"] = 1
            dict["hx"] = 1
            dict["hy"] = 0
            dict["hz"] = 0
        elif len == package.dimensions[2] and wid == package.dimensions[0] and hei == package.dimensions[1]:
            dict["lx"] = 0
            dict["ly"] = 0
            dict["lz"] = 1
            dict["wx"] = 1
            dict["wy"] = 0
            dict["wz"] = 0
            dict["hx"] = 0
            dict["hy"] = 1
            dict["hz"] = 0
        else:
            dict["lx"] = 0
            dict["ly"] = 0
            dict["lz"] = 1
            dict["wx"] = 0
            dict["wy"] = 1
            dict["wz"] = 0
            dict["hx"] = 1
            dict["hy"] = 0
            dict["hz"] = 0
        initialorientation[package.id] = dict
    # print sij,xi,yi,zi,relative_position,orientation for 2 packages
    package1 = packages[-1]
    package2 = packages[-2]
    initial_solution = {'sij': initialsij, 'xi': initialxi, 'yi': initialyi, 'zi': initialzi,
                        'relative_position': initialrelative_position, 'orientation': initialorientation}
    stability_constraints = {'Pcij': Pcij, 'wi': wi, 'wij': wij}
    print(cartons)
    cartons.sort(key=lambda x: x['id'])
    return initial_solution, cartons, assigned_solutions, stability_constraints
def get_specific_from_greedy_multi( container_ids, filename= None, packageArray = None):

    """
    Processes packages and assigns them to cartons or solutions based on container IDs.
    This function reads package data either from a CSV file or from a provided array of packages.
    It then assigns each package to a carton or a solution based on the specified container IDs.
    Args:
        container_ids (list): A list of container IDs to filter packages.
        filename (str, optional): The path to the CSV file containing package data. Defaults to None.
        packageArray (list, optional): An array of package objects. Defaults to None.
    Returns:
        tuple: A tuple containing two lists:
            - cartons (list): A list of cartons created from the packages.
            - assigned_solutions (list): A list of solutions assigned to the packages.
    Raises:
        FileNotFoundError: If the specified CSV file does not exist.
        ValueError: If the package data in the CSV file is not in the expected format.
    Note:
        - If `filename` is provided, the function reads package data from the CSV file.
        - If `filename` is not provided, the function uses the `packageArray` for package data.
        - Packages with ULD value "-1" or not in the specified container IDs are assigned to cartons.
        - Packages with ULD value in the specified container IDs are assigned to solutions.
    """

    import csv
    from utils.structs import CartonPackage as Package
    import ast
    packages = []
    rem_packages = []
    specific_packages = []
    ULDS = ["U1", "U2", "U3", "U4", "U5", "U6"]
    if filename is None:
        packages = packageArray
    else:
        with open(filename, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row:
                    f = 1
                else:
                    continue
                package = Package(row[0], row[1], ast.literal_eval(row[2]), ast.literal_eval(row[3]), row[4], row[5],
                                row[6])
                packages.append(package)
    cartons = []
    assigned_solutions = []
    for package in packages:
        if package.ULD == "-1" or package.ULD == -1:
            cartons.append(make_carton(package))
        elif package.ULD in container_ids:
            cartons.append(make_carton(package))
        else:
            assigned_solutions.append(make_solution(package))

    # print(initial_solution)
    cartons.sort(key=lambda x: x['id'])
    return cartons, assigned_solutions


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
    The function reads each row from the CSV file, creates a `Package` object from the row data,
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