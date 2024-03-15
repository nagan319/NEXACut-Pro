import os
import shutil
import json
from typing import Tuple

from constants import *
from stock import Stock

# all units to be stored in mm, input in inches converted automatically
class Controller:

    def __init__(self): # copies user properties to file
        
        self.initialize_preferences()

        self.router_manager = RouterManager()
        self.stock_manager = StockManager()
        
        self.new_parts = []
        self.new_plates = []

    # preferences

    def initialize_preferences(self): # loads preferences from file

        with open(user_preferences_path, 'r') as f:
            preference_data = json.load(f)
        
        self.units = preference_data["units"]
        self.image_resolution = preference_data["image_resolution"]
        self.stock = preference_data["stock"]
        self.router = preference_data["router"]

    def revert_preferences(self): # copies default preferences to user preferences

        if os.path.exists(user_preferences_path):
            os.remove(user_preferences_path)

        shutil.copyfile(default_preferences_path, user_preferences_path)

        self.initialize_preferences() # re-initializes self

    def configure_user_preferences(self, key: str, new_value): # modifies user preferences

        allowed_keys = ["units", "image_resolution", "stock", "router"]
        allowed_units = ["metric", "imperial"]

        with open(user_preferences_path, 'r') as f:
            preference_data = json.load(f)

        try:
            if key not in allowed_keys:
                raise ValueError(f"Invalid argument: {key}.")

            if key == "image_resolution":
                if not isinstance(new_value, int):
                    raise TypeError(f"Invalid type for preference parameter: {type(new_value)}. Integer expected.")
                if new_value <= 0 or new_value > max_resolution:
                    raise ValueError(f"Invalid value for image resolution: {new_value}")
                
            elif key == "units":
                if not isinstance(new_value, str):
                    raise TypeError(f"Invalid type for preference parameter: {type(new_value)}. String expected.")
                if new_value not in allowed_units:
                    raise ValueError(f"Invalid value for units: {new_value}")
                
            elif key == "stock":
                stock_path = os.path.join(stock_path, new_value)
                if not os.path.exists(new_value):
                    raise ValueError(f"The stock {new_value} does not exist")
                
            elif key == "router":
                name_with_extension = new_value + '.json'
                router_path = os.path.join(routers_path, name_with_extension)
                if not os.path.exists(router_path):
                    raise ValueError(f"The router {new_value} does not exist")

        except (TypeError, ValueError) as e:
            print(f"Error: {e}")
            return
        
        else:
            preference_data[key] = new_value

            with open(user_preferences_path, 'w') as json_file:
                json.dump(preference_data, json_file, indent=4)

            self.initialize_preferences()

    # adding new parts to machine

    def add_new_part_to_tray(self, path: str): # further checks for file 'flatness' etc will be carried out upon conversion to stl

        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file {path} does not exist")
            
            _, extension = os.path.splitext(path)
            extension = extension.lower()[1:]  
            if extension not in supported_part_formats: 
                raise TypeError(f"The file {path} must be converted to a supported part format")

        except (FileNotFoundError, TypeError) as e:
            print(e)
            return
        
        else:
            self.new_parts.append(path)

    def add_new_plate_to_tray(self, path: str):

        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file {path} does not exist")
            
            _, extension = os.path.splitext(path)
            extension = extension.lower()[1:]  

            if extension not in supported_image_formats: 
                raise TypeError(f"The file {path} must be converted to a supported image format")
            
            self.new_plates.append(path)

        except (FileNotFoundError, TypeError) as e:
            print(e)
            return

class RouterManager:

    def new_router(self, name: str, machineable_area: Tuple[int, int, int], max_plate_size: Tuple[int, int, int], min_safe_distance_from_edge: int, drill_bit_diameter: float, mill_bit_diameter: float): # adds new router, saves as json

        name_with_extension = name+'.json'
        new_router_path = os.path.join(routers_path, name_with_extension)

        # checks for all input data

        try: 
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
        router_path = os.path.join(routers_path, name_with_extension)

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
        router_path = os.path.join(routers_path, name_with_extension)
        
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

        except(FileNotFoundError, ValueError) as e:
            print(e)
            return

        else: 
            with open(router_path, 'r') as f:
                router_data = json.load(f)

            router_data[property] = value

            with open(router_path, 'w') as f:
                json.dump(router_data, f, indent=4)

class StockManager:

    def new_stock(self, name: str): # adds new blank stock, saves as json

        new_stock_file_path = os.path.join(stock_path, name)
        
        try:
            if os.path.exists(new_stock_file_path):
                raise FileExistsError(f"A stock folder with the name {name} already exists.")
            
        except(FileExistsError) as e:
            print(e)
            return
        
        else: 
            os.makedirs(new_stock_file_path)
            
            new_stock_json_path = new_stock_file_path+'/data.json'

            new_stock = Stock(new_stock_json_path, new_stock_file_path)

            with open(new_stock_json_path, "w") as json_file:
                json.dump(new_stock.to_json(), json_file, indent=4)

    def delete_stock(self, name: str):
        stock_folder_path = os.path.join(stock_path, name)
        
        try:
            if os.path.exists(stock_folder_path):
                shutil.rmtree(stock_folder_path) # removes entire folder as opposed to single file
            else:
                raise FileNotFoundError(f"The stock {name} does not exist")
            
        except(FileNotFoundError) as e:
            print(e)
            return
