from WarehouseLocation import *
import numpy as np


# Warehouse Class
class Warehouse:

    # Enter the warehouse dimension (list-3), length (list-3), speed (list-3), goods (double-layer list -? * 2),
    # and frequent item dictionary to be formed
    def __init__(self, dimension, length, speed, stock, fre_dict):
        # Get dimensions, unit time of each dimension, goods list, frequent item dictionary
        self.dimension = dimension
        self.unit_time = [i / j for i, j in zip(length, speed)]
        self.stock = Stock(stock)
        self.fre_dict = fre_dict
        # Calculate the running time of each warehouse location (numpy dimension)
        self.loc_time = self.cal_loc_time()
        # Initial Layout
        self.initial_layout = self.initial_layout()
        # Generate all inventory locations (set up (dimension))
        self.all_loc = self.gene_all_loc()
        # Store objective function value
        self.target_list = [self.cal_tatget()]
        # Dictionary of initial layout
        self.initial_layout_dict = self.get_dict()
        # Compose frequent items
        self.form_fre()

    # Output as dictionary
    def __repr__(self):
        return str(self.get_dict())

    # Calculate the running time of each storage location
    def cal_loc_time(self):
        loc_time = np.zeros(self.dimension)
        for ii in range(self.dimension[0]):
            for jj in range(self.dimension[1]):
                for kk in range(self.dimension[2]):
                    # Calculation formula for the running time of the warehouse
                    loc_time[ii][jj][kk] = round(
                        ii * self.unit_time[0] + kk * self.unit_time[2] + jj * self.unit_time[1], 1)
        return loc_time

    # Initial layout
    def initial_layout(self):
        layout = np.zeros(self.dimension)
        # Get the warehouse location time dictionary
        loc_time_dict = {}
        for ii in range(self.dimension[0]):
            for jj in range(self.dimension[1]):
                for kk in range(self.dimension[2]):
                    loc_time_dict[(ii, jj, kk)] = self.loc_time[ii, jj, kk]
        # Get the corresponding inventory location list from small to large by time
        loc_time_list = sorted(loc_time_dict.items(), key=lambda item: item[1])
        loc_sorted = [x[0] for x in loc_time_list]
        # Put the goods into the storage location list in turn
        index = 0
        for cargo, num, fre in self.stock.car_locnum_fre_list:
            for ii in range(num):
                layout[loc_sorted[index]] = cargo
                index = index + 1
        return layout

    # Generate all storage locations
    def gene_all_loc(self):
        all_loc = set()
        for ii in range(self.dimension[0]):
            for jj in range(self.dimension[1]):
                for kk in range(self.dimension[2]):
                    all_loc.add(
                        Location((ii + 1, jj + 1, kk + 1), self.loc_time[ii, jj, kk], self.initial_layout[ii, jj, kk],
                                 self))
        return all_loc

    # Get goods storage location group list dictionary
    def get_dict(self):
        # Generate warehouse location group goods dictionary
        loctup_car_dict = {}
        for loc in self.all_loc:
            if loc.loctup not in loctup_car_dict.keys():
                loctup_car_dict[loc.loctup] = loc.loctup.cargo
        # Generate reverse dictionary
        car_loctup_dict = {}
        for (key, value) in loctup_car_dict.items():
            if value not in car_loctup_dict.keys():
                car_loctup_dict[value] = [key]
            else:
                car_loctup_dict[value].append(key)
        return car_loctup_dict

    # Get all storage locations where SKUs are stored
    def get_cargo_loc_dict(self):
        cargo_loc_dict = {}
        cartup_loctup_dict = self.get_dict()
        for (cartup,loctup_list) in cartup_loctup_dict.items():
            for loctup in loctup_list:
                for (cargo,loc) in zip(cartup,loctup.form):
                    if cargo in cargo_loc_dict.keys():
                        cargo_loc_dict[cargo].append(loc)
                    else:
                        cargo_loc_dict[cargo] = [loc]
        return cargo_loc_dict

    # Disassemble the cargo group with the length of k into a list in the form of k-1 and 1
    @staticmethod
    def dis_cartup(cartup):
        cartup_list = []
        for ii in range(len(cartup)):
            ksub1_carlist = list(cartup)
            del ksub1_carlist[ii]
            cartup_list.append([tuple(ksub1_carlist), cartup[ii]])
        return cartup_list

    # Judge whether it is a non empty true subset
    @staticmethod
    def is_true_subset(par_set, sub_set):
        if len(sub_set) == 0:
            return False
        elif par_set & sub_set != sub_set:
            return False
        elif par_set == sub_set:
            return False
        else:
            return True

    # Find True Subsets in the List
    @staticmethod
    def find_true_subset(par, a_list):
        sub_list = []
        for sub in a_list:
            if Warehouse.is_true_subset(set(par), set(sub)):
                sub_list.append(sub)
        return sub_list

    # Find the storage location group list according to the cargo group
    def cargo_find_loc(self, cartup):
        car_loctup_dict = self.get_dict()
        if cartup in car_loctup_dict.keys():
            return car_loctup_dict[cartup]
        else:
            return []

    # Corresponding storage location group of goods group
    def form_loctup(self, cartup):
        # List of goods groups disassembled into k-1 and 1
        cartup_list = Warehouse.dis_cartup(cartup)
        # For each decomposition method
        for ksub1, rem in cartup_list:
            # Find the list of storage location groups corresponding to k-1
            ksub1_loctup_list = self.cargo_find_loc(ksub1)
            # Find a feasible inventory location next to each inventory location group in the inventory location group
            # list: 1 is close to the inventory location group; 2 stores the remaining items; 3 the inventory location
            # group goods belong to are the true subset of cartup
            for ksub1_loctup in ksub1_loctup_list:
                # Find the adjacent storage location
                for ad_loc in ksub1_loctup.find_adjoin_locset():
                    # If this inventory location stores the remaining single items and the goods corresponding to
                    # the inventory location group where this inventory location is located are cartup true subsets
                    if (ad_loc.cargo == rem) & (Warehouse.is_true_subset(set(cartup), set(ad_loc.loctup.cargo))):
                        # Set ad_ Loc is removed from the corresponding location group
                        ad_loc.loctup.dele_loc(ad_loc)
                        # Generate a new location group
                        Location_group(*ksub1_loctup.form, ad_loc)
                        # Return whether to complete the update
                        return True
        # Return whether to complete the update
        return False

    # Exchange a group of goods to form a group of goods
    def ex_cargo(self, cartup):
        # List of goods groups disassembled into k-1 and 1
        cartup_list = Warehouse.dis_cartup(cartup)
        # For each decomposition method
        twoloc_time_dict = {}  # Used to save the optimum of each decomposition method
        for ksub1, rem in cartup_list:
            # Predefine the set of replaced and replaced storage locations
            berep_loc_set = set()
            rep_loc_set = set()
            # Find the list of storage location groups corresponding to k-1
            ksub1_loctup_list = self.cargo_find_loc(ksub1)
            # Look for the replaced inventory location next to each inventory location group in the inventory location
            # group list: close to the inventory location group; Can be replaced
            for ksub1_loctup in ksub1_loctup_list:
                for ad_loc in ksub1_loctup.find_adjoin_locset():
                    if ad_loc.whether_be_replace():
                        berep_loc_set.add((ad_loc, ksub1_loctup))
            # Find the storage location set that can be replaced
            for loc in self.all_loc:
                if loc.whether_replace(rem):
                    rep_loc_set.add(loc)
            # Find a relatively small loss value
            min_loss = np.inf
            berep_loc = None
            rep_loc = None
            ksub1_loctup = None
            for (loc1, loctup) in berep_loc_set:
                for loc2 in rep_loc_set:
                    loss_value = (loc1.time * self.stock.car_fre_dict[loc2.cargo] + loc2.time * self.stock.car_fre_dict[
                        loc1.cargo]) - (loc1.time * self.stock.car_fre_dict[loc1.cargo] + loc2.time *
                                        self.stock.car_fre_dict[loc2.cargo])
                    if loss_value < min_loss:
                        min_loss = loss_value
                        berep_loc = loc1
                        rep_loc = loc2
                        ksub1_loctup = loctup
            if berep_loc is not None:
                twoloc_time_dict[(berep_loc, rep_loc, ksub1_loctup)] = min_loss
        # If there is no feasible transposition, false is returned directly
        if len(twoloc_time_dict) == 0:
            return False
        # Find a relatively small loss value
        min_loss = np.inf
        selected_twoloc = None
        for twoloc, loss in twoloc_time_dict.items():
            if loss < min_loss:
                selected_twoloc = twoloc
        # Exchange goods in two storage locations
        (berep_loc, rep_loc, ksub1_loctup) = selected_twoloc
        temp = berep_loc.cargo
        berep_loc.cargo = rep_loc.cargo
        rep_loc.cargo = temp
        # New Location Group
        Location_group(*ksub1_loctup.form, berep_loc)
        Location_group(rep_loc)
        return True

    # Calculate two objective function values
    def cal_tatget(self):
        target_1 = 0
        for loc in self.all_loc:
            target_1 = target_1 + loc.time * self.stock.car_fre_dict[loc.cargo]
        target_2 = sum([len(value) for (key, value) in self.get_dict().items() if len(key) != 1])
        return target_1, target_2

    # Construct a fixed number of cargo groups
    def reach_quantity(self, cartup):
        # Find the goods storage location group dictionary
        car_loctup_dict = self.get_dict()
        # Quantity needed
        if cartup in car_loctup_dict:
            need_num = self.fre_dict[cartup] - len(car_loctup_dict[cartup])
        else:
            need_num = self.fre_dict[cartup]
        # If the required quantity is 0
        if need_num == 0:
            return
        # If the update is successful and the required quantity exists, the k-1 subset should meet the quantity
        # requirements before the update
        is_update = True
        while is_update & (need_num > 0):
            self.reach_subset_quantity(cartup)
            is_update = self.form_loctup(cartup)
            if is_update:
                self.target_list.append(self.cal_tatget())
            need_num = need_num - is_update
        is_update = True
        while is_update & (need_num > 0):
            self.reach_subset_quantity(cartup)
            is_update = self.ex_cargo(cartup)
            if is_update:
                self.target_list.append(self.cal_tatget())
            need_num = need_num - is_update

    # Make the subset meet the quantity requirement
    def reach_subset_quantity(self, cartup):
        if len(cartup) == 2:
            return
        sub_cartup = [x[0] for x in Warehouse.dis_cartup(cartup)]
        for sub in sub_cartup:
            self.reach_quantity(sub)

    # Construct cargo groups in turn
    def form_fre(self):
        cartup_sequence = [y[0] for y in sorted(self.fre_dict.items(), key=lambda x: len(x[0]), reverse=True)]
        for cartup in cartup_sequence:
            self.reach_quantity(cartup)
            print(f"Finished frequent item {cartup}")
