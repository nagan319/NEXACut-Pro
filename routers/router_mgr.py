import os
import json
from typing import Tuple

from constants.hardware import *
from constants.file_paths import ROUTERS_DIRECTORY

class RouterManager:

    def new_router(self, name: str, machineable_area: Tuple[int, int, int], max_plate_size: Tuple[int, int, int], min_safe_distance_from_edge: int, drill_bit_diameter: float, mill_bit_diameter: float): # adds new router, saves as json

        name_with_extension = name+'.json'
        new_router_path = os.path.join(ROUTERS_DIRECTORY, name_with_extension)

        # checks for all input data

        try: 
            if os.path.exists(new_router_path):
                raise FileExistsError(f"A router with the name {name} already exists.")
            
            for value in machineable_area:
                if value <= 0 or value > ROUTER_MAX_DIMENSION:
                    raise ValueError(f"Invalid value for machineable area.")
            
            for value in max_plate_size:
                if value <= 0 or value > PLATE_MAX_DIMENSION:
                    raise ValueError(f"Invalid value for maximum plate size.") 
            
            if min_safe_distance_from_edge > (min(max_plate_size[:2]) / 2) or min_safe_distance_from_edge < 0:
                raise ValueError(f"Invalid value for maximum plate size.") 
            
            if drill_bit_diameter < 0 or drill_bit_diameter > DRILL_BIT_MAX_DIAMETER: 
                raise ValueError(f"Invalid value for drill bit diameter.") 
            
            if mill_bit_diameter < 0 or mill_bit_diameter > MILL_BIT_MAX_DIAMETER:
                raise ValueError(f"Invalid value for mill bit diameter.") 
            
        except(FileExistsError, ValueError) as e:
            print(e)
            return
        
        else:

            # creates new router, dumps to json

            new_router = {
                "machineable_area": machineable_area,
                "max_plate_size": max_plate_size,
                "min_safe_distance_from_edge": min_safe_distance_from_edge,
                "drill_bit_diameter": drill_bit_diameter,
                "mill_bit_diameter": mill_bit_diameter
            }

            with open(new_router_path, "w") as json_file:
                json.dump(new_router, json_file, indent=4)
        
    def delete_router(self, name: str): # deletes router at indicated path

        name_with_extension = name+'.json'
        router_path = os.path.join(ROUTERS_DIRECTORY, name_with_extension)

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
        router_path = os.path.join(ROUTERS_DIRECTORY, name_with_extension)
        
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