# Import packages
import csv
import math
import numpy as np
from Pretreatment import *
from Warehouse import *
from Simulation import *


# Load dataset according to path
def load_data(path):
    # Predefined return list
    data_list = []
    # Read csv file
    with open(path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            row = list(set(row))    # Duplicate removal
            row.sort()              # Sort
            data_list.append(row)   # Add
    # Return the processed data set
    return data_list


# Principal function
if __name__ == "__main__":
    # Set parameters
    data_path = "groceries.csv"
    min_support = 50
    theta = 5
    warehouse_dimension = [25, 50, 4]
    warehouse_length = [0.5, 1, 0.5]
    warehouse_speed = [0.5, 0.5, 1]
    simulate_path = "order_test\order_set1\order"
    # Load dataset
    data = load_data(data_path)
    # Find frequent items for de duplication
    fp_dict = find_dup_re_fp(data, min_support)
    # Number to get the number dictionary and new fp_ dict
    num_car_dict, fp_dict = number(fp_dict)
    # The dataset is numbered because data is changed in the find_dup_re_fp and needs to be reloaded
    data = load_data(data_path)
    data = data_number(data, num_car_dict)
    # Remove the impact of the cycle. Assume that this batch of orders has 12 cycles
    fp_dict = {key: int(value / 12) for (key, value) in fp_dict.items()}
    # Continuous processing
    is_completed = False
    while not is_completed:
        is_completed, fp_dict = continuous_processing(fp_dict)
    # Get frequent 1 item set (add frequent item 0) and frequent multiple item set
    fre_1 = [[key[0], math.ceil(1.2 * value), value] for (key, value) in fp_dict.items() if len(key) == 1]
    fre_1.append([0, 0, 0])
    fre_k = {key: np.ceil(theta * value) for (key, value) in fp_dict.items() if len(key) != 1}
    # Call the warehouse class to get the warehouse location allocation result
    ware = Warehouse(warehouse_dimension, warehouse_length, warehouse_speed, fre_1, fre_k)
    # Simulate a batch of order groups
    time = []
    for ii in range(1, 51):
        # Read order
        path = simulate_path + str(ii) + ".csv"
        order_set = Picker.read_order(path)
        # Copy location allocation layout
        import copy
        ware_copy = copy.deepcopy(ware)
        # Conduct simulation
        picker = Picker(ware_copy)
        time.extend(picker.simulation(order_set))
    print(f'Total time is {np.sum(time)} s')
    # Record results
    import pandas as pd
    time = pd.DataFrame(time)
    time.to_csv("picking_time.csv", index=False, header=0)
