import csv
import ast
from utils.structs import CartonPackage as Package

import csv
import ast
from utils.structs import CartonPackage as Package


def sol_to_package(solution):
    # container = solution[0]['container_id']

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
