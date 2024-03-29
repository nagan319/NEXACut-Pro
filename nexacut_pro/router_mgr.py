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

    def select_router(self, idx: int):
        target_router_path = os.path.join(self.router_directory, self.routers[idx])
        self.load_router_properties(target_router_path)

    def load_router_properties(self, router_path: str):
        if os.path.exists(router_path):
            with open(router_path, 'r') as f:
                self.router_data = json.load(f)

    def add_router(self, name: str):
        name_with_extension = name+'.json'
        new_router_path = os.path.join(self.router_directory, name_with_extension)
        try: 
            if os.path.exists(new_router_path):
                raise FileExistsError(f"A router with the name {name} already exists.")

        except FileExistsError as e:
            print(e)

        else:
            new_router = {
                "machineable_area_(x-axis)": ROUTER_DEFAULT_DIMENSION, 
                "machineable_area_(y-axis)": ROUTER_DEFAULT_DIMENSION, 
                "machineable_area_(z-axis)": ROUTER_DEFAULT_DIMENSION, 
                "max_plate_size_(x-axis)": PLATE_DEFAULT_DIMENSION,
                "max_plate_size_(y-axis)": PLATE_DEFAULT_DIMENSION,
                "max_plate_size_(z-axis)": PLATE_DEFAULT_DIMENSION,
                "min_safe_distance_from_edge": DEFAULT_SAFE_DISTANCE,
                "drill_bit_diameter": DRILL_BIT_DEFAULT_DIAMETER,
                "mill_bit_diameter": MILL_BIT_DEFAULT_DIAMETER
            }

            with open(new_router_path, "w") as json_file:
                json.dump(new_router, json_file, indent=4) 
        
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

    def configure_router_properties(self, name: str, property: str, value): # modifies router at indicated path (entirely in json format)

        allowed_properties = ["machineable_area", "max_plate_size", "min_safe_distance_from_edge", "drill_bit_diameter", "mill_bit_diameter"]

        name_with_extension = name + '.json'
        router_path = os.path.join(self.router_directory, name_with_extension)
        
        try:
            if not os.path.exists(router_path):
                raise FileNotFoundError(f"The router {name} does not exist.")

            if property not in allowed_properties:
                raise ValueError(f"Invalid property: {property}")
            
            if property in ["machineable_area", "max_plate_size"]:
                if not isinstance(value, tuple) or len(value) != 3:
                    raise ValueError("Invalid value for property. Expected a tuple of length 3.")
                
                for dimension in value:
                    if dimension <= 0:
                        raise ValueError("Invalid value for property. All dimensions must be greater than 0.")
                    
                    if property == "max_plate_size" and dimension > PLATE_MAX_DIMENSION:
                        raise ValueError("Invalid value for property. Dimension exceeds maximum allowed.")
                    
            elif property == "min_safe_distance_from_edge":

                if not isinstance(value, int) or value < 0:
                    raise ValueError("Invalid value for property. Expected a non-negative integer.")
                
            elif property in ["drill_bit_diameter", "mill_bit_diameter"]:

                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError("Invalid value for property. Expected a non-negative number.")
                
                if property == "drill_bit_diameter" and value > DRILL_BIT_MAX_DIAMETER:
                    raise ValueError("Invalid value for property. Exceeds maximum allowed.")
                
                if property == "mill_bit_diameter" and value > MILL_BIT_MAX_DIAMETER:
                    raise ValueError("Invalid value for property. Exceeds maximum allowed.")

        except(FileNotFoundError, ValueError) as e:
            print(e)
            return

        else: 
            with open(router_path, 'r') as f:
                router_data = json.load(f)

            router_data[property] = value

            with open(router_path, 'w') as f:
                json.dump(router_data, f, indent=4)