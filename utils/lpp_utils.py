from utils.cartons import cartons
from utils.containers import containers
from utils.structs import getCube


cartons = cartons()
containers = containers()

def are_cubes_intersecting(obj1, obj2):
    """
    Determine if two 3D rectangular objects (cubes) are intersecting.
    This function checks whether two cubes, defined by their coordinates and dimensions,
    intersect with each other in a 3D space. The cubes are considered to be in the same
    container if their 'container_id' values are the same.
    Parameters:
    obj1 (dict): A dictionary representing the first cube with keys:
        - 'container_id': Identifier for the container the cube is in.
        - 'x': The x-coordinate of the cube's origin.
        - 'y': The y-coordinate of the cube's origin.
        - 'z': The z-coordinate of the cube's origin.
        - 'DimX': The dimension of the cube along the x-axis.
        - 'DimY': The dimension of the cube along the y-axis.
        - 'DimZ': The dimension of the cube along the z-axis.
    obj2 (dict): A dictionary representing the second cube with the same keys as obj1.
    Returns:
    bool: True if the cubes intersect, False otherwise.
    Note:
    - The function first checks if both cubes are in the same container.
    - It then calculates the minimum and maximum coordinates for both cubes along each axis.
    - Finally, it checks for overlap on all three axes (x, y, and z) to determine intersection.
    """
    # Function implementation here

    if obj1['container_id'] != obj2['container_id']:
        return False
    x1 = obj1['x']
    y1 = obj1['y']
    z1 = obj1['z']
    dimX1 = obj1['DimX']
    dimY1 = obj1['DimY']
    dimZ1 = obj1['DimZ']
    x2 = obj2['x']
    y2 = obj2['y']
    z2 = obj2['z']
    dimX2 = obj2['DimX']
    dimY2 = obj2['DimY']
    dimZ2 = obj2['DimZ']
    # Calculate the max and min coordinates for both cubes
    x1_min, x1_max = x1, x1 + dimX1
    y1_min, y1_max = y1, y1 + dimY1
    z1_min, z1_max = z1, z1 + dimZ1

    x2_min, x2_max = x2, x2 + dimX2
    y2_min, y2_max = y2, y2 + dimY2
    z2_min, z2_max = z2, z2 + dimZ2

    # Check for overlap on all three axes
    intersects = (
            x1_min < x2_max and x1_max > x2_min and  # X-axis overlap
            y1_min < y2_max and y1_max > y2_min and  # Y-axis overlap
            z1_min < z2_max and z1_max > z2_min  # Z-axis overlap
    )

    return intersects


def plot(answer):
    """
    Plots the 3D visualization of packages inside containers.
    This function takes a list of packages and plots their positions inside their respective containers
    using a 3D plot. Each container is plotted in a separate subplot.
    Parameters:
    answer (list of dict): A list of dictionaries where each dictionary represents a package with the following keys:
        - 'container_id': ID of the container the package belongs to.
        - 'x': X-coordinate of the package's position.
        - 'y': Y-coordinate of the package's position.
        - 'z': Z-coordinate of the package's position.
        - 'DimX': Dimension of the package along the X-axis.
        - 'DimY': Dimension of the package along the Y-axis.
        - 'DimZ': Dimension of the package along the Z-axis.
    Note:
    - The function assumes that the variable `containers` is defined globally and contains a list of dictionaries,
      where each dictionary represents a container with the following keys:
        - 'id': ID of the container.
        - 'length': Length of the container.
        - 'width': Width of the container.
        - 'height': Height of the container.
    - The function uses the `getCube` function to generate the vertices, edges, and faces of the packages.
    - The function uses Matplotlib for plotting.
    """
    # Function implementation here

    import math
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    num_containers = len(containers)
    fig = plt.figure(figsize=(15, 15))
    for idx, container in enumerate(containers):
        ax = fig.add_subplot(math.ceil(num_containers / 3), 3, idx + 1, projection='3d')
        ax.set_xlim([0, container['length']])
        ax.set_ylim([0, container['width']])
        ax.set_zlim([0, container['height']])
        ax.set_title(f"Container {container['id']}")
        for package in answer:
            if package['container_id'] != container['id']:
                continue
            x, y, z = package['x'], package['y'], package['z']
            dx, dy, dz = package['DimX'], package['DimY'], package['DimZ']
            v, e, f = getCube(np.array([[x, x + dx], [y, y + dy], [z, z + dz]]))
            ax.plot(*v.T, marker='o', color='k', ls='')
            for i, j in e:
                ax.plot(*v[[i, j], :].T, color='r', ls='-')
                ax.add_collection3d(
                    Poly3DCollection([v[i] for i in f], facecolors='green', linewidths=1, edgecolors='r', alpha=.25))

    plt.tight_layout()
    plt.show()


# Verifies if a box lies completely inside a container.
def is_box_inside_container(box, container):
    """
    Check if a box is inside a container.
    Parameters:
    box (dict): A dictionary containing the dimensions and position of the box with keys 'x', 'y', 'z', 'DimX', 'DimY', 'DimZ'.
    container (dict): A dictionary containing the dimensions of the container with keys 'length', 'width', 'height'.
    Returns:
    bool: True if the box is inside the container, False otherwise.
    The function checks if the box is within the bounds of the container in all three dimensions (x, y, z).
    """
    
    return (0 <= box['x'] and box['x'] + box['DimX'] <= container['length'] and
            0 <= box['y'] and box['y'] + box['DimY'] <= container['width'] and
            0 <= box['z'] and box['z'] + box['DimZ'] <= container['height'])

