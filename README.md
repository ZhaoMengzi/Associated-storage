# Associated storage

## Introduction
This program is a heuristic algorithm proposed for the inventory location allocation problem. First, the non repeated frequent items and their degree of supportare extracted according to the historical orders, and based on this, the inventory location initialization only for frequent single items is carried out. Then, a recursive strategy is used to improve the aggregation degree of frequent items in the warehouse and realize the final allocation of warehouseby using location group query and location exchange for frequent multiple items. Finally, the effectiveness of this method is demonstrated by simulation of the picker.

## Required Packages
* math
* csv
* numpy

## Running
Please run in the file "Case"
Change "data_path" to change the original order data set, change "min_support" to change the minimum support number, and change "theta" to change θ Value, change "warehouse_dimension", "warehouse_length", "warehouse_speed" to change the parameters of the storage location, change "simulate_path" to change the simulation order path, and try to convert "1" in "order_test order_set1 order" to "2" - "8"
The results are placed in "picking_time. csv", where each value represents the picking time of each order

## Dataset
Dataset is from Kaggle，For more information, 
see [https://www.kaggle.com/datasets/heeraldedhia/groceries-dataset](https://www.kaggle.com/datasets/heeraldedhia/groceries-dataset). 

## Contributing
Improvements are always welcome, feel free to log a bug, write a suggestion. 