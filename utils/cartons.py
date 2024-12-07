import csv

def cartons():
    """
    Reads carton data from a CSV file and returns a list of carton dictionaries.
    The CSV file should have the following columns:
    - id: Unique identifier for the carton
    - dimension1: First dimension of the carton (float)
    - dimension2: Second dimension of the carton (float)
    - dimension3: Third dimension of the carton (float)
    - weight: Weight of the carton (float)
    - priority: Priority status of the carton ("Priority" or other)
    - cost: Cost associated with the carton (float or '-')
    The function processes each row in the CSV file, sorts the dimensions,
    and creates a dictionary for each carton with the following keys:
    - id: Carton ID (string)
    - length: Smallest dimension (float)
    - width: Middle dimension (float)
    - height: Largest dimension (float)
    - weight: Weight of the carton (float)
    - priority: 1 if the carton is marked as "Priority", otherwise 0
    - cost: Cost of the carton (float, default to 1e6 if not provided)
    The list of carton dictionaries is sorted by the 'id' key before being returned.
    Returns:
        list: A list of dictionaries, each representing a carton.
    """
    
    file_path = './package.csv'
    cartons = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            v = [float(row[1]), float(row[2]), float(row[3])]
            v.sort()
            carton = {
                "id": row[0],
                "length": float(v[0]),
                "width": float(v[1]),
                "height": float(v[2]),
                "weight": float(row[4]),
                "priority": 1 if row[5] == "Priority" else 0,
                "cost": float(row[6]) if row[6] != '-' else 1e6
            }
            cartons.append(carton)
    cartons.sort(key=lambda x: x['id'])

    return cartons