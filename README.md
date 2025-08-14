# FedEx ULD Optimization  

The Unit Load Device (ULD) optimization problem focuses on enhancing operational efficiency, reducing costs, and improving service reliability in logistics networks. ULDs are standardized air shipment containers with strict weight and volume limits, requiring efficient packing to maximize space utilization, minimize costs, and ensure the timely delivery of Priority Packages.

The challenge is to determine which packages to load into which ULDs while adhering to constraints such as weight limits, package dimensions, and the precedence of Priority Packages. Properly optimized ULDs not only reduce costs and ensure efficient resource utilization but also improve delivery timeliness and contribute to environmental sustainability by minimizing fuel consumption and carbon emissions.

## Packing Simulation using Streamlit  

We have provided a GUI, deployed using `Streamlit`, to display the packing sequence in each ULD, along with the packing visualization.

## Solution Pipeline  
[View the full report (PDF)](reports/67_m4_fedex.pdf)

### Overview of Optimization Strategy  

The solution pipeline employs a multi-stage approach to efficiently pack packages into Unit Load Devices (ULDs), combining heuristic methods and Mixed Integer Programming (MIP) techniques.  

### Pipeline Stages  

1. **Initial Data Preprocessing**  
   - Reorder ULD and package data using custom heuristics.  
   - Prepare data for an efficient placement strategy.  

2. **Package Classification**  
   - Separate packages into:  
     - **Priority Packages**: High-importance items.  
     - **Economy Packages**: Standard items.  

3. **Initial Package Assignment**  
   - **Extreme Points Filling**: Assign packages using extreme point placement to optimize spatial utilization.  
   - **Tri-Planar Projection**: Analyze and optimize placements along three axes (X, Y, Z).  

4. **Space Defragmentation**  
   - Reorganize package placements to minimize unused space and improve ULD efficiency.  

5. **Second Projection and Refinement**  
   - Repeat tri-planar projection for further optimization.  

6. **First Mixed Integer Programming (MIP) Stage**  
   - Attempt to fit unassigned packages using mathematical optimization.  
   - Execute for a predefined number of iterations.  

7. **Second MIP Stage**  
   - Focus on package swapping and optimizing assignments.  
   - Run additional iterations to maximize placement efficiency.  

### Optimization Objectives  

- Maximize ULD space utilization.  
- Prioritize critical (priority) packages.  
- Minimize transportation costs.  
- Reduce the number of unused or partially filled ULDs.  

---

## Deployment  

### Installing the Dependencies  

__Make sure that you have `Python 3.12` installed on your system.__  

Run the following command in your terminal:  

```bash
pip install -r requirements.txt
```  

__Ensure that your system has a valid `Gurobi Named-User License` installed.__  

---

### Running the Program  

#### 1. Command-Line Interface  

Run the following command in the repository folder:  

```bash
python main.py
```  

For advanced usage, an optional timeout parameter t (in seconds) can be added to control the runtime. Here t is not the total runtime, but the time the MIP solvers will run for:  

```bash
python main.py t
```  

#### 2. Streamlit Web Application  

To run the Streamlit app, use one of the following commands in the terminal inside the repository folder:  

```bash
streamlit run Streamlit_App.py
```  

If the above doesn't work, try:  

```bash
python3 -m streamlit run Streamlit_App.py
```  

Or:  

```bash
python -m streamlit run Streamlit_App.py
```  

---

## Streamlit App Usage Guide  

### Main Page  

When you first launch the app, you will see the main page with two input options:  

- __Upload File__: Upload CSV files for ULDs and packages.  
- __Manual Input__: Enter ULD and package data directly into the app.  

### Input Methods  

#### __File Input Method__:  

Prepare two CSV files:  

- **ULDs**: Contains ULD data with columns: ULD_id, length, width, height, and weight_limit.  
- **Packages**: Contains package data with columns: Package_id, length, width, height, weight, package_type, and penalty (for economy packages; enter `-` for priority packages).  

After that, you can choose the runtime t. Here t is not the total runtime, but the time the MIP solvers will run for.

Example ULDs CSV:  

```csv
U1, 100, 100, 100, 2500
U2, 100, 150, 125, 3000
```  

Example Packages CSV:  

```csv
P1, 99, 53, 55, 61, Economy, 176
P2, 56, 99, 81, 53, Priority, -
P3, 42, 101, 51, 17, Priority, -
P4, 108, 75, 56, 73, Economy, 138
P5, 88, 58, 64, 93, Economy, 139
```  

#### __Manual Input Method__:  

Manually enter details for:  

- **ULDs**: ULD_id, length, width, height, weight_limit.  
- **Packages**: Package_id, length, width, height, weight, package_type, penalty (for economy packages; enter `-` for priority packages).  

Click on __Add ULD__ or __Add Package__ after entering data for each ULD/package.  

After that, you can choose the runtime t. Here t is not the total runtime, but the time the MIP solvers will run for.

---

### Visualization  

After input, the app will:  

- Solve package placement optimization.  
- Create interactive 3D visualizations of package placement.  
- Display progressive packing sequences.  
- Show detailed metrics, including:  
  - Free space percentage.  
  - Free weight percentage.  
  - Total number of packages.  
  - Priority vs. economy packages packed.  
  - Total packages loaded.  
  - Total cost of shipment.  

---

### Demo


https://github.com/user-attachments/assets/7620c50d-f914-449e-8498-6cc412d363d5



### Potential Future Enhancements  

- Advanced space fragmentation techniques.  
- Enhanced MIP formulations.  
- Machine learning-based placement predictions.  
