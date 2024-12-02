import csv
import ast
from utils.structs import CartonPackage as Package


def sol_to_package(solution):
    # container = solution[0]['container_id']

    packages = []

    print(solution)

    for o in solution:

        x = o['x']
        y = o['y']
        z = o['z']
        dimX = o['DimX']
        dimY = o['DimY']
        dimZ = o['DimZ']


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
