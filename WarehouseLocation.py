from Warehouse import *
import numpy as np


# Warehouse location class
class Location:

    # Warehouse location has attributes: location, lane, time, goods, warehouse, location group
    def __init__(self, position, time, cargo, warehouse):
        self.position = position
        self.tunnel = int((position[1] + 1) / 2)
        self.time = time
        self.cargo = int(cargo)
        self.warehouse = warehouse
        self.loctup = Location_group(self)

    # Output as inventory location
    def __repr__(self):
        return str(self.position)

    # Judge whether storage locations are adjacent
    def is_adjoin(self, other):
        loc1 = self.position
        loc2 = other.position
        if loc1[1] != loc2[1]:
            return False
        elif (abs(loc1[0] - loc2[0]) == 1) & (loc1[2] == loc2[2]):
            return True
        elif (loc1[0] == loc2[0]) & (abs(loc1[2] - loc2[2]) == 1):
            return True
        elif (abs(loc1[0] - loc2[0]) == 1) & (abs(loc1[2] - loc2[2]) == 1):
            return True
        else:
            return False

    # Find the adjacent storage location set
    def find_adjoin_loc_set(self):
        ad_loc_set = set()
        for temp_loc in self.warehouse.all_loc:
            if self.is_adjoin(temp_loc):
                ad_loc_set.add(temp_loc)
        return ad_loc_set

    # Can it be replaced: only those without inventory or whose inventory location group is a single item
    # can be replaced
    def whether_be_replace(self):
        if self.cargo == 0:
            return True
        if self.loctup.len == 1:
            return True
        else:
            return False

    # Can it be replaced: fixed goods are stored and the length of the location group is 1
    def whether_replace(self, cargo):
        if (self.cargo == cargo) & (self.loctup.len == 1):
            return True
        else:
            return False


# Location group class
class Location_group:

    # Warehouse location group has attributes: composition of warehouse location group, corresponding cargo
    # group and length
    def __init__(self, *loc_tup):
        loc_tup = np.asarray(loc_tup)
        # Find the corresponding goods
        cargo_list = []
        for loc in loc_tup:
            cargo_list.append(loc.cargo)
        cargo_np = np.asarray(cargo_list)
        # Get the goods sorting subscript
        sort_index = np.argsort(cargo_np)
        # Get the sorted position and goods
        self.form = tuple(loc_tup[sort_index])
        cargo_np = cargo_np[sort_index]
        self.cargo = tuple(cargo_np.tolist())
        self.len = len(self.form)
        # Change the location group bound to each location
        for loc in self.form:
            loc.loctup = self

    # Output as Output Location Group
    def __repr__(self):
        return str(self.form)

    # Find the adjacent inventory location set according to the inventory location tuple
    def find_adjoin_locset(self):
        # If there is only a single inventory location in the inventory location group, find its adjacent
        # inventory location
        ad_loc_set = set(self.form[0].find_adjoin_loc_set())
        if len(self.form) == 1:
            return ad_loc_set
        # If there are multiple storage locations in the storage location group, return the union of all
        # adjacent storage locations
        for temp_loc in self.form[1:]:
            ad_loc_set = ad_loc_set | temp_loc.find_adjoin_loc_set()
        return ad_loc_set

    # Delete a storage location from the storage location group
    def dele_loc(self, loc):
        form_list = list(self.form)
        cargo_list = list(self.cargo)
        del_index = form_list.index(loc)
        del form_list[del_index]
        del cargo_list[del_index]
        self.form = tuple(form_list)
        self.cargo = tuple(cargo_list)
        self.len = len(self.form)
        loc.loctup = None


# Inventory class
class Stock:

    # Goods have attributes: corresponding warehouse number, stock in/stock out frequency
    def __init__(self, stock):
        car_locnum_dict = {}
        car_fre_dict = {}
        for every in stock:
            car_locnum_dict[every[0]] = every[1]
            car_fre_dict[every[0]] = every[2]
        stock = sorted(stock, key=lambda item: item[2], reverse=True)
        self.car_locnum_fre_list = stock
        self.car_locnum_dict = car_locnum_dict
        self.car_fre_dict = car_fre_dict

    # Output as two dictionaries of inventory number and frequency
    def __repr__(self):
        return str(self.car_locnum_dict) + str(self.car_fre_dict)
