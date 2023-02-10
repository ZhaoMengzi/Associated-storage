from WarehouseLocation import *
import csv


# Picker
class Picker:

    # Picker has some attributes
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.unit_time = warehouse.unit_time
        self.loc_time = warehouse.loc_time
        self.stock = warehouse.stock
        self.fre_dict = warehouse.fre_dict

    # Randomly select from historical orders to form new orders
    @staticmethod
    def form_new_order(data,need_num,limit_len):
        new_order = []
        while len(new_order)<need_num:
            order_temp = np.random.choice(data,need_num)
            order_temp = [order for order in order_temp if limit_len[0] <= len(order) <= limit_len[1]]
            new_order.extend(order_temp)
        new_order = new_order[0:need_num]
        return new_order

    # 生成一定数量订单集
    @staticmethod
    def form_order_set(num, data, need_num, limit_len):
        for ii in list(range(1, num + 1)):
            # 生成一定数量订单
            order_list = Picker.form_new_order(data, need_num, limit_len)
            import pandas as pd
            order_list = pd.DataFrame(order_list)
            order_list.to_csv('order' + str(ii) + ".csv", index=False, header=0)

    # 读取订单集
    @staticmethod
    def read_order(path):
        # 预定义返回值
        order_set = []
        # 读取csv文件
        with open(path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                row = [float(x) for x in row if x != '']
                row = [int(x) for x in row]
                order_set.append(row)
        # 返回订单集
        return order_set

    # 提取订单的性质
    def extract_character(self, path):
        # 加载订单
        order_list = Picker.read_order(path)
        # 初始化订单最短长度、最长长度、平均长度、SKU频繁程度、所有频繁项、相关度
        max_len = 0
        min_len = 10000
        sum_len = 0
        frequency = 0
        all_fre = set()
        correlation = []
        # 对于每个订单
        for order in order_list:
            # 初始化订单最短长度、最长长度、平均长度
            if len(order) > max_len:
                max_len = len(order)
            if len(order) < min_len:
                min_len = len(order)
            sum_len = sum_len + len(order)
            # 计算SKU总的频繁程度
            for item in order:
                frequency = frequency + self.stock.car_fre_dict[item]
            # 计算SKU之间的相关度
            fre = self.warehouse.fre_dict.keys()  # 找出所有频繁项
            fre = sorted(fre, key=lambda x: len(x), reverse=True)  # 按照长度排序
            # 按照频繁项对订单进行拆解
            for item in fre:
                if set(item) & set(order) == set(item):
                    all_fre.add(item)
                    order = list(set(order) - set(item))
        # 计算平均长度
        mean_len = sum_len / len(order_list)
        # 计算相关度
        for fre in all_fre:
            k = len(fre)
            correlation.append(2 ** k - 1 - k)
        return min_len, max_len, mean_len, frequency, sum(correlation)

    # 读取一批订单集的性质
    def extract_multiple(self, path):
        records = []
        for ii in range(1, 51):
            new_path = path + str(ii) + ".csv"
            a_record = self.extract_character(new_path)
            records.append(a_record)
        import pandas as pd
        records = pd.DataFrame(records)
        records.to_csv("features.csv", index=False)

    # 找到货物组列表中的总时间最小者
    def find_min_locs_time(self, loctup_list):
        time_list = []
        # 对库位组列表中的每个库位组计算总时间
        for loctup in loctup_list:
            time = 0
            for loc in loctup.form:
                time = time + loc.time
            time_list.append(time)
        # 找到总时间最小的下标
        index = np.argmin(time_list)
        # 返回最小时间对应的库位组
        return loctup_list[index]

    # Find the lowest total time in the goods group list
    def find_min_loc_time(self,loc_list):
        time_list = [loc.time for loc in loc_list]
        index = np.argmin(time_list)
        return loc_list[index]

    # Find the picking location according to the order
    def find_loc(self, order):
        # Find the goods group - storage location group list - dictionary
        cartup_loctup_dict = self.warehouse.get_dict()
        # Sort the dictionary according to the length of goods group and then the number of storage locations
        # from high to low to get a feasible goods group
        allowed_cartup = [x[0] for x in sorted(cartup_loctup_dict.items(),key = lambda x : (len(x[0]),len(x[1])),reverse = True)]
        # Disassemble the order according to the goods group
        selected_order = []
        for cartup in allowed_cartup:
            if set(cartup)&set(order) == set(cartup):
                selected_order.append(cartup)
                order = list(set(order)-set(cartup))
        # Select the one with the least total time in each group of storage locations to get the picking
        # storage location
        selected_loc_list = []
        for order_item in selected_order:
            loctup_list = cartup_loctup_dict[order_item]
            selected_locs = self.find_min_locs_time(loctup_list)
            selected_loc_list.extend(selected_locs.form)
        # 找到货物-库位列表字典
        car_loc_dict = self.warehouse.get_cargo_loc_dict()
        for order_item in order:
            if order_item in car_loc_dict.keys():
                loc_list = car_loc_dict[order_item]
                selected_loc = self.find_min_loc_time(loc_list)
                selected_loc_list.append(selected_loc)
                order.remove(order_item)
        return selected_loc_list

    # Calculate the time according to the order picking location
    def cal_time(self, loc_list):
        # Calculate the time on the y-axis, multiply by 2 to calculate the round-trip
        time_y = self.unit_time[1] * max([loc.position[1] for loc in loc_list]) * 2
        # Find the lane of each storage location and return to the dictionary
        tunnel_loc_dict = {}
        for loc in loc_list:
            if loc.tunnel in tunnel_loc_dict.keys():
                tunnel_loc_dict[loc.tunnel].append(loc)
            else:
                tunnel_loc_dict[loc.tunnel] = [loc]
        # Time spent on x-axis for calculation of each roadway
        time_x = 0
        for (tunnel, locs) in tunnel_loc_dict.items():
            time_x = time_x + self.unit_time[0] * max([loc.position[0] for loc in locs]) * 2
        # Calculate the time spent on the z-axis
        time_z = 0
        for loc in loc_list:
            time_z = time_z + loc.position[2] * loc.position[2] * self.unit_time[0]
        # Calculate the total time and return
        time = time_x + time_y + time_z
        return round(time)

    # Take out the goods according to the warehouse location
    def pick_up(self,loc_list):
        for loc in loc_list:
            loc.loctup.dele_loc(loc)
            loc.cargo = 0
            Location_group(loc)

    # Simulation
    def simulation(self,original_order_list):
        import copy
        order_list = copy.deepcopy(original_order_list)
        sum_time = []
        # For each order
        for order in order_list:
            # Determine picking location
            loc_list = self.find_loc(order)
            if len(loc_list) != 0:
                # Calculate picking time
                time = self.cal_time(loc_list)
                sum_time.append(time)
                # Pick up
                self.pick_up(loc_list)
            else:
                sum_time.append(0)
        return sum_time
