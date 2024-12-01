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
        with open('file.csv', mode='a', newline='') as outfile:
            writer = csv.writer(outfile)
            p = int(o.get('Priority', '') == 'Priority')
            writer.writerow([
                o.get('carton_id', ''),
                o.get('container_id', ''),
                str([o.get('x', ''), o.get('y', ''), o.get('z', '')]),
                str([o.get('DimX', ''), o.get('DimY', ''), o.get('DimZ', '')]),
                o.get('weight'),
                o.get('cost'),
                p
            ])
    return packages
