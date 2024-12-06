import gurobipy as gp
from gurobipy import GRB
# from utils.cartons import cartons
# from utils.containers import containers
from LPP.package_to_carton import get_from_greedy, get_specific_from_greedy


# containers = containers_specific(specific_container)
# init, cartons, assigned_solutions = get_specific_from_greedy(filename, specific_container)
def cut_short_rem(cartons, length):
    rem = []
    ass = []
    for carton in cartons:
        if carton['container_id'] == "-1" or carton['container_id'] == -1:
            rem.append(carton)
        else:
            ass.append(carton)
    rem.sort( key=lambda x: -(x['cost']**2)/(x['length']*x['width']*x['height']))
    ass = ass + rem[0:length]
    rem = rem[length:]
    return ass, rem
def cut_short_rem_adding(cartons, length):
    rem = []
    ass = []
    for carton in cartons:
        if carton['container_id'] == "-1" or carton['container_id'] == -1:
            rem.append(carton)
        else:
            ass.append(carton)
    rem.sort(key=lambda x: (x['length']*x['width']*x['height']))
    ass = ass + rem[0:length]
    rem = rem[length:]
    print("rem ")
    print(ass)
    return ass, rem
def all_swaps(cartons, containers, init, assigned_solutions, timeout = 600):
    print(containers)
    print(len(cartons))
    # print(len(assigned_solutions))
    model = gp.Model("3D_Container_Loading_with_Relative_Positioning")
    # model.Params.LogToConsole = 1  # Show optimization logs
    model.setParam('TimeLimit', timeout)  # Set time limit to 10 minutes
    # Define constants
    M = 100000  # Large constant for "big-M" constraints
    cartons, rem = cut_short_rem(cartons, 40)
    rem_to_sol = []
    for obj in rem:
        cart = {
            'carton_id': obj['id'],
            'container_id': -1,
            'DimX': obj['length'],
            'DimY': obj['width'],
            'DimZ': obj['height'],
            'weight':obj['weight'],
            'cost': obj['cost'],
            'Priority': obj['Priority']
        }
        rem_to_sol.append(cart)

    assigned_solutions += rem_to_sol
    additional_cost = 0 + sum(carton['cost'] for carton in rem)
    cartons.sort(key=lambda x: x['id'])
    # Decision variables
    sij = {}  # Binary: carton i assigned to container j
    xi, yi, zi = {}, {}, {}  # Continuous: coordinates of FLB corner of carton i
    nj = {}
    orientation = {}  # Binary variables for carton orientation (rotation matrix)
    relative_position = {}  # Binary variables for relative positions (aik, bik, cik, dik, eik, fik)
    # Add variables
    x = model.addVar(vtype=GRB.BINARY, name="1")
    model.addConstr(x == 1)
    # extra constraints redundant
    # for container in containers:
    #     nj[container['id']] = model.addVar(vtype=GRB.INTEGER, name=f"n_{container['id']}")
    print(containers)
    for carton in cartons:
        for container in containers:
            sij[(carton['id'], container['id'])] = model.addVar(vtype=GRB.BINARY,
                                                                name=f"s_{carton['id']}_{container['id']}")
        xi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"x_{carton['id']}")
        yi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"y_{carton['id']}")
        zi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"z_{carton['id']}")
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
        }

    # Relative positioning variables: aik, bik, cik, dik, eik, fik
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

    # Constraints
    # 1. Assign each carton to exactly one container
    for carton in cartons:
        model.addConstr(sum(sij[(carton['id'], container['id'])] for container in containers) <= 1,
                        name=f"assign_{carton['id']}")

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

    # 4. Prevent overlapping of cartons with aik, bik, cik, dik, eik, fik
    for container in containers:
        # weight constraints
        model.addConstr(
            sum((sij[(carton['id'], container['id'])] * carton['weight']) for carton in cartons) <= container['weight'],
            name=f"weight_limit_constr{container['id']}")
        for i in range(len(cartons)):
            for k in range(i + 1, len(cartons)):
                carton_i = cartons[i]
                carton_k = cartons[k]
                rel = relative_position[(carton_i['id'], carton_k['id'])]
                model.addConstr((rel["aik"] + rel["bik"] + rel["cik"] + rel["dik"] + rel["eik"] + rel["fik"] >=
                                 sij[(carton_i['id'], container['id'])] + sij[(carton_k['id'], container['id'])] - x),
                                name=f"relative_sum_{carton_i['id']}_{carton_k['id']}_{container['id']}")
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
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

    # add MIP here
    initcost = 0
    # print(init)
    # for carton in cartons:
    #     if sum(init['sij'][carton['id'], container['id']] for container in containers) == 0:
    #         print(carton['id'])
    #         initcost += carton['cost']
    print("initCost")
    print(initcost)
    ids = []
    for carton in cartons:
        ids.append(carton['id'])
    for (carton_id, container_id), value in init['sij'].items():
        if carton_id not in ids:
            continue
        sij[(carton_id, container_id)].Start = value
    for carton_id, value in init['xi'].items():
        if carton_id not in ids:
            continue
        xi[carton_id].Start = value
    for carton_id, value in init['yi'].items():
        if carton_id not in ids:
            continue
        yi[carton_id].Start = value
    for carton_id, value in init['zi'].items():
        if carton_id not in ids:
            continue
        zi[carton_id].Start = value
    for carton_id, orientations in init['orientation'].items():
        if carton_id not in ids:
            continue
        for orient, value in orientations.items():
            orientation[carton_id][orient].Start = value
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
            carton_i = cartons[i]
            carton_k = cartons[k]
            for orient, value in init['relative_position'][(carton_i['id'], carton_k['id'])].items():
                if (carton_i['id'] not in ids) or (carton_k['id'] not in ids):
                    continue
                relative_position[(carton_i['id'], carton_k['id'])][orient].Start = value

    # x = 5000 * sum(max(sij[(carton['id'], container['id'])] * carton['priority'] for carton in cartons) for container in containers)

    penalty = sum(
        (1 - (sum(sij[(carton['id'], container['id'])] for container in containers))) * carton['cost'] for carton in
        cartons) + additional_cost
    model.setObjective(penalty, GRB.MINIMIZE)
    model.optimize()
    # Extract the solution
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT or model.status == GRB.INTERRUPTED or model.status == GRB.SUBOPTIMAL:
        print("Optimal solution found. Checking constraints:")
        model.printQuality()
        solution = []
        for container in containers:
            for carton in cartons:
                if sij[(carton['id'], container['id'])].X > 0.5:
                    solution.append({
                        "carton_id": carton['id'],
                        "container_id": container['id'],
                        "x": xi[carton['id']].X,
                        "y": yi[carton['id']].X,
                        "z": zi[carton['id']].X,
                        "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
                                orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
                                    "hx"].X,
                        "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
                                orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
                                    "hy"].X,
                        "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
                                orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']][
                                    "hz"].X,
                        "weight": carton['weight'],
                        "cost": carton['cost']
                    })
                    # Print aik and bik variables
        for sol in assigned_solutions:
            solution.append(sol)
        for carton in cartons:
            if sum(sij[(carton['id'], container['id'])].X for container in containers) == 0:
                solution.append({
                    "carton_id": carton['id'],
                    "container_id": -1,
                    "x": -1,
                    "y": -1,
                    "z": -1,
                    "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
                            orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
                                "hx"].X,
                    "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
                            orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
                                "hy"].X,
                    "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
                            orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']][
                                "hz"].X,
                    "weight": carton['weight'],
                    "cost": carton['cost']
                })
        print(solution)
        return solution
    else:
        print("No feasible solution found.")

def multi_containers_extra(cartons, containers, assigned_solutions, length, timeout = 60):
    print("MODEL STARTED")
    model = gp.Model("3D_Container_Loading_with_Relative_Positioning")
    model.setParam('TimeLimit', timeout)    # Stop after 120 seconds
    # model.Params.LogToConsole = 1  # Show optimization logs
    # model.setParam('TimeLimit', timeout)  # Set time limit to 10 minutes
    # Define constants
    M = 100000  # Large constant for "big-M" constraints
    additional_cost = 0
    cartons, rem = cut_short_rem_adding(cartons, length)
    rem_to_sol = []
    for obj in rem:
        cart = {
            'carton_id': obj['id'],
            'container_id': -1,
            'DimX': obj['length'],
            'DimY': obj['width'],
            'DimZ': obj['height'],
            'weight': obj['weight'],
            'cost': obj['cost'],
            'Priority': obj['Priority']
        }
        rem_to_sol.append(cart)

    assigned_solutions += rem_to_sol
    cartons.sort(key=lambda x: x['id'])
    for carton in rem:
        if carton['container_id'] == "-1" or carton['container_id'] == -1:
            additional_cost += carton['cost']

    new_cost = additional_cost

    # Decision variables
    sij = {}  # Binary: carton i assigned to container j
    xi, yi, zi = {}, {}, {}  # Continuous: coordinates of FLB corner of carton i
    nj = {}
    orientation = {}  # Binary variables for carton orientation (rotation matrix)
    relative_position = {}  # Binary variables for relative positions (aik, bik, cik, dik, eik, fik)
    # Add variables
    x = model.addVar(vtype=GRB.BINARY, name="1")
    model.addConstr(x == 1)
    # extra constraints redundant
    # for container in containers:
    #     nj[container['id']] = model.addVar(vtype=GRB.INTEGER, name=f"n_{container['id']}")
    for carton in cartons:
        for container in containers:
            sij[(carton['id'], container['id'])] = model.addVar(vtype=GRB.BINARY,
                                                                name=f"s_{carton['id']}_{container['id']}")
        xi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"x_{carton['id']}")
        yi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"y_{carton['id']}")
        zi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"z_{carton['id']}")
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
        }

    # Relative positioning variables: aik, bik, cik, dik, eik, fik
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

    # Constraints
    # 1. Assign each carton to exactly one container
    for carton in cartons:
        model.addConstr(sum(sij[(carton['id'], container['id'])] for container in containers) == 1,
                        name=f"assign_{carton['id']}")

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

    # 4. Prevent overlapping of cartons with aik, bik, cik, dik, eik, fik
    for container in containers:
        # weight constraints
        model.addConstr(
            sum((sij[(carton['id'], container['id'])] * carton['weight']) for carton in cartons) <= container['weight'],
            name=f"weight_limit_constr{container['id']}")
        for i in range(len(cartons)):
            for k in range(i + 1, len(cartons)):
                carton_i = cartons[i]
                carton_k = cartons[k]
                rel = relative_position[(carton_i['id'], carton_k['id'])]
                model.addConstr((rel["aik"] + rel["bik"] + rel["cik"] + rel["dik"] + rel["eik"] + rel["fik"] >=
                                 sij[(carton_i['id'], container['id'])] + sij[(carton_k['id'], container['id'])] - x),
                                name=f"relative_sum_{carton_i['id']}_{carton_k['id']}_{container['id']}")
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
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
    model.optimize()
    # Extract the solution
    if model.status == GRB.OPTIMAL or model.status == GRB.SUBOPTIMAL:
        print("Optimal solution found. Checking constraints:")
        model.printQuality()
        solution = []
        print("succesfully added new cost = ", new_cost)
        for container in containers:
            for carton in cartons:
                if sij[(carton['id'], container['id'])].X > 0.5:
                    solution.append({
                        "carton_id": carton['id'],
                        "container_id": container['id'],
                        "x": xi[carton['id']].X,
                        "y": yi[carton['id']].X,
                        "z": zi[carton['id']].X,
                        "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
                                orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
                                    "hx"].X,
                        "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
                                orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
                                    "hy"].X,
                        "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
                                orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']][
                                    "hz"].X,
                        "weight": carton['weight'],
                        "cost": carton['cost']
                    })
                    # Print aik and bik variables
        for sol in assigned_solutions:
            solution.append(sol)
        for carton in cartons:
            if sum(sij[(carton['id'], container['id'])].X for container in containers) == 0:
                solution.append({
                    "carton_id": carton['id'],
                    "container_id": -1,
                    "x": -1,
                    "y": -1,
                    "z": -1,
                    "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
                            orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
                                "hx"].X,
                    "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
                            orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
                                "hy"].X,
                    "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
                            orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']][
                                "hz"].X,
                    "weight": carton['weight'],
                    "cost": carton['cost']
                })
        print("printing solution ", solution)
        return solution
    else:
        print("No feasible solution found. checking next")
def with_stability(cartons, containers, init, assigned_solutions, stability_constraints):
    # print(containers)
    # print(len(cartons))
    # cartons = cartons[:2]
    # print(cartons)
    # print(len(assigned_solutions))
    model = gp.Model("3D_Container_Loading_with_Relative_Positioning")
    # model.Params.LogToConsole = 1  # Show optimization logs
    # model.setParam('TimeLimit', timeout)  # Set time limit to 10 minutes
    # Define constants
    M = 100000  # Large constant for "big-M" constraints
    f = 1
    # Decision variables
    sij = {}  # Binary: carton i assigned to container j
    xi, yi, zi = {}, {}, {}  # Continuous: coordinates of FLB corner of carton i
    orientation = {}  # Binary variables for carton orientation (rotation matrix)
    relative_position = {}  # Binary variables for relative positions (aik, bik, cik, dik, eik, fik)
    wij = {}
    wi = {}
    Pcij = {}
    # Add variables
    x = model.addVar(vtype=GRB.BINARY, name="1")
    model.addConstr(x == 1)
    # extra constraints redundant
    # for container in containers:
    #     nj[container['id']] = model.addVar(vtype=GRB.INTEGER, name=f"n_{container['id']}")
    print(containers)
    for container in containers:
        for carton1 in cartons:
            for carton2 in cartons:
                if carton1['id'] == carton2['id']:
                    continue
                Pcij[(carton1['id'], carton2['id'], container['id'])] = model.addVar(vtype=GRB.BINARY,
                                                                                     name=f"Pcij_{carton1['id']}_{carton2['id']}_{container['id']}")
    for carton in cartons:
        wi[carton['id']] = model.addVar(vtype=GRB.BINARY, name=f"weight_{carton['id']}")
        for container in containers:
            sij[(carton['id'], container['id'])] = model.addVar(vtype=GRB.BINARY,
                                                                name=f"s_{carton['id']}_{container['id']}")
        xi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"x_{carton['id']}")
        yi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"y_{carton['id']}")
        zi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"z_{carton['id']}")
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
        }

    # Relative positioning variables: aik, bik, cik, dik, eik, fik
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

    # stability :
    for carton1 in cartons:
        for carton2 in cartons:
            if carton1['id'] == carton2['id']:
                continue
            wij[(carton1['id'], carton2['id'])] = model.addVar(vtype=GRB.BINARY,
                                                               name=f"wij_{carton1['id']}_{carton2['id']}")
    for carton in cartons:
        model.addConstr(zi[carton['id']] <= (1 - wi[carton['id']]) * M, name=f"doesnt_go_underground{carton['id']}")
        model.addConstr(wi[carton['id']] + sum(
            wij[(carton['id'], carton2['id'])] for carton2 in cartons if carton['id'] != carton2['id']) + (
                                    1 - sum(sij[(carton['id'], container['id'])] for container in containers)) * M >= 1,
                        name=f"platform_{carton['id']}")
    for carton1 in cartons:
        for carton2 in cartons:
            if carton1['id'] == carton2['id']:
                continue
            orients1 = orientation[carton1['id']]
            orients2 = orientation[carton2['id']]
            model.addConstr(zi[carton1['id']] <= zi[carton2['id']] + carton2['length'] * orients2["lz"] +
                            carton2['width'] * orients2["wz"] +
                            carton2['height'] * orients2["hz"] + (1 - wij[(carton1['id'], carton2['id'])]) * M,
                            name=f"stability_z_{carton1['id']}_{carton2['id']}")
            model.addConstr(
                zi[carton1['id']] + (1 - wij[(carton1['id'], carton2['id'])]) * M >= zi[carton2['id']] + zi[
                    carton2['id']] + carton2['length'] * orients2["lz"] +
                carton2['width'] * orients2["wz"] +
                carton2['height'] * orients2["hz"],
                name=f"stability_z_{carton1['id']}_{carton2['id']}")
            model.addConstr(
                xi[carton1['id']] + carton1['length'] * orients1["lx"] + carton1['width'] * orients1["wx"] + carton1[
                    'height'] * orients1["hx"]
                <= xi[carton2['id']] + carton2['length'] * orients2["lx"] + carton2['width'] * orients2["wx"] + carton2[
                    'height'] * orients2["hx"] +
                f * (carton1['length'] * orients1["lx"] + carton1['width'] * orients1["wx"] + carton1['height'] *
                     orients1["hx"]) +
                M * (1 - wij[(carton1['id'], carton2['id'])]), name=f"stability_x_1{carton1['id']}_{carton2['id']}")
            model.addConstr(xi[carton1['id']] <= xi[carton2['id']] +
                            f * (carton1['length'] * orients1["lx"] + carton1['width'] * orients1["wx"] + carton1['height'] * orients1["hx"]) +
                            M * (1 - wij[(carton1['id'], carton2['id'])]),
                            name=f"stability_x_2{carton1['id']}_{carton2['id']}")
            model.addConstr(
                yi[carton1['id']] + carton1['length'] * orients1["ly"] + carton1['width'] * orients1["wy"] + carton1[
                    'height'] * orients1["hy"]
                <= yi[carton2['id']] + carton2['length'] * orients2["ly"] + carton2['width'] * orients2["wy"] + carton2[
                    'height'] * orients2["hy"] +
                f * (carton1['length'] * orients1["ly"] + carton1['width'] * orients1["wy"] + carton1['height'] *
                     orients1["hy"]) +
                M * (1 - wij[(carton1['id'], carton2['id'])]), name=f"stability_y_1{carton1['id']}_{carton2['id']}")
            model.addConstr(yi[carton1['id']] <= yi[carton2['id']] +
                            f * (carton1['length'] * orients1["ly"] + carton1['width'] * orients1["wy"] + carton1[
                'height'] * orients1["hy"]) +
                            M * (1 - wij[(carton1['id'], carton2['id'])]),
                            name=f"stability_y_2{carton1['id']}_{carton2['id']}")
            model.addConstr(sum(Pcij[(carton1['id'], carton2['id'], container['id'])] for container in containers) >=
                            wij[(carton1['id'], carton2['id'])], name=f"stability_sum_{carton1['id']}_{carton2['id']}")
    for container in containers:
        for carton1 in cartons:
            for carton2 in cartons:
                if carton1['id'] == carton2['id']:
                    continue
                model.addConstr(
                    2 * Pcij[(carton1['id'], carton2['id'], container['id'])] <= sij[(carton1['id'], container['id'])] +
                    sij[(carton2['id'], container['id'])],
                    name=f"stability_{carton1['id']}_{carton2['id']}_{container['id']}")
                model.addConstr(
                    2 * Pcij[(carton1['id'], carton2['id'], container['id'])] >= sij[carton1['id'], container['id']] +
                    sij[(carton2['id'], container['id'])],
                    name=f"stability_{carton1['id']}_{carton2['id']}_{container['id']}")

    # Constraints
    # 1. Assign each carton to exactly one container
    for carton in cartons:
        model.addConstr(sum(sij[(carton['id'], container['id'])] for container in containers) <= 1,
                        name=f"assign_{carton['id']}")

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

    # 4. Prevent overlapping of cartons with aik, bik, cik, dik, eik, fik
    for container in containers:
        # weight constraints
        model.addConstr(
            sum((sij[(carton['id'], container['id'])] * carton['weight']) for carton in cartons) <= container['weight'],
            name=f"weight_limit_constr{container['id']}")
        for i in range(len(cartons)):
            for k in range(i + 1, len(cartons)):
                carton_i = cartons[i]
                carton_k = cartons[k]
                rel = relative_position[(carton_i['id'], carton_k['id'])]
                model.addConstr((rel["aik"] + rel["bik"] + rel["cik"] + rel["dik"] + rel["eik"] + rel["fik"] >=
                                 sij[(carton_i['id'], container['id'])] + sij[(carton_k['id'], container['id'])] - x),
                                name=f"relative_sum_{carton_i['id']}_{carton_k['id']}_{container['id']}")
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
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

    # add MIP here
    initcost = 0
    # sij[('P-10', 'U6')].Start = 1
    # sij[('P-100', 'U6')] = 1
    # xi['P-10'].Start = 0
    # yi['P-10'].Start = 0
    # zi['P-10'].Start = 0
    # xi['P-100'].Start = 0
    # yi['P-100'].Start = 0
    # zi['P-100'].Start = 88
    # orientation['P-10']['lx'].Start = 1
    # orientation['P-10']['wx'].Start = 0
    # orientation['P-10']['hx'].Start = 0
    # orientation['P-10']['ly'].Start = 0
    # orientation['P-10']['wy'].Start = 1
    # orientation['P-10']['hy'].Start = 0
    # orientation['P-10']['lz'].Start = 0
    # orientation['P-10']['wz'].Start = 0
    # orientation['P-10']['hz'].Start = 1
    # orientation['P-100']['lx'].Start = 1
    # orientation['P-100']['wx'].Start = 0
    # orientation['P-100']['hx'].Start = 0
    # orientation['P-100']['ly'].Start = 0
    # orientation['P-100']['wy'].Start = 1
    # orientation['P-100']['hy'].Start = 0
    # orientation['P-100']['lz'].Start = 0
    # orientation['P-100']['wz'].Start = 0
    # orientation['P-100']['hz'].Start = 1
    # relative_position[('P-10', 'P-100')]['aik'].Start = 0
    # relative_position[('P-10', 'P-100')]['bik'].Start = 0
    # relative_position[('P-10', 'P-100')]['cik'].Start = 0
    # relative_position[('P-10', 'P-100')]['dik'].Start = 0
    # relative_position[('P-10', 'P-100')]['eik'].Start = 1
    # relative_position[('P-10', 'P-100')]['fik'].Start = 0
    # wij[('P-10','P-100')].Start = 0
    # wij[('P-100','P-10')].Start = 1
    # wi['P-10'].Start = 1
    # wi['P-100'].Start = 0
    # Pcij[('P-10', 'P-100', 'U6')].Start = 1
    # Pcij[('P-100', 'P-10', 'U6')].Start = 1



    # print(init)
    # for carton in cartons:
    #     if sum(init['sij'][carton['id'], container['id']] for container in containers) == 0:
    #         print(carton['id'])
    #         initcost += carton['cost']
    # print("initCost")
    # print(initcost)
    # for (carton1_id, carton2_id), value in stability_constraints['wij'].items():
    #     wij[(carton1_id, carton2_id)].Start = value
    #     print(carton1_id, carton2_id, value)
    # for (carton1_id, carton2_id, container_id), value in stability_constraints['Pcij'].items():
    #     Pcij[(carton1_id, carton2_id, container_id)].Start = value
    #     print(carton1_id, carton2_id, container_id, value)
    #
    # for carton_id, value in stability_constraints['wi'].items():
    #     wi[carton_id].Start = value
    #     print(carton_id, value)
    #
    # for (carton_id, container_id), value in init['sij'].items():
    #     sij[(carton_id, container_id)].Start = value
    # for carton_id, value in init['xi'].items():
    #     xi[carton_id].Start = value
    # for carton_id, value in init['yi'].items():
    #     yi[carton_id].Start = value
    # for carton_id, value in init['zi'].items():
    #     zi[carton_id].Start = value
    # for carton_id, orientations in init['orientation'].items():
    #     for orient, value in orientations.items():
    #         orientation[carton_id][orient].Start = value
    # for i in range(len(cartons)):
    #     for k in range(i + 1, len(cartons)):
    #         carton_i = cartons[i]
    #         carton_k = cartons[k]
    #         for orient, value in init['relative_position'][(carton_i['id'], carton_k['id'])].items():
    #             relative_position[(carton_i['id'], carton_k['id'])][orient].Start = value

    # x = 5000 * sum(max(sij[(carton['id'], container['id'])] * carton['priority'] for carton in cartons) for container in containers)

    penalty = sum(
        (1 - (sum(sij[(carton['id'], container['id'])] for container in containers))) * carton['cost'] for carton in
        cartons)
    model.setObjective(penalty, GRB.MINIMIZE)
    model.optimize()
    # Extract the solution
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT or model.status == GRB.INTERRUPTED or model.status == GRB.SUBOPTIMAL:
        print("Optimal solution found. Checking constraints:")
        model.printQuality()
        solution = []
        for container in containers:
            for carton in cartons:
                if sij[(carton['id'], container['id'])].X > 0.5:
                    solution.append({
                        "carton_id": carton['id'],
                        "container_id": container['id'],
                        "x": xi[carton['id']].X,
                        "y": yi[carton['id']].X,
                        "z": zi[carton['id']].X,
                        "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
                                orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
                                    "hx"].X,
                        "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
                                orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
                                    "hy"].X,
                        "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
                                orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']][
                                    "hz"].X,
                        "weight": carton['weight'],
                        "cost": carton['cost']
                    })
                    # Print aik and bik variables
        # for sol in assigned_solutions:
        #     solution.append(sol)
        # for carton in cartons:
        #     if sum(sij[(carton['id'], container['id'])].X for container in containers) == 0:
        #         solution.append({
        #             "carton_id": carton['id'],
        #             "container_id": -1,
        #             "x": -1,
        #             "y": -1,
        #             "z": -1,
        #             "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
        #                     orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
        #                         "hx"].X,
        #             "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
        #                     orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
        #                         "hy"].X,
        #             "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
        #                     orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']][
        #                         "hz"].X,
        #             "weight": carton['weight'],
        #             "cost": carton['cost']
        #         })
        return solution
    else:
        print("No feasible solution found.")

def add_extra(cartons, containers, init, assigned_solutions):
    model = gp.Model("3D_Container_Loading_with_Relative_Positioning")
    # model.Params.LogToConsole = 1  # Show optimization logs
    # containers = dict(containers)
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
    # extra constraints redundant
    # for container in containers:
    #     nj[container['id']] = model.addVar(vtype=GRB.INTEGER, name=f"n_{container['id']}")
    for carton in cartons:
        for container in containers:
            sij[(carton['id'], container['id'])] = model.addVar(vtype=GRB.BINARY,
                                                                name=f"s_{carton['id']}_{container['id']}")
        xi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"x_{carton['id']}")
        yi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"y_{carton['id']}")
        zi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"z_{carton['id']}")
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
        }

    # Relative positioning variables: aik, bik, cik, dik, eik, fik
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

    # Constraints
    # 1. Assign each carton to exactly one container
    for carton in cartons:
        if carton['container_id'] == "-1":
            print(carton['id'])
            model.addConstr(sum(sij[(carton['id'], container['id'])] for container in containers) == 1,
                            name=f"assign_{carton['id']}")
        else:
            for container in containers:
                model.addConstr(sij[(carton['id'], container['id'])] == 0,
                                name=f"assign_{carton['id']}_{container['id']}")
            model.addConstr(sij[(carton['id'], carton['container_id'])] == 1, name=f"assign_{carton['id']}")

        # model.addConstr(sum(sij[(carton['id'], container['id'])] for container in containers) <= 1,
        #                 name=f"assign_{carton['id']}")

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

    # 4. Prevent overlapping of cartons with aik, bik, cik, dik, eik, fik
    for container in containers:
        # weight constraints
        model.addConstr(
            sum((sij[(carton['id'], container['id'])] * carton['weight']) for carton in cartons) <= container['weight'],
            name=f"weight_limit_constr{container['id']}")
        for i in range(len(cartons)):
            for k in range(i + 1, len(cartons)):
                carton_i = cartons[i]
                carton_k = cartons[k]
                rel = relative_position[(carton_i['id'], carton_k['id'])]
                model.addConstr((rel["aik"] + rel["bik"] + rel["cik"] + rel["dik"] + rel["eik"] + rel["fik"] >=
                                 sij[(carton_i['id'], container['id'])] + sij[(carton_k['id'], container['id'])] - x),
                                name=f"relative_sum_{carton_i['id']}_{carton_k['id']}_{container['id']}")
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
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

    # add MIP here

    for (carton_id, container_id), value in init['sij'].items():
        sij[(carton_id, container_id)].Start = value
    for carton_id, value in init['xi'].items():
        xi[carton_id].Start = value
    for carton_id, value in init['yi'].items():
        yi[carton_id].Start = value
    for carton_id, value in init['zi'].items():
        zi[carton_id].Start = value
    for carton_id, orientations in init['orientation'].items():
        for orient, value in orientations.items():
            orientation[carton_id][orient].Start = value
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
            carton_i = cartons[i]
            carton_k = cartons[k]
            for orient, value in init['relative_position'][(carton_i['id'], carton_k['id'])].items():
                relative_position[(carton_i['id'], carton_k['id'])][orient].Start = value

    # x = 5000 * sum(max(sij[(carton['id'], container['id'])] * carton['priority'] for carton in cartons) for container in containers)

    # penalty = sum(
    #     (1 - (sum(sij[(carton['id'], container['id'])] for container in containers))) * carton['cost'] for carton in
    #     cartons)
    # model.setObjective(penalty, GRB.MINIMIZE)
    # model.optimize()
    # Extract the solution
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT or model.status == GRB.INTERRUPTED or model.status == GRB.SUBOPTIMAL:
        print("Optimal solution found. Checking constraints:")
        model.printQuality()
        solution = []
        for container in containers:
            for carton in cartons:
                if sij[(carton['id'], container['id'])].X > 0.5:
                    solution.append({
                        "carton_id": carton['id'],
                        "container_id": container['id'],
                        "x": xi[carton['id']].X,
                        "y": yi[carton['id']].X,
                        "z": zi[carton['id']].X,
                        "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
                                orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
                                    "hx"].X,
                        "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
                                orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
                                    "hy"].X,
                        "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
                                orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']][
                                    "hz"].X,
                        "weight": carton['weight'],
                        "cost": carton['cost'],
                        "priority": carton['priority']
                    })
                    # Print aik and bik variables
        for sol in assigned_solutions:
            solution.append(sol)
        return solution
    else:
        print("No feasible solution found.")

def complete_LPP(cartons, containers, init):
    # Create a model
    model = gp.Model("3D_Container_Loading_with_Relative_Positioning")
    # model.Params.LogToConsole = 1  # Show optimization logs
    model.setParam('OutputFlag', 1)  # Ensure logging to the terminal is on (optional)
    model.setParam('LogFile', 'gurobi_log_final.txt')  # Log all output to this file

    # redefine termination criteria
    # Define constants
    M = 100000  # Large constant for "big-M" constraints

    # Decision variables
    sij = {}  # Binary: carton i assigned to container j
    xi, yi, zi = {}, {}, {}  # Continuous: coordinates of FLB corner of carton i
    pj = {}
    orientation = {}  # Binary variables for carton orientation (rotation matrix)
    relative_position = {}  # Binary variables for relative positions (aik, bik, cik, dik, eik, fik)
    # Add variables
    x = model.addVar(vtype=GRB.BINARY, name="1")
    model.addConstr(x == 1)
    # extra constraints redundant
    # for container in containers:
    #     nj[container['id']] = model.addVar(vtype=GRB.INTEGER, name=f"n_{container['id']}")
    for container in containers:
        print(container['id'])
        pj[container['id']] = model.addVar(vtype=GRB.BINARY, name=f"contains_priority_{container['id']}")
    for carton in cartons:
        for container in containers:
            sij[(carton['id'], container['id'])] = model.addVar(vtype=GRB.BINARY,
                                                                name=f"s_{carton['id']}_{container['id']}")
        xi[carton['id']] = model.addVar(vtype=GRB.CONTINUOUS, name=f"x_{carton['id']}")
        yi[carton['id']] = model.addVar(vtype=GRB.CONTINUOUS, name=f"y_{carton['id']}")
        zi[carton['id']] = model.addVar(vtype=GRB.CONTINUOUS, name=f"z_{carton['id']}")
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
        }

    # Relative positioning variables: aik, bik, cik, dik, eik, fik
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

    # Constraints
    # 1. Assign each carton to exactly one container
    for carton in cartons:
        model.addConstr(sum(sij[(carton['id'], container['id'])] for container in containers) <= 1,
                        name=f"assign_{carton['id']}")
    # redundant constraints
    # for container in containers:
    #     model.addConstr(sum(sij[(carton['id'], container['id'])] for carton in cartons) <= M*nj[container['id']],
    #  name=f"assign_{container['id']}")

    # check for priority packages spread :
    for container in containers:
        for carton in cartons:
            model.addConstr(pj[container['id']] >= (sij[(carton['id'], container['id'])] * carton['priority']),
                            name=f"priority_{carton['id']}_{container['id']}")

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

    # 4. Prevent overlapping of cartons with aik, bik, cik, dik, eik, fik
    for container in containers:
        # weight constraints
        model.addConstr(
            sum((sij[(carton['id'], container['id'])] * carton['weight']) for carton in cartons) <= container['weight'],
            name=f"weight_limit_constr{container['id']}")
        for i in range(len(cartons)):
            for k in range(i + 1, len(cartons)):
                carton_i = cartons[i]
                carton_k = cartons[k]
                rel = relative_position[(carton_i['id'], carton_k['id'])]
                model.addConstr((rel["aik"] + rel["bik"] + rel["cik"] + rel["dik"] + rel["eik"] + rel["fik"] >=
                                 sij[(carton_i['id'], container['id'])] + sij[(carton_k['id'], container['id'])] - x),
                                name=f"relative_sum_{carton_i['id']}_{carton_k['id']}_{container['id']}")
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
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
    temp = 0
    # init = get_from_greedy()
    #MIP
    for (carton_id, container_id), value in init['sij'].items():
        sij[(carton_id, container_id)].Start = value
    for carton_id, value in init['xi'].items():
        xi[carton_id].Start = value
    for carton_id, value in init['yi'].items():
        yi[carton_id].Start = value
    for carton_id, value in init['zi'].items():
        zi[carton_id].Start = value
    for carton_id, orientations in init['orientation'].items():
        for orient, value in orientations.items():
            orientation[carton_id][orient].Start = value
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
            carton_i = cartons[i]
            carton_k = cartons[k]
            for orient, value in init['relative_position'][(carton_i['id'], carton_k['id'])].items():
                relative_position[(carton_i['id'], carton_k['id'])][orient].Start = value
    for container in containers:
        for carton in cartons:
            if carton['priority'] == 1 and init['sij'][(carton['id'], container['id'])] == 1:
                pj[container['id']].Start = 1

    # Objective:
    penalty = 5000 * sum(pj[container['id']] for container in containers) + sum(
        ((1 - (sum(sij[(carton['id'], container['id'])] for container in containers))) * carton['cost']) for carton in
        cartons)
    model.setParam('BarHomogeneous', 1)

    model.setObjective(penalty, GRB.MINIMIZE)
    model.setParam('PoolSolutions', 100)
    model.params.MipGap = 0.00001
    model.optimize()
    # Extract the solution
    if model.status == GRB.OPTIMAL:
        print("Optimal solution found. Checking constraints:")
        for c in model.getConstrs():
            lhs = model.getRow(c).getValue()
            rhs = c.RHS
            print(f"{c.ConstrName}: LHS = {lhs}, RHS = {rhs}, Sense = {c.Sense}")
        model.printQuality()
        solution = []
        for container in containers:
            for carton in cartons:
                if sij[(carton['id'], container['id'])].X > 0.5:
                    solution.append({
                        "carton_id": carton['id'],
                        "container_id": container['id'],
                        "x": xi[carton['id']].X,
                        "y": yi[carton['id']].X,
                        "z": zi[carton['id']].X,
                        "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
                                orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
                                    "hx"].X,
                        "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
                                orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
                                    "hy"].X,
                        "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
                                orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']][
                                    "hz"].X,
                        "weight": carton['weight'].X,
                        "priority": carton['priority'],
                        "cost": carton['cost']
                    })
        print(solution)
        return solution
    else:
        print("No feasible solution found.")


def useless(cartons, containers, init):
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
    # model.Params.LogToConsole = 1  # Show optimization logs

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
    # extra constraints redundant
    # for container in containers:
    #     nj[container['id']] = model.addVar(vtype=GRB.INTEGER, name=f"n_{container['id']}")
    for carton in cartons:
        for container in containers:
            sij[(carton['id'], container['id'])] = model.addVar(vtype=GRB.BINARY,
                                                                name=f"s_{carton['id']}_{container['id']}")
        xi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"x_{carton['id']}")
        yi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"y_{carton['id']}")
        zi[carton['id']] = model.addVar(vtype=GRB.INTEGER, name=f"z_{carton['id']}")
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
        }

    # Relative positioning variables: aik, bik, cik, dik, eik, fik
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

    # Constraints
    # 1. Assign each carton to exactly one container
    for carton in cartons:
        model.addConstr(sum(sij[(carton['id'], container['id'])] for container in containers) <= 1,
                        name=f"assign_{carton['id']}")
    # redundant constraints
    # for container in containers:
    #     model.addConstr(sum(sij[(carton['id'], container['id'])] for carton in cartons) <= M*nj[container['id']],
    #  name=f"assign_{container['id']}")

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

    # 4. Prevent overlapping of cartons with aik, bik, cik, dik, eik, fik
    for container in containers:
        # weight constraints
        model.addConstr(
            sum((sij[(carton['id'], container['id'])] * carton['weight']) for carton in cartons) <= container['weight'],
            name=f"weight_limit_constr{container['id']}")
        for i in range(len(cartons)):
            for k in range(i + 1, len(cartons)):
                carton_i = cartons[i]
                carton_k = cartons[k]
                rel = relative_position[(carton_i['id'], carton_k['id'])]
                model.addConstr((rel["aik"] + rel["bik"] + rel["cik"] + rel["dik"] + rel["eik"] + rel["fik"] >=
                                 sij[(carton_i['id'], container['id'])] + sij[(carton_k['id'], container['id'])] - x),
                                name=f"relative_sum_{carton_i['id']}_{carton_k['id']}_{container['id']}")
    for i in range(len(cartons)):
        for k in range(i + 1, len(cartons)):
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
    # print(cartons)
    # Objective: Minimize unused space
    model.setObjective(gp.quicksum(
        (gp.quicksum(sij[(carton['id'], container['id'])] for carton in cartons) for container in containers)),
        GRB.MAXIMIZE)
    # Objective: Minimize unused space
    #  priority_penalty = 0
    #  for container in containers:
    #     prod = 0
    #     for carton in cartons:
    #         prod = prod or ((sij[(carton['id'], container['id'])] * carton['priority']))
    #     priority_penalty += prod
    #  priority_penalty *= 5000
    #  penalty = sum(1-(sum(sij[(carton['id'], container['id'])] for container in containers)) * carton['cost'] for carton in cartons)
    # for carton in cartons:
    #     s = 1
    #     for container in containers:
    #         s -= sij[(carton['id'], container['id'])]
    #     economy_penalty += s * carton['cost']
    # penalty =  economy_penalty
    # model.setObjective(penalty, GRB.MINIMIZE)
    model.optimize()
    # Extract the solution
    if model.status == GRB.OPTIMAL:
        print("Optimal solution found. Checking constraints:")
        # for c in model.getConstrs():
        #     lhs = model.getRow(c).getValue()
        #     rhs = c.RHS
        # print(f"{c.ConstrName}: LHS = {lhs}, RHS = {rhs}, Sense = {c.Sense}")
        # print(sij["P-365", "U6"].X)
        # print(sij["P-165", "U6"].X)
        model.printQuality()
        solution = []
        # for container in containers:
        # for i in range(len(cartons)):
        #     for j in range(i + 1, len(cartons)):
        #         rel = relative_position[(cartons[i]['id'], cartons[j]['id'])]
        #         print(cartons[i]['id'], cartons[j]['id'], container['id'])
        #         print(rel["aik"].X, rel["bik"].X, rel["cik"].X, rel["dik"].X, rel["eik"].X, rel["fik"].X)
        for container in containers:
            for carton in cartons:
                if sij[(carton['id'], container['id'])].X > 0.5:
                    solution.append({
                        "carton_id": carton['id'],
                        "container_id": container['id'],
                        "x": xi[carton['id']].X,
                        "y": yi[carton['id']].X,
                        "z": zi[carton['id']].X,
                        "DimX": carton['length'] * orientation[carton['id']]["lx"].X + carton['width'] *
                                orientation[carton['id']]["wx"].X + carton['height'] * orientation[carton['id']][
                                    "hx"].X,
                        "DimY": carton['length'] * orientation[carton['id']]["ly"].X + carton['width'] *
                                orientation[carton['id']]["wy"].X + carton['height'] * orientation[carton['id']][
                                    "hy"].X,
                        "DimZ": carton['length'] * orientation[carton['id']]["lz"].X + carton['width'] *
                                orientation[carton['id']]["wz"].X + carton['height'] * orientation[carton['id']]["hz"].X
                    })
                    # Print aik and bik variables
        return solution
    else:
        print("No feasible solution found.")
