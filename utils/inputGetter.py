import csv
from utils.structs import ULD,Package

def getPackages(packages):
    """
    Reads package data from a CSV file and appends Package objects to the provided list.
    Args:
        packages (list): A list to which the Package objects will be appended.
    Returns:
        list: The updated list with Package objects appended.
    The function reads from a CSV file named "package.csv". For each row in the CSV:
    - If the package type (6th column) is "Economy", it creates a Package object with 7 attributes.
    - Otherwise, it creates a Package object with 6 attributes.
    - The created Package object is then appended to the provided packages list.
    """
    
    f = open("package.csv", mode="r")
    packageCSV = csv.reader(f)
    for p in packageCSV:
        if p[5] == "Economy":
            package = Package(p[1],p[2],p[3],p[4],p[0],p[5],p[6])
            packages.append(package)
        else:
            package = Package(p[1],p[2],p[3],p[4],p[0],p[5])
            packages.append(package)
    return packages

def getULD(ulds):
    """
    Reads ULD data from a CSV file and appends ULD objects to the provided list.
    Args:
        ulds (list): A list to which ULD objects will be appended.
    Returns:
        list: The updated list with ULD objects appended.
    Note:
        The CSV file "ULD.csv" should be present in the same directory as this script.
        Each row in the CSV file should contain the following columns in order:
        [0] - Some identifier (used as the last argument in ULD constructor)
        [1] - First attribute for ULD
        [2] - Second attribute for ULD
        [3] - Third attribute for ULD
        [4] - Fourth attribute for ULD
    Raises:
        FileNotFoundError: If the "ULD.csv" file is not found.
        IndexError: If the rows in the CSV file do not have the expected number of columns.
    """

    f = open("ULD.csv", mode="r")
    uldCSV = csv.reader(f)
    for u in uldCSV:
        uld = ULD(u[1],u[2],u[3],u[4],u[0])
        ulds.append(uld)
    return ulds
