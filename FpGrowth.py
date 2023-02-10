# Node class
class Node:
    def __init__(self, node_name, count, parent_node):
        self.name = node_name
        self.count = count
        self.nodeLink = None            # Linked list used to find the same node
        self.parent = parent_node       # Parent node
        self.children = {}              # Child node {node name: node address}


# FP algorithm class
class FpGrowth:

    # Update linked list
    @staticmethod
    def update_table(node, target_node):
        # Find the last link in the linked list and make it point to the new node
        while node.nodeLink is not None:
            node = node.nodeLink
        node.nodeLink = target_node

    # Update Tree
    def update_fp_tree(self, items, tree_header, table_header):
        # If this node already exists in the tree, the quantity is+1
        # Otherwise, generate a new node and update the linked list
        if items[0] in tree_header.children:
            tree_header.children[items[0]].count += 1
        else:
            # Generate new node
            tree_header.children[items[0]] = Node(items[0], 1, tree_header)
            # If the linked list does not point to a node, make it point to the newly generated node;
            # otherwise, make the old node point to the new node
            if table_header[items[0]][1] is None:
                table_header[items[0]][1] = tree_header.children[items[0]]
            else:
                self.update_table(table_header[items[0]][1], tree_header.children[items[0]])
        # Recursively process each element in a piece of data
        if len(items) > 1:
            # Remove the items added this time and enter the child nodes generated
            self.update_fp_tree(items[1:], tree_header.children[items[0]], table_header)

    # Create fp tree
    def create_fp_tree(self, data_set, min_support):
        # First traversal to find frequent itemsets
        item_count = {}             # Dictionary, key is item, value is occurrence
        for t in data_set:          # Count the occurrence times of each item
            for item in t:
                if item not in item_count:
                    item_count[item] = 1
                else:
                    item_count[item] += 1
        # Stores a linked list of single elements. The structure is {Item: [Quantity, Child Node]}
        table_header = {}
        for k in item_count:        # Eliminate items that do not meet the minimum support
            if item_count[k] >= min_support:
                table_header[k] = item_count[k]
        # Frequent Itemset Collection
        freq_item_set = set(table_header.keys())
        # If frequent itemsets cannot be found at the beginning, an empty fp tree is established
        if len(freq_item_set) == 0:
            return None, None
        # Generate chain header from frequent 1 item set
        for k in table_header:
            table_header[k] = [table_header[k], None]
        # Establish tree root node
        tree_header = Node('head tree_header', 1, None)
        # Traverse each item in the dataset to build a tree
        for t in data_set:
            # Filter infrequent items in a dataset
            filter_item = {}  # Dictionary in the form {Item: Quantity}
            for item in t:
                if item in freq_item_set:
                    filter_item[item] = table_header[item][0]
            # If there is 1 frequent item in this data
            if len(filter_item) > 0:
                # Sort the single items in descending order according to the quantity, and return to the list
                order_item = [v[0] for v in sorted(filter_item.items(), key=lambda x: x[1], reverse=True)]
                # Updating trees and linked lists with filtered and sorted samples
                self.update_fp_tree(order_item, tree_header, table_header)
        # Return fp tree and linked list
        return tree_header, table_header

    # Find the path of the node in the tree
    def find_path(self, node, node_path):
        if node.parent is not None:
            node_path.append(node.parent.name)
            self.find_path(node.parent, node_path)

    # Extract Conditional Mode Base
    def find_cond_pattern_base(self, node_name, header_table):
        # For a specific frequent 1 itemset, find the child node first
        tree_node = header_table[node_name][1]
        cond_pat_base = {}              # Dictionary {path: quantity}
        # If the child node is not empty, find the child nodes in order according to the linked list
        while tree_node is not None:
            node_path = []                          # Predefined path
            self.find_path(tree_node, node_path)    # Find its node path
            if len(node_path) > 1:                  # Add path and quantity to dictionary
                cond_pat_base[frozenset(node_path[:-1])] = tree_node.count
            # Advance according to the linked list
            tree_node = tree_node.nodeLink
        return cond_pat_base

    # Create Conditional FP Tree
    def create_cond_fp_tree(self, header_table, min_support, temp, freq_items, support_data):
        # Get frequent itemsets from headerTable and sort them according to the total frequency
        fre = [v[0] for v in sorted(header_table.items(), key=lambda p: p[1][0])]
        # For each element, create an FP tree
        for f in fre:
            freq_set = temp.copy()                              # Add frequent itemsets previously mined
            freq_set.add(f)                                     # Add this frequent itemset to the frequent itemset
            freq_items.add(frozenset(freq_set))
            # Number of supports for joining this frequent 1 itemset
            support_data[frozenset(freq_set)] = header_table[f][0]
            # Find the conditional pattern base and convert the conditional pattern base dictionary into an array
            cond_pat_base = self.find_cond_pattern_base(f, header_table)
            cond_pat_dataset = []
            for item in cond_pat_base.keys():
                item_list = list(item)                          # Convert the key or path to a list
                item_list.sort()                                # Sort the list
                for i in range(cond_pat_base[item]):            # Add in the number of conditional mode bases
                    cond_pat_dataset.append(item_list)
            # Create Conditional FP Tree
            cond_tree, cur_head_table = self.create_fp_tree(cond_pat_dataset, min_support)
            # Recursive mining conditional FP tree
            if cur_head_table is not None:
                self.create_cond_fp_tree(cur_head_table, min_support, freq_set, freq_items, support_data)

    # Generate frequent itemsets
    def generate_l(self, data_set, min_support):
        # Predefined frequent itemsets and support
        freq_item_set = set()
        support_data = {}
        # Create fp tree based on dataset
        tree_header, header_table = self.create_fp_tree(data_set, min_support)
        # If the fp linked list is not available, return it directly
        if header_table is None:
            return support_data
        # Create frequent fp tree, mine frequent items and save support
        self.create_cond_fp_tree(header_table, min_support, set(), freq_item_set, support_data)
        # Return support dictionary
        return support_data
