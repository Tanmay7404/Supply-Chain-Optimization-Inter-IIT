import gurobipy as gp
from gurobipy import GRB, quicksum

stability_threshold = 0.6
# maximum fraction of dimension of a carton allowed to be unsupported by another carton

def container_loading_with_relative_constraints(cartons, containers,timeout = 30):
    """
    Solve the 3D container loading problem using mixed integer programming,
    incorporating relative positioning constraints (aik, bik, cik, dik, eik, fik).

    Parameters:
    cartons: list of dictionaries with carton details (dimensions and weight).
             Each carton is represented as {'id': int, 'length': float, 'width': float, 'height': float, 'weight': float}.
    containers: list of dictionaries with container dimensions.
             Each container is represented as {'id': int, 'length': float, 'width': float, 'height': float}.

    Returns:
    Optimal packing solution with carton placements, orientations, and container usage.
    """

    # Create a model
    model = gp.Model("3D_Container_Loading_with_Relative_Positioning")
    model.Params.LogToConsole = 0 # Show optimization logs
    
    # Define constants
    M = 100000  # Large constant for "big-M" constraints

    # Decision variables
    sij = {}  # Binary: carton i assigned to container j
    xi, yi, zi = {}, {}, {}  # Continuous: coordinates of FLB corner of carton i
    nj = {}
    orientation = {}  # Binary variables for carton orientation (rotation matrix)
    relative_position = {}  # Binary variables for relative positions (aik, bik, cik, dik, eik, fik)
    # Add variables
    x = model.addVar(vtype=GRB.BINARY, name="1")
    model.addConstr(x == 1)

    
    for container in containers:        #nj variable is 1 if j-th container is used
        nj[container['id']] = model.addVar(vtype=GRB.INTEGER, name=f"n_{container['id']}")
    
    for carton in cartons:
        for container in containers:
            '''
            sij[(carton['id'], container['id'])] is a binary variable that is 1 if the carton is assigned to the container
            yi[carton['id']] is the y-coordinate of the front-left-bottom corner of the carton
            xi[carton['id']] is the x-coordinate of the front-left-bottom corner of the carton
            zi[carton['id']] is the z-coordinate of the front-left-bottom corner of the carton
            '''
            sij[(carton['id'], container['id'])] = model.addVar(vtype=GRB.BINARY, name=f"s_{carton['id']}_{container['id']}")
        
        xi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"x_{carton['id']}")
        yi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"y_{carton['id']}")
        zi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"z_{carton['id']}")
        
        # coordinates must be non-negative
        model.addConstr(xi[carton['id']] >= 0)
        model.addConstr(yi[carton['id']] >= 0)
        model.addConstr(zi[carton['id']] >= 0)
        # Add 9 binary orientation variables for each carton
        orientation[carton['id']] = {

            "lx": model.addVar(vtype=GRB.BINARY, name=f"lx_{carton['id']}"),
            "ly": model.addVar(vtype=GRB.BINARY, name=f"ly_{carton['id']}"),
            "lz": model.addVar(vtype=GRB.BINARY, name=f"lz_{carton['id']}"),
            "wx": model.addVar(vtype=GRB.BINARY, name=f"wx_{carton['id']}"),
            "wy": model.addVar(vtype=GRB.BINARY, name=f"wy_{carton['id']}"),
            "wz": model.addVar(vtype=GRB.BINARY, name=f"wz_{carton['id']}"),
            "hx": model.addVar(vtype=GRB.BINARY, name=f"hx_{carton['id']}"),
            "hy": model.addVar(vtype=GRB.BINARY, name=f"hy_{carton['id']}"),
            "hz": model.addVar(vtype=GRB.BINARY, name=f"hz_{carton['id']}"),
            "ground":model.addVar(vtype=GRB.BINARY, name=f"touching_ground_{carton['id']}"),
            # ground - 1 if the carton is touching the ground
        }

    # Relative positioning variables: aik, bik, cik, dik, eik, fik
    '''
        aik - carton i is to the left of carton k
        bik - carton i is to the right of carton k
        cik - carton i is behind carton k
        dik - carton i is in front of carton k
        eik - carton i is below carton k
        fik - carton i is above carton k
    '''
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
            carton_i = cartons[i]
            carton_k = cartons[k]
            relative_position[(carton_i['id'], carton_k['id'])] = {
                "aik": model.addVar(vtype=GRB.BINARY, name=f"aik_{carton_i['id']}_{carton_k['id']}"),
                "bik": model.addVar(vtype=GRB.BINARY, name=f"bik_{carton_i['id']}_{carton_k['id']}"),
                "cik": model.addVar(vtype=GRB.BINARY, name=f"cik_{carton_i['id']}_{carton_k['id']}"),
                "dik": model.addVar(vtype=GRB.BINARY, name=f"dik_{carton_i['id']}_{carton_k['id']}"),
                "eik": model.addVar(vtype=GRB.BINARY, name=f"eik_{carton_i['id']}_{carton_k['id']}"),
                "fik": model.addVar(vtype=GRB.BINARY, name=f"fik_{carton_i['id']}_{carton_k['id']}"),
            }
    
    # stability constraints
    for i in range(len(cartons)):
        for j in range(len(cartons)):
            if (i==j):
                continue
            if (cartons[i]['id'], cartons[j]['id']) not in relative_position:
                relative_position[(cartons[i]['id'], cartons[j]['id'])] = {}
            relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"] = model.addVar(vtype=GRB.BINARY, name=f"support_{carton_i['id']}_{carton_k['id']}")
    # for every pair of cartons i, j, there is a binary variable support_ij that is 1 if carton i is supported carton j
   
    # Constraints
    # 1. Assign each carton to exactly one container
    for carton in cartons:
        model.addConstr(sum(sij[(carton['id'], container['id'])] for container in containers) == 1,
                        name=f"assign_{carton['id']}")
    
    # carton must be assigned to a used container 
    for container in containers:
       model.addConstr(sum(sij[(carton['id'], container['id'])] for carton in cartons) <= M*nj[container['id']],
      name=f"assign_{container['id']}")


    # 2. Orientation consistency: Each dimension aligns with exactly one axis
    for carton in cartons:
        orients = orientation[carton['id']]
        model.addConstr(orients["lx"] + orients["ly"] + orients["lz"] == 1, name=f"orient_length_{carton['id']}")
        model.addConstr(orients["wx"] + orients["wy"] + orients["wz"] == 1, name=f"orient_width_{carton['id']}")
        model.addConstr(orients["hx"] + orients["hy"] + orients["hz"] == 1, name=f"orient_height_{carton['id']}")

        # Each axis has one dimension
        model.addConstr(orients["lx"] + orients["wx"] + orients["hx"] == 1, name=f"axis_x_{carton['id']}")
        model.addConstr(orients["ly"] + orients["wy"] + orients["hy"] == 1, name=f"axis_y_{carton['id']}")
        model.addConstr(orients["lz"] + orients["wz"] + orients["hz"] == 1, name=f"axis_z_{carton['id']}")

    # 3. Fit cartons within container dimensions
    for carton in cartons:
        for container in containers:
            orients = orientation[carton['id']]
            model.addConstr(xi[carton['id']] + carton['length'] * orients["lx"] +
                            carton['width'] * orients["wx"] +
                            carton['height'] * orients["hx"] <= container['length'] + (
                                        1 - sij[(carton['id'], container['id'])]) * M,
                            name=f"fit_x_{carton['id']}_{container['id']}")

            model.addConstr(yi[carton['id']] + carton['length'] * orients["ly"] +
                            carton['width'] * orients["wy"] +
                            carton['height'] * orients["hy"] <= container['width'] + (
                                        1 - sij[(carton['id'], container['id'])]) * M,
                            name=f"fit_y_{carton['id']}_{container['id']}")

            model.addConstr(zi[carton['id']] + carton['length'] * orients["lz"] +
                            carton['width'] * orients["wz"] +
                            carton['height'] * orients["hz"] <= container['height'] + (
                                        1 - sij[(carton['id'], container['id'])]) * M,
                            name=f"fit_z_{carton['id']}_{container['id']}")

    
    for container in containers:
        # weight constraints
        model.addConstr(sum((sij[(carton['id'], container['id'])] * carton['weight']) for carton in cartons) <= container['weight'],
                        name=f"weight_limit_constr{container['id']}")
        for i in range(len(cartons)):
            for k in range(i + 1, len(cartons)):
                carton_i = cartons[i]
                carton_k = cartons[k]
                rel = relative_position[(carton_i['id'], carton_k['id'])]
                model.addConstr((rel["aik"] + rel["bik"] + rel["cik"] + rel["dik"] + rel["eik"] + rel["fik"] >=
                                 sij[(carton_i['id'], container['id'])] + sij[(carton_k['id'], container['id'])] - x),
                                name=f"relative_sum_{carton_i['id']}_{carton_k['id']}_{container['id']}")
    
    # 4. Prevent overlapping of cartons with aik, bik, cik, dik, eik, fik
    for i in range(len(cartons)):
        for k in range(i+1, len(cartons)):
            carton_i = cartons[i]
            carton_k = cartons[k]
            rel = relative_position[(carton_i['id'], carton_k['id'])]
            model.addConstr(
                xi[carton_i['id']] + carton_i['length'] * orientation[carton_i['id']]["lx"] + carton_i['width'] *
                orientation[carton_i['id']]["wx"] + carton_i['height'] * orientation[carton_i['id']]["hx"] <= xi[
                    carton_k['id']] + (1 - rel["aik"]) * M, name=f"no_overlap_x_a_{carton_i['id']}_{carton_k['id']}")
            model.addConstr(
                xi[carton_k['id']] + carton_k['length'] * orientation[carton_k['id']]["lx"] + carton_k['width'] *
                orientation[carton_k['id']]["wx"] + carton_k['height'] * orientation[carton_k['id']]["hx"] <= xi[
                    carton_i['id']] + (1 - rel["bik"]) * M, name=f"no_overlap_x_b_{carton_i['id']}_{carton_k['id']}")
            model.addConstr(
                yi[carton_i['id']] + carton_i['length'] * orientation[carton_i['id']]["ly"] + carton_i['width'] *
                orientation[carton_i['id']]["wy"] + carton_i['height'] * orientation[carton_i['id']]["hy"] <= yi[
                    carton_k['id']] + (1 - rel["cik"]) * M, name=f"no_overlap_y_c_{carton_i['id']}_{carton_k['id']}")
            model.addConstr(
                yi[carton_k['id']] + carton_k['length'] * orientation[carton_k['id']]["ly"] + carton_k['width'] *
                orientation[carton_k['id']]["wy"] + carton_k['height'] * orientation[carton_k['id']]["hy"] <= yi[
                    carton_i['id']] + (1 - rel["dik"]) * M, name=f"no_overlap_y_d_{carton_i['id']}_{carton_k['id']}")
            model.addConstr(
                zi[carton_i['id']] + carton_i['length'] * orientation[carton_i['id']]["lz"] + carton_i['width'] *
                orientation[carton_i['id']]["wz"] + carton_i['height'] * orientation[carton_i['id']]["hz"] <= zi[
                    carton_k['id']] + (1 - rel["eik"]) * M, name=f"no_overlap_z_e_{carton_i['id']}_{carton_k['id']}")
            model.addConstr(
                zi[carton_k['id']] + carton_k['length'] * orientation[carton_k['id']]["lz"] + carton_k['width'] *
                orientation[carton_k['id']]["wz"] + carton_k['height'] * orientation[carton_k['id']]["hz"] <= zi[
                    carton_i['id']] + (1 - rel["fik"]) * M, name=f"no_overlap_z_f_{carton_i['id']}_{carton_k['id']}")
    
    # Stability constraints
    '''
    for every pair of cartons, if i is being supported by j, the following must hold true:
        1. The z-coordinate of the Front Left Bottom (FLB) of i must be greater than the z-coordinate of the FLB of j
        2. The z-coordinate of the Rear Right Top (RRT) of i must be less than the z-coordinate of the RRT of j
        3. The x-coordinate of the FLB of i must be greater than the x-coordinate of the RRT of j
        4. The x-coordinate of the RRT of i must be less than the x-coordinate of the FLB of j
        5. The y-coordinate of the FLB of i must be greater than the y-coordinate of the RRT of j
        6. The y-coordinate of the RRT of i must be less than the y-coordinate of the FLB of j
    '''
    for i in range(len(cartons)):
        model.addConstr(zi[cartons[i]['id']] <= (1 - orientation[cartons[i]['id']]["ground"]) * M, name=f"touching_ground_{carton['id']}")
        model.addConstr(orientation[carton['id']]['ground'] + sum(relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"] for j in range(len(cartons)) if i!=j) == 1)
        for j in range(len(cartons)):
            if (i==j):
                continue
            model.addConstr(zi[cartons[i]['id']] <= zi[cartons[j]['id']] + cartons[j]['height'] * orientation[cartons[j]['id']]["hz"] + 
                            cartons[j]['length'] * orientation[cartons[j]['id']]["lz"] + cartons[j]['width'] * orientation[cartons[j]['id']]["wz"] +
                            (1 - relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"]) * M)
            model.addConstr(zi[cartons[i]['id']] + (1 - relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"]) * M >= zi[cartons[j]['id']] + 
                            cartons[j]['height'] * orientation[cartons[j]['id']]["hz"] + cartons[j]['length'] * orientation[cartons[j]['id']]["lz"] + cartons[j]['width'] * orientation[cartons[j]['id']]["wz"])
            model.addConstr(xi[cartons[i]['id']] + cartons[i]['length'] * orientation[cartons[i]['id']]["lx"] + cartons[i]['width'] * orientation[cartons[i]['id']]["wx"] +
                            cartons[i]['height'] * orientation[cartons[i]['id']]["hx"] <= xi[cartons[j]['id']] + cartons[j]['length'] * orientation[cartons[j]['id']]["lx"] + cartons[j]['width'] * orientation[cartons[j]['id']]["wx"] +
                            cartons[j]['height'] * orientation[cartons[j]['id']]["hx"] + stability_threshold * (xi[cartons[j]['id']] + cartons[j]['length'] * orientation[cartons[j]['id']]["lx"] + cartons[j]['width'] * orientation[cartons[j]['id']]["wx"] +
                            cartons[j]['height'] * orientation[cartons[j]['id']]["hx"] - xi[cartons[j]['id']]) + M * (1 - relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"]))
            model.addConstr(xi[cartons[i]['id']] <= xi[cartons[j]['id']] + stability_threshold * (xi[cartons[j]['id']] + cartons[j]['length'] * orientation[cartons[j]['id']]["lx"] + cartons[j]['width'] * orientation[cartons[j]['id']]["wx"] +
                            cartons[j]['height'] * orientation[cartons[j]['id']]["hx"] - xi[cartons[j]['id']]) + M * (1 - relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"])) 
            model.addConstr(yi[cartons[i]['id']] + cartons[i]['length'] * orientation[cartons[i]['id']]["ly"] + cartons[i]['width'] * orientation[cartons[i]['id']]["wy"] +
                            cartons[i]['height'] * orientation[cartons[i]['id']]["hy"] <= yi[cartons[j]['id']] + cartons[j]['length'] * orientation[cartons[j]['id']]["ly"] + cartons[j]['width'] * orientation[cartons[j]['id']]["wy"] +
                            cartons[j]['height'] * orientation[cartons[j]['id']]["hy"] + stability_threshold * (yi[cartons[j]['id']] + cartons[j]['length'] * orientation[cartons[j]['id']]["ly"] + cartons[j]['width'] * orientation[cartons[j]['id']]["wy"] +
                            cartons[j]['height'] * orientation[cartons[j]['id']]["hy"] - yi[cartons[j]['id']]) + M * (1 - relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"]))
            model.addConstr(yi[cartons[i]['id']] <= yi[cartons[j]['id']] + stability_threshold * (yi[cartons[j]['id']] + cartons[j]['length'] * orientation[cartons[j]['id']]["ly"] + cartons[j]['width'] * orientation[cartons[j]['id']]["wy"] +
                            cartons[j]['height'] * orientation[cartons[j]['id']]["hy"] - yi[cartons[j]['id']]) + M * (1 - relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"])) 
            model.addConstr(sum(sij[cartons[i]['id'],container['id']] * sij[cartons[j]['id'],container['id']] for container in containers) >= relative_position[(cartons[i]['id'], cartons[j]['id'])]["support"])
   
   
    
    model.setParam('TimeLimit', timeout)    # Stop after timout
    model.optimize()
    if model.status == GRB.OPTIMAL:
        solution = []                       # if optimal solution is found, update the result
        for container in containers:
            for carton in cartons:
                if sij[(carton['id'], container['id'])].X > 0.5:    # used to check if sij variable is one in optimal solution
                    solution.append({
                            "carton_id": carton['id'],
                            "container_id": container['id'],
                            "x": xi[carton['id']].X,
                            "y": yi[carton['id']].X,
                            "z": zi[carton['id']].X,
                            "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] * orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']]["hx"].X,
                            "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] * orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']]["hy"].X,
                            "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] * orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']]["hz"].X
                        })
        return solution
    