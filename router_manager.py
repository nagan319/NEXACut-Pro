from imports import *
from router import Router

class RouterManager:

    def add_router(self, name: str, machineable_area: Tuple[int, int, int], max_plate_size: Tuple[int, int, int], min_safe_distance_from_edge: int, drill_bit_diameter: float, mill_bit_diameter: float): # adds new router, saves as json

        name_with_extension = name+'.json'
        new_router_path = os.path.join(routers_path, name_with_extension)

        # checks for all input data

        if os.path.exists(new_router_path):
            raise FileExistsError(f"A router with the name {name} already exists.")
        
        for value in machineable_area:
            if value <= 0 or value > router_max_dimension:
                raise ValueError(f"Invalid value for machineable area.")
        
        for value in max_plate_size:
            if value <= 0 or value > plate_max_dimension:
                raise ValueError(f"Invalid value for maximum plate size.") 
        
        if min_safe_distance_from_edge > (min(max_plate_size[:2]) / 2) or min_safe_distance_from_edge < 0:
            raise ValueError(f"Invalid value for maximum plate size.") 
        
        if drill_bit_diameter < 0 or drill_bit_diameter > drill_bit_max_size: 
            raise ValueError(f"Invalid value for drill bit diameter.") 
        
        if mill_bit_diameter < 0 or mill_bit_diameter > mill_bit_max_size:
            raise ValueError(f"Invalid value for mill bit diameter.") 
        
        # creates new router, dumps to json

        new_router = Router(new_router_path, machineable_area, max_plate_size, min_safe_distance_from_edge, drill_bit_diameter, mill_bit_diameter)
        new_router.to_json()

        with open(new_router_path, "w") as json_file:
            json.dump(new_router.to_json(), json_file, indent=4)
        
    def delete_router(self, name: str): # deletes router at indicated path

        name_with_extension = name+'.json'
        router_path = os.path.join(routers_path, name_with_extension)

        if os.path.exists(router_path):
            os.remove(router_path)

    def configure_router_properties(self, name: str, property: str, value): # modifies router at indicated path (entirely in json format)

        allowed_properties = ["machineable_area", "max_plate_size", "min_safe_distance_from_edge", "drill_bit_diameter", "mill_bit_diameter"]
        
        if property not in allowed_properties:
            raise ValueError(f"Invalid property: {property}")
        
        name_with_extension = name + '.json'
        router_path = os.path.join(routers_path, name_with_extension)

        if not os.path.exists(router_path):
            raise FileNotFoundError(f"The router {name} does not exist.")

        with open(router_path, 'r') as f:
            router_data = json.load(f)

        if property in ["machineable_area", "max_plate_size"]:
            if not isinstance(value, tuple) or len(value) != 3:
                raise ValueError("Invalid value for property. Expected a tuple of length 3.")
            
            for dimension in value:
                if dimension <= 0:
                    raise ValueError("Invalid value for property. All dimensions must be greater than 0.")
                
                if property == "max_plate_size" and dimension > plate_max_dimension:
                    raise ValueError("Invalid value for property. Dimension exceeds maximum allowed.")
                
                
        elif property == "min_safe_distance_from_edge":

            if not isinstance(value, int) or value < 0:
                raise ValueError("Invalid value for property. Expected a non-negative integer.")
            
        elif property in ["drill_bit_diameter", "mill_bit_diameter"]:

            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError("Invalid value for property. Expected a non-negative number.")
            
            if property == "drill_bit_diameter" and value > drill_bit_max_size:
                raise ValueError("Invalid value for property. Exceeds maximum allowed.")
            
            if property == "mill_bit_diameter" and value > mill_bit_max_size:
                raise ValueError("Invalid value for property. Exceeds maximum allowed.")
            

        router_data[property] = value

        with open(router_path, 'w') as f:
            json.dump(router_data, f, indent=4)