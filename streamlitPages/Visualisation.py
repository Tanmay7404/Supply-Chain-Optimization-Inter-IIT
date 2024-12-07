import streamlit as st
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from utils.structs import ULD, Package
from heuristics.solver2_withSpaceDefrag import Solver2
import numpy as np
import plotly.graph_objs as go
import colorsys
import time
import plotly.colors as colors
from main import *

k=5000

def generate_color_map(packages):
    """
    Generate a color map with visually distinct colors for packages.
    
    Args:
        packages: List of Package objects
    
    Returns:
        A dictionary mapping package IDs to colors
    """
    num_packages = len(packages)
    # Extract package IDs
    package_ids = [package.id for package in packages]
    unique_ids = np.unique(package_ids)

    # Convert package IDs to numeric indices
    id_to_index = {pid: idx for idx, pid in enumerate(unique_ids)}
    indices = np.array([id_to_index[pid] for pid in package_ids])

    if len(unique_ids) > 1:
        # Scale indices to range [0, 1]
        scaled = (indices - np.min(indices)) / (np.max(indices) - np.min(indices))
        # Sample colors from the Rainbow colorscale
        color_list = colors.sample_colorscale(colors.sequential.Rainbow, scaled)
    else:
        color_list = ["blue"] * len(package_ids)
    
     # Create color map
    color_map = {}
    for idx, package in enumerate(packages):
        color_map[package.id] = color_list[idx]
    
    return color_map

def create_package_mesh(package,color_map):
    """
    Create a detailed 3D mesh representation of a package
    
    Args:
        package: Package object
    
    Returns:
        Plotly Mesh3d trace
    """
    [x,y,z] = package.position 
    [dx,dy,dz] = package.getDimensions() 
    color = color_map[package.id]  # Use the color assigned from the color map
    opacity = 1  # Uniform opacity
    
    # # Determine package color based on stability
    # if package.stable == -1:
    #     color = 'red'      # Unstable 
    #     opacity = 0.6
    # elif package.stable:
    #     color = 'green'    # Stable 
    #     opacity = 0.7
    # else:
    #     color = 'orange'   # Partially stable
    #     opacity = 0.65
    
    # Vertex coordinates for a cuboid
    x_coords = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    y_coords = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    z_coords = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    
    # Indices for creating mesh faces
    i = [0, 1, 0, 1, 1, 2, 0, 4, 3, 7, 4, 5]
    j = [1, 4, 1, 3, 2, 5, 3, 3, 2, 2, 5, 7]
    k = [4, 5, 3, 2, 5, 6, 4, 7, 7, 6, 7, 6]
    
    # Create a 3D mesh trace with distinct outline
    mesh_trace = go.Mesh3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        i=i,
        j=j,
        k=k,
        opacity=opacity,
        color=color,
        showscale=False,
        name=f'Package at\n({x:.2f},{y:.2f},{z:.2f})',
        # Add wireframe effect
        flatshading=True,
        lighting=dict(
            ambient=0.8,
            diffuse=0.8,
            fresnel=0.2,
            specular=0.3,
            roughness=0.4
        ),
        lightposition=dict(
            x=100,
            y=200,
            z=300
        )
    )

     # Define edges for black outline
    edges = [
        # Bottom face edges
        [0, 1], [1, 2], [2, 3], [3, 0],
        # Top face edges
        [4, 5], [5, 6], [6, 7], [7, 4],
        # Vertical connecting edges
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    # Create edge traces
    edge_traces = []
    for edge in edges:
        edge_trace = go.Scatter3d(
            x=[x_coords[edge[0]], x_coords[edge[1]]],
            y=[y_coords[edge[0]], y_coords[edge[1]]],
            z=[z_coords[edge[0]], z_coords[edge[1]]],
            mode='lines',
            line=dict(color='black', width=3),
            showlegend=False,
            hoverinfo='none'
        )
        edge_traces.append(edge_trace)
    
    return [mesh_trace] + edge_traces


def process_file_input():
    """
    Processes the file inputs for ULDs and packages from the Streamlit session state.
    This function reads CSV data from the Streamlit session state for ULDs and packages,
    creates instances of ULD and Package classes, and returns lists of these instances.
    Returns:
        tuple: A tuple containing two lists:
            - ulds (list): A list of ULD instances created from the ULD CSV data.
            - packages (list): A list of Package instances created from the package CSV data.
    """
    # Function implementation here

    ulds = []
    packages = []
    
    with st.session_state.uld_file:
        uldCSV = csv.reader(st.session_state.uld_file.getvalue().decode("utf-8").splitlines())
       
        for u in uldCSV:
            uld = ULD(u[1], u[2], u[3], u[4], u[0])
            ulds.append(uld)
    
    with st.session_state.package_file:
        packageCSV = csv.reader(st.session_state.package_file.getvalue().decode("utf-8").splitlines())
        
        for p in packageCSV:
            if p[5] == "Economy":
                package = Package(p[1], p[2], p[3], p[4], p[0], p[5], p[6])
            else:
                package = Package(p[1], p[2], p[3], p[4], p[0], p[5])
            packages.append(package)
    
    return ulds, packages


def create_progressive_uld_plot(uld, packages_to_add):
    """
    Create a progressive 3D plot where packages are added one by one with ULD boundaries and semi-transparent faces.
    
    Args:
        uld: ULD object 
        packages_to_add: List of packages to add progressively
    
    Returns:
        Plotly figure object
    """

    # Create columns for plot and packing sequence
    col1, col2 = st.columns([2, 1])
    with col1:
        # Create a Streamlit container for the plot
        plot_container = st.empty()

    with col2:
        # Containers for upcoming and completed packing sequence
        upcoming_sequence_container = st.empty()
        completed_sequence_container = st.empty()

    # Generate color map for all packages
    color_map = generate_color_map(packages_to_add)

    # Determine plot boundaries
    max_length = float(uld.length)
    max_width = float(uld.width)
    max_height = float(uld.height)

    # ULD boundary vertices
    x_coords = [0, max_length, max_length, 0, 0, max_length, max_length, 0]
    y_coords = [0, 0, max_width, max_width, 0, 0, max_width, max_width]
    z_coords = [0, 0, 0, 0, max_height, max_height, max_height, max_height]

    # ULD edges definition
    uld_edges = [
        # Bottom face edges
        [0, 1], [1, 2], [2, 3], [3, 0],
        # Top face edges
        [4, 5], [5, 6], [6, 7], [7, 4],
        # Vertical connecting edges
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    # Create ULD boundary traces (edges)
    boundary_traces = []
    for edge in uld_edges:
        boundary_traces.append(
            go.Scatter3d(
                x=[x_coords[edge[0]], x_coords[edge[1]]],
                y=[y_coords[edge[0]], y_coords[edge[1]]],
                z=[z_coords[edge[0]], z_coords[edge[1]]],
                mode='lines',
                line=dict(color='black', width=3),
                showlegend=False,
                hoverinfo='none'
            )
        )

    # Add semi-transparent faces for the ULD
    uld_faces = go.Mesh3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        color='blue',
        opacity=0.3,
        i = [0, 1, 0, 1, 1, 2, 0, 4, 3, 7, 4, 5],
        j = [1, 4, 1, 3, 2, 5, 3, 3, 2, 2, 5, 7],
        k = [4, 5, 3, 2, 5, 6, 4, 7, 7, 6, 7, 6],
        name="ULD",
        showscale=False
    )

    # Create the layout
    layout = go.Layout(
        scene=dict(
            xaxis=dict(
                title=dict(text='Length', font=dict(size=16, color='black', family='Arial, bold')),
                range=[0, max_length],
                gridcolor='lightgray',
                showbackground=True,
                backgroundcolor='rgba(230,230,230,0.5)'
            ),
            yaxis=dict(
                title=dict(text='Width', font=dict(size=14, color='black', family='Arial, bold')),
                range=[0, max_width],
                gridcolor='lightgray',
                showbackground=True,
                backgroundcolor='rgba(230,230,230,0.5)'
            ),
            zaxis=dict(
                title=dict(text='Height', font=dict(size=14, color='black', family='Arial, bold')),
                range=[0, max_height],
                gridcolor='lightgray',
                showbackground=True,
                backgroundcolor='rgba(230,230,230,0.5)'
            ),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1)
        ),
        title=dict(
            text=f'ULD {uld.id}',
            font=dict(size=24, color='black', family='Arial, bold')
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        paper_bgcolor='white'
    )

    # Prepare sequence lists
    upcoming_packages = [p.id for p in packages_to_add]
    completed_packages = []

    # Progressive package addition
    for i in range(1, len(packages_to_add) + 1):
        # Create traces for packages added so far
        current_packages = packages_to_add[:i]
        all_traces = [uld_faces] + boundary_traces  # Start with ULD faces and boundaries

        for package in current_packages:
            all_traces.extend(create_package_mesh(package, color_map))

        # Create figure with current packages
        fig = go.Figure(data=all_traces, layout=layout)

        # Update Streamlit plot
        with col1:
            plot_container.plotly_chart(fig, use_container_width=True)

        # Update packing sequence
        if upcoming_packages:
            current_package = upcoming_packages.pop(0)
            completed_packages.append(current_package)

        with col2:
            # Upcoming sequence (CSV format)
            if upcoming_packages:
                upcoming_sequence_container.markdown(f"Upcoming Sequence:  \n`{','.join(upcoming_packages)}`")
            else:
                upcoming_sequence_container.markdown("Upcoming Sequence:  \n`None`")

            completed_sequence_container.markdown(f"Packing Sequence Till Now:  \n`{','.join(completed_packages)}`")

        # Add a small delay to create a progressive loading effect
        time.sleep(0.1)

    return fig



def metrics(ulds, packages):
    """
    Calculate various metrics related to the utilization of ULDs (Unit Load Devices) and packages.
    Args:
        ulds (list): A list of ULD objects, each containing volume, weight limit, and packages.
        packages (list): A list of package objects, each containing volume, weight, priority, and ULD assignment.
    Returns:
        dict: A dictionary containing the following metrics:
            - freeSpacePercentage (float): The percentage of free space available in all ULDs.
            - freeWeightPercentage (float): The percentage of free weight capacity available in all ULDs.
            - packagesTotal (int): The total number of packages.
            - packagesPriority (int): The total number of priority packages.
            - packagesEconomy (int): The total number of economy packages.
            - packagesTotalTaken (int): The total number of packages that have been taken (assigned to a ULD).
            - packagesPriorityTaken (int): The total number of priority packages that have been taken.
            - packagesEconomyTaken (int): The total number of economy packages that have been taken.
            - cost (float): The total cost of packages that have not been taken, plus an additional cost for priority ULDs.
    """
    # Function implementation here
    
    freeSpace = 0
    totalSpace = 0
    freeWeight = 0
    totalWeight = 0
    for uld in ulds:
        uldfreeSpace = uld.getVolume()
        uldtotalSpace = uld.getVolume()
        totalSpace += uld.getVolume()
        freeSpace += uld.getVolume()
        totalWeight += uld.weight_limit
        freeWeight += uld.weight_limit
        uldfreeWeight = uld.weight_limit
        uldtotalWeight = uld.weight_limit
        for package in uld.packages:
            uldfreeSpace -= package.getVolume()
            freeSpace -= package.getVolume()
            uldfreeWeight -= package.weight
            freeWeight -= package.weight

    if totalSpace > 0 and totalWeight > 0:
        freeSpacePercentage = freeSpace / totalSpace * 100
        freeWeightPercentage = freeWeight / totalWeight * 100
    else:
        freeSpacePercentage = 0
        freeWeightPercentage = 0
    
    packagesTotal = len(packages)
    packagesPriority = sum(1 for p in packages if p.priority == "Priority")
    packagesEconomy = packagesTotal - packagesPriority
    packagesTotalTaken = sum(1 for p in packages if str(p.ULD) != '-1')
    packagesPriorityTaken = sum(1 for p in packages if p.priority == "Priority" and str(p.ULD) != '-1')
    packagesEconomyTaken = packagesTotalTaken - packagesPriorityTaken

    cost = sum(p.cost for p in packages if str(p.ULD) == '-1')
    for uld in ulds:
        if uld.isPriority:
            cost += k

    return {
        "freeSpacePercentage": freeSpacePercentage,
        "freeWeightPercentage": freeWeightPercentage,
        "packagesTotal": packagesTotal,
        "packagesPriority": packagesPriority,
        "packagesEconomy": packagesEconomy,
        "packagesTotalTaken": packagesTotalTaken,
        "packagesPriorityTaken": packagesPriorityTaken,
        "packagesEconomyTaken": packagesEconomyTaken,
        "cost": cost
    }

def sort_packages_by_position(packages):
    """
    Sorts a list of packages based on their position.
    The packages are sorted primarily by the z-coordinate, then by the x-coordinate,
    and finally by the y-coordinate of their position.
    Args:
        packages (list): A list of package objects, where each package has a 'position' attribute
                         that is a tuple or list containing three numerical values (x, y, z).
    Returns:
        list: A sorted list of packages based on their position.
    """
    # Sort packages by z-coordinate, then x-coordinate, and finally y-coordinate
    
    return sorted(packages, key=lambda p: (p.position[2], p.position[0], p.position[1]))



def page():
    """
    Renders the ULDs and Packages Visualization page in a Streamlit application.
    This function handles the following:
    - Displays the title of the page.
    - Provides a button to navigate back to the main page.
    - Manages session state for delay placeholders.
    - Determines the input method (file upload or manual input) and processes the ULDs and Packages accordingly.
    - Visualizes the ULDs and Packages using progressive plots.
    - Displays various metrics related to the ULDs and Packages.
    The function checks for the presence of ULD and Package data in the session state and processes them using the appropriate method:
    - If file upload method is used, it processes the files and visualizes the data.
    - If manual input method is used, it uses the Solver2 class to solve and visualize the data.
    Metrics displayed include:
    - Free Space Percentage
    - Free Weight Percentage
    - Total Packages
    - Priority Packages
    - Economy Packages
    - Packages Taken
    - Priority Packages Taken
    - Economy Packages Taken
    - Total Cost
    If no ULDs or Packages are found in the session state, an error message is displayed.
    At the end of the function, any ULD or Package data in the session state is cleared.
    """

    st.title("ULDs and Packages Visualization")
    
    # Add a button to return to main page
    if st.button("← Back to Main Page"):
        st.session_state.page = 'main'
        st.rerun()
    
    
    # Add a delay placeholder in session state
    if 'delay_placeholder' not in st.session_state:
        st.session_state.delay_placeholder = st.empty()

    # Determine input method and get ULDs and Packages
    if hasattr(st.session_state, 'uld_file') and hasattr(st.session_state, 'package_file'):
        # File upload method
        ulds, packages = process_file_input()
        # Solve and visualize
        run_all(ulds, packages, st.session_state.timeout)
        #sort by z,x,y
        
        st.subheader("Visualizing ULDs and Packages")
        for uld in ulds:
            if uld.packages:
                uld.packages=sort_packages_by_position(uld.packages)
                create_progressive_uld_plot(uld, uld.packages)
                
        # Display metrics
        st.subheader("Metrics")
        metrics_data = metrics(ulds, packages)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Free Space (%)", f"{metrics_data['freeSpacePercentage']:.2f}%")
            st.metric("Total Free Weight (%)", f"{metrics_data['freeWeightPercentage']:.2f}%")
        with col2:
            st.metric("Total Packages", metrics_data['packagesTotal'])
            st.metric("Total Priority Packages", metrics_data['packagesPriority'])
            st.metric("Total Economy Packages", metrics_data['packagesEconomy'])
        with col3:
            st.metric("Packages Taken", metrics_data['packagesTotalTaken'])
            st.metric("Priority Packages Taken", metrics_data['packagesPriorityTaken'])
            st.metric("Economy Packages Taken", metrics_data['packagesEconomyTaken'])
            st.metric("Total Cost", f"{metrics_data['cost']}")
    elif hasattr(st.session_state, 'manual_ulds') and hasattr(st.session_state, 'manual_packages'):
        # Manual input method
        ulds = st.session_state.manual_ulds
        packages = st.session_state.manual_packages
         # Solve and visualize
        solver2 = Solver2(packages, ulds)
        solver2.solve()

        st.subheader("Visualizing ULDs and Packages")
        for uld in ulds:
            if uld.packages:
                uld.packages=sort_packages_by_position(uld.packages)
                create_progressive_uld_plot(uld, uld.packages)
       


        # Display metrics
        st.subheader("Metrics")
        metrics_data = metrics(ulds, packages)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Free Space (%)", f"{metrics_data['freeSpacePercentage']:.2f}%")
            st.metric("Free Weight (%)", f"{metrics_data['freeWeightPercentage']:.2f}%")
        with col2:
            st.metric("Total Packages", metrics_data['packagesTotal'])
            st.metric("Priority Packages", metrics_data['packagesPriority'])
            st.metric("Economy Packages", metrics_data['packagesEconomy'])
        with col3:
            st.metric("Packages Taken", metrics_data['packagesTotalTaken'])
            st.metric("Priority Packages Taken", metrics_data['packagesPriorityTaken'])
            st.metric("Economy Packages Taken", metrics_data['packagesEconomyTaken'])
            st.metric("Total Cost", f"{metrics_data['cost']}")
    else:
        st.error("No ULDs or Packages found. Please input data first.")
        return
    if 'uld_file' in st.session_state:
        del st.session_state['uld_file']
    if 'package_file' in st.session_state:
        del st.session_state['package_file']
    if 'manual_ulds' in st.session_state:
        del st.session_state.manual_ulds
    if 'manual_packages' in st.session_state:
        del st.session_state.manual_packages
   

if __name__ == "main":
    page()