from FpGrowth import *
from Warehouse import *


# Eliminate frequent items in data
def reject(data, fre):
    # Predefine new datasets
    new_data = []
    # For frequent item traversal data set, if this frequent item is included, the difference set
    for item in data:
        item_set = set(item)
        if item_set.issuperset(fre):
            if (len(item_set - fre) != 0) & (len(item_set - fre) != 1):
                new_data.append(list(item_set - fre))
        else:
            new_data.append(item)
    return new_data


# Find an fp dictionary without repeated frequent items
def find_dup_re_fp(data, min_sup):
    # Extract frequent items separately and create de duplication frequent items_support dictionary
    fp = FpGrowth()
    fp_dict = fp.generate_l(data, min_sup)
    dup_re_fp = {key: value for (key, value) in fp_dict.items() if len(key) == 1}
    # Circular traversal
    while True:
        # Create FP object and call method
        fp = FpGrowth()
        fp_dict = fp.generate_l(data, min_sup)
        # Return the final value if no frequent item is found
        if len(fp_dict) == 0:
            return dup_re_fp
        # Get the maximum length frequent item dictionary
        max_len = max([len(key) for key in fp_dict])  # Find the maximum length of frequent items
        max_len_fp_dict = {key: value for (key, value) in fp_dict.items() if len(key) == max_len}
        # If the maximum length is 1, return directly
        if max_len == 1:
            return dup_re_fp
        # Convert the dictionary to a double-layer list and sort it from high to low support
        max_len_fp_list = [[key, value] for (key, value) in max_len_fp_dict.items()]
        max_len_fp_list = sorted(max_len_fp_list, key=lambda x: x[1], reverse=True)
        # Filter the first column (cargo group) in the list, and add it to the final dictionary
        # with the cargo group with no previous duplicate value
        car_set = set()         # Store the existing goods in the goods group
        fre_set = set()         # Frequent items added by storage
        for [fre, _] in max_len_fp_list:
            # Only when the duplicate item is empty can the operation be performed
            if len(fre & car_set) == 0:
                # Add non repeated frequent items to the dictionary, and add the goods in the goods group to the set
                dup_re_fp[fre] = max_len_fp_dict[fre]
                fre_set.add(fre)
                car_set = car_set | fre
        # Eliminate the newly added frequent items in the data
        for fre in fre_set:
            data = reject(data, fre)


# Numbering frequent items
def number(fp_dict):
    # Predefined goods and goods number dictionary
    car_num_dict = {}
    # Predefined initial goods number is 1
    ii = 1
    # For dictionary key, namely goods number tuple
    for cargo in fp_dict.keys():
        if len(cargo) == 1:
            car_num_dict[list(cargo)[0]] = ii
            # Continue to increase the goods number
            ii = ii + 1
    # Get the goods number - cargos dictionary
    num_car_dict = {value: key for (key, value) in car_num_dict.items()}
    # Predefine new fp dictionary
    new_fp_dict = {}
    for (key, value) in fp_dict.items():
        new_key = list([car_num_dict[ii] for ii in list(key)])
        # The goods number should be in order
        new_key.sort()
        new_fp_dict[tuple(new_key)] = value
    # Return Number Dictionary
    return num_car_dict, new_fp_dict


# Continuous processing of frequent items
def continuous_processing(fp_dict):
    # It is used to judge whether it is completed. If there is a subset not in the dictionary, it is false
    is_completed = True
    # Find all frequent 3 and above
    fp_s3_dict = {key for key in fp_dict.keys() if len(key) >= 3}
    for fre_item in fp_s3_dict:
        fre_sub_list = [x[0] for x in Warehouse.dis_cartup(fre_item)]
        for fre_sub in fre_sub_list:
            if fre_sub in fp_dict.keys():
                continue
            else:
                is_completed = False
                fp_dict[fre_sub] = 1
    return is_completed, fp_dict


# Numbering datasets
def data_number(data, num_car_dict):
    # Get the goods name number dictionary
    car_num_dict = {value: key for (key, value) in num_car_dict.items()}
    # Predefine New Datasets
    new_data = []
    for order in data:
        new_data_order = []
        for item in order:
            if item in car_num_dict.keys():
                new_data_order.append(car_num_dict[item])
        new_data.append(new_data_order)
    return new_data
