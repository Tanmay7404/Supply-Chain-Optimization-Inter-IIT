import csv

def containers():
    """
    Reads container data from a CSV file and returns a list of containers.
    The CSV file should have the following columns in order:
    - id (str): The identifier of the container.
    - length (float): The length of the container.
    - width (float): The width of the container.
    - height (float): The height of the container.
    - weight (float): The weight of the container.
    Returns:
        list of dict: A list of dictionaries where each dictionary represents a container with keys:
        'id', 'length', 'width', 'height', and 'weight'. The list is sorted by container 'id'.
    """
    # Open the CSV file and read its contents
    # Create a list of containers with their attributes
    # Sort the list of containers by their 'id' before returning

    file_path = './ULD.csv'
    containers = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            container = {
                "id": row[0],
                "length": float(row[1]),
                "width": float(row[2]),
                "height": float(row[3]),
                "weight": float(row[4])
            }
            containers.append(container)
    containers.sort(key=lambda x: x['id'])
    return containers

def containers_specific(container_id):
    """
    Retrieve specific container details from a CSV file.
    This function reads container data from a CSV file named 'ULD.csv', 
    filters the containers based on the provided container_id, and returns 
    a list of containers that match the given ID. The containers are sorted 
    by their ID.
    Args:
        container_id (str): The ID of the container to be retrieved.
    Returns:
        list: A list of dictionaries, each containing the details of a container 
              with the specified ID. Each dictionary contains the following keys:
              - 'id' (str): The container ID.
              - 'length' (float): The length of the container.
              - 'width' (float): The width of the container.
              - 'height' (float): The height of the container.
              - 'weight' (float): The weight of the container.
    """



    file_path = './ULD.csv'
    containers = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            container = {
                "id": row[0],
                "length": float(row[1]),
                "width": float(row[2]),
                "height": float(row[3]),
                "weight": float(row[4])
            }
            if container['id'] != container_id:
                continue
            containers.append(container)
    containers.sort(key=lambda x: x['id'])
    return containers


def containers_specific_multiple(container_ids):
    """
    Retrieve specific container details from a CSV file based on given container IDs.
    This function reads container data from a CSV file named 'ULD.csv' and filters the containers
    whose IDs are present in the provided list of container IDs. The filtered containers are then
    sorted by their IDs and returned as a list of dictionaries.
    Args:
        container_ids (list): A list of container IDs to filter the containers.
    Returns:
        list: A list of dictionaries, where each dictionary contains the details of a container
              with keys 'id', 'length', 'width', 'height', and 'weight'.
    Example:
        container_ids = ['C1', 'C2']
        containers = containers_specific_multiple(container_ids)
        # containers will be a list of dictionaries with details of containers 'C1' and 'C2'
    """
    
    file_path = './ULD.csv'
    containers = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            container = {
                "id": row[0],
                "length": float(row[1]),
                "width": float(row[2]),
                "height": float(row[3]),
                "weight": float(row[4])
            }
            if container['id'] not in container_ids:
                continue
            containers.append(container)
    containers.sort(key=lambda x: x['id'])
    return containers

