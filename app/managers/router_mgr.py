import os
import json
from typing import Tuple

ROUTER_MAX_DIMENSION = 5000 # all constants in mm
PLATE_MAX_DIMENSION = 5000
DRILL_BIT_MAX_DIAMETER = 100
MILL_BIT_MAX_DIAMETER = 100

ROUTER_DEFAULT_DIMENSION = 1000
PLATE_DEFAULT_DIMENSION = 1000
DEFAULT_SAFE_DISTANCE = 50
DRILL_BIT_DEFAULT_DIAMETER = 5
MILL_BIT_DEFAULT_DIAMETER = 10

class RouterManager:

    def __init__(self, router_data_folder: str):
        self.router_directory = router_data_folder
        self.value_ranges = self._load_value_ranges()
        self.update_properties()

    def update_properties(self):
        self.routers = os.listdir(self.router_directory)
        self.selected_router_idx = None

    def _load_value_ranges(self): # does not include name (not stored inside json)
        return {
            "machineable_area_(x-axis)": (0, ROUTER_MAX_DIMENSION), 
            "machineable_area_(y-axis)": (0, ROUTER_MAX_DIMENSION), 
            "machineable_area_(z-axis)": (0, ROUTER_MAX_DIMENSION), 
            "max_plate_size_(x-axis)": (0, PLATE_MAX_DIMENSION),
            "max_plate_size_(y-axis)": (0, PLATE_MAX_DIMENSION),
            "max_plate_size_(z-axis)": (0, PLATE_MAX_DIMENSION),
            "min_safe_distance_from_edge": (0, ROUTER_MAX_DIMENSION//2),
            "drill_bit_diameter": (0, DRILL_BIT_MAX_DIAMETER),
            "mill_bit_diameter": (0, MILL_BIT_MAX_DIAMETER)
        }

    def select_router(self, name: str):
        filename = name + '.json'
        if filename in self.routers:
            target_router_path = os.path.join(self.router_directory, filename)
            self.load_router_properties(target_router_path)

    def load_router_properties(self, router_path: str):
        if os.path.exists(router_path):
            with open(router_path, 'r') as f:
                self.router_data = json.load(f)

    def add_router(self, name: str, val_list: list[int]):
        name_with_extension = name+'.json'
        new_router_path = os.path.join(self.router_directory, name_with_extension)
        try: 
            if os.path.exists(new_router_path):
                raise FileExistsError(f"A router with the name {name} already exists.")
            
            new_router = {}
            for i, key in enumerate(self.value_ranges.keys()):
                new_router[key] = val_list[i]

            with open(new_router_path, "w") as json_file:
                json.dump(new_router, json_file, indent=4) 

        except FileExistsError as e:
            print(e)
            
        
    def delete_router(self, name: str): # deletes router at indicated path

        name_with_extension = name+'.json'
        router_path = os.path.join(self.router_directory, name_with_extension)

        try:
            if os.path.exists(router_path):
                os.remove(router_path)
            else:
                raise FileNotFoundError(f"The router {name} does not exist")
            
        except(FileNotFoundError) as e:
            print(e)
            return
    