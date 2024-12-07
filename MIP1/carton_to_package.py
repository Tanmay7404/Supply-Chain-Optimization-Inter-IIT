import csv
import ast
from utils.structs import CartonPackage as Package


def sol_to_package(solution):
    """
    Converts a solution dictionary to a list of Package objects.
    Args:
        solution (list of dict): A list of dictionaries where each dictionary contains
                                 information about a carton and its placement in a package.
    Returns:
        list of Package: A list of Package objects created from the solution data.
    Each dictionary in the solution list may contain the following keys:
        - 'x', 'y', 'z' (optional): Coordinates of the carton in the package.
        - 'DimX', 'DimY', 'DimZ' (optional): Dimensions of the carton.
        - 'length', 'width', 'height' (optional): Dimensions of the carton if 'DimX', 'DimY', 'DimZ' are not provided.
        - 'carton_id' (optional): Identifier for the carton.
        - 'container_id' (optional): Identifier for the container.
        - 'weight' (optional): Weight of the carton.
        - 'cost' (optional): Cost associated with the carton.
        - 'rotation' (optional): Rotation of the carton.
    If 'x', 'y', 'z' are not provided, they are set to -1.
    If 'DimX', 'DimY', 'DimZ' are not provided, they are calculated from 'length', 'width', 'height' by sorting them.
    Example:
        solution = [
            {'x': 1, 'y': 2, 'z': 3, 'DimX': 4, 'DimY': 5, 'DimZ': 6, 'carton_id': 'C1', 'container_id': 'U1', 'weight': 10, 'cost': 100, 'rotation': 0},
            {'length': 7, 'width': 8, 'height': 9, 'carton_id': 'C2', 'container_id': 'U2', 'weight': 20, 'cost': 200, 'rotation': 1}
        ]
        packages = sol_to_package(solution)
    """
    
    packages = []
    for o in solution:
        if o.get('x') != None:
            x = o['x']
            y = o['y']
            z = o['z']
        else:
            x = -1
            y = -1
            z = -1
        if o.get('DimX') != None:
            dimX = o['DimX']
            dimY = o['DimY']
            dimZ = o['DimZ']
        else:
            v = [float(o['length']), float(o['width']), float(o['height'])]
            v.sort()
            dimX = v[0]
            dimY = v[1]
            dimZ = v[2]



        packages.append(Package(
            id=o.get('carton_id', ''),
            uldid=o.get('container_id', ''),
            position=[x, y, z],
            dimensions=[dimX, dimY, dimZ],
            weight=o.get('weight', ''),
            cost=o.get('cost', ''),
            rotation=o.get('rotation', '')
        ))
    return packages
