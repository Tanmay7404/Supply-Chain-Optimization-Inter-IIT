
# FedEx ULD Optimization



The Unit Load Device (ULD) optimization problem focuses on enhancing operational efficiency,
reducing costs, and improving service reliability in logistics networks. ULDs are standardized
air shipment containers with strict weight and volume limits, requiring efficient packing to
maximize space utilization, minimize costs, and ensure the timely delivery of Priority Packages.

The challenge is to determine which packages to load into which ULDs while adhering to
constraints such as weight limits, package dimensions, and the precedence of Priority Packages. Properly optimized ULDs not only reduce costs and ensure efficient resource utilization but
also improve delivery timeliness and contribute to environmental sustainability by minimizing
fuel consumption and carbon emissions.
## Packing Simulation using Streamlit

We have provided a GUI, deployed using `Streamlit` to display the packing sequence in each ULD, along with the packing visualization.
## Deployment


### Installing the dependencies

__Make sure that you have `Python 3.12` installed in your system.__

Run the following command in your terminal 

```bash
pip install -r requirements.txt
```

__Ensure that your system has a valid `Gurobi Named-User License` installed.__


### Running the program

Now, to run the script enter the following command in the terminal inside the folder where the repository is cloned

```bash
streamlit run Streamlit_App.py
```

If it does not work, then try

```bash
python3 -m streamlit run Streamlit_App.py
```

If it does not work, then try

```bash
python -m streamlit run Streamlit_App.py
```
## Streamlit App Usage Guide

### Main Page

When you first launch the app, you will see the main page with two input options:

- __Upload File__ : Upload CSV files for ULDs and packages
- __Manual Input__ : Enter ULD and package data directly into the app

### Input Methods

#### __File Input Method :__

Prepare two CSV files : 

- __ULDs__ : It must have the data of the ULDs with columns respectively as ULD_id, length, width, height and weight_limit.
- __Packages__ : It must have the data of the packages respectively as Package_id, length, width, height, weight, package_type and penalty(for economy(enter a '-' for priority)).

ULDs CSV format example :

```csv
U1, 100, 100, 100, 2500
U2, 100, 150, 125, 3000
```

Packages CSV format example :

```csv
P1, 99, 53, 55, 61, Economy, 176
P2, 56, 99, 81, 53, Priority, -
P3, 42, 101, 51, 17, Priority, -
P4, 108, 75, 56, 73, Economy, 138
P5, 88, 58, 64, 93, Economy, 139
```

#### __Manual Input Method :__

Manually enter details for :

- __ULDs__ : ULD_id, length, width, height, weight_limit
- __Packages__ : Package_id, length, width, height, weight, package_type, penalty(for economy(enter a '-' for priority))

Click on __Add ULD__ or __Add Package__ everytime we enter data for a particular ULD/package.

### Visualization

After input, the app will

- Solve package placement optimization.
- Create interactive 3D visualizations of package placement.
- Display progressive packing sequence.
- Show detailed metrics such as free space percentage, free weight percentage, total packages, priority vs economy packages packed, total packages taken and total cost of shipment.
## Solution Pipeline

### Overview of Optimization Strategy
The solution pipeline is a multi-stage approach to efficiently pack packages into Unit Load Devices (ULDs), utilizing a combination of heuristic methods and Mixed Integer Programming (MIP) techniques.

### Pipeline Stages

#### 1. Initial Data Preprocessing
- **Reordering Heuristics**
  - Reorder ULD and Package data based on custom heuristics
  - Prepare data for efficient placement strategy

#### 2. Package Classification
- Separate packages into two categories:
  - **Priority Packages**: High-importance items
  - **Economy Packages**: Standard items

#### 3. Initial Package Assignment
- **Extreme Points Filling**
  - Assign packages to ULDs using extreme point placement strategy
  - Optimize initial spatial utilization

- **Tri-Planar Projection**
  - Project and analyze package placement along three axes:
    - X-axis (Length)
    - Y-axis (Width)
    - Z-axis (Height)
  - Ensures comprehensive spatial coverage

#### 4. Space Defragmentation
- Reorganize package placements to:
  - Minimize unused spaces
  - Improve overall ULD space efficiency

#### 5. Second Projection and Refinement
- Repeat tri-planar projection
- Further optimize package positioning

#### 6. First Mixed Integer Programming (MIP) Stage
- **Unassigned Package Fitting**
  - Attempt to fit remaining unassigned packages
  - Run for a predefined number of iterations
  - Utilize mathematical optimization techniques

#### 7. Second MIP Stage
- **Package Swapping and Optimization**
  - Focus on unassigned packages
  - Swap currently assigned packages to create space
  - Run for additional iterations to maximize placement efficiency

### Optimization Objectives
- Maximize ULD space utilization
- Prioritize critical (priority) packages
- Minimize transportation costs
- Reduce number of unused or partially filled ULDs

### Algorithmic Complexity
- Combines heuristic and mathematical programming approaches
- Iterative refinement of package placement
- Handles both priority and economy package constraints

### Potential Future Enhancements
- More advanced space fragmentation techniques
- Enhanced MIP formulations
- Machine learning-based placement predictions
