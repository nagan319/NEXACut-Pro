import os
import shutil
import json
from typing import Tuple

from common.constants import *
from stock.stock import Stock

# not all os use '/' divider, therefore path cannot be directly defined in constants
USER_PREFERENCE_PATH = os.path.join(PREFERENCE_DIRECTORY, USER_PREFERENCE_FILE)
DEFAULT_PREFERENCE_PATH = os.path.join(PREFERENCE_DIRECTORY, DEFAULT_PREFERENCE_FILE)

# all units to be stored in mm, input in inches converted automatically
class Controller:

    def __init__(self): # copies user properties to file
        
        self.initialize_preferences()

        self.new_parts = []
        self.new_plates = []

    # preferences

    def initialize_preferences(self): # loads preferences from file

        with open(USER_PREFERENCE_PATH, 'r') as f:
            preference_data = json.load(f)
        
        self.units = preference_data["units"]
        self.image_resolution = preference_data["image_resolution"]
        self.stock = preference_data["stock"]
        self.router = preference_data["router"]

    def revert_preferences(self): # copies default preferences to user preferences

        if os.path.exists(USER_PREFERENCE_PATH):
            os.remove(USER_PREFERENCE_PATH)

        shutil.copyfile(DEFAULT_PREFERENCE_PATH, USER_PREFERENCE_PATH)

        self.initialize_preferences() # re-initializes self

    def configure_user_preferences(self, key: str, new_value): # modifies user preferences

        allowed_keys = ["units", "image_resolution", "stock", "router"]
        allowed_units = ["metric", "imperial"]

        with open(USER_PREFERENCE_PATH, 'r') as f:
            preference_data = json.load(f)

        try:
            if key not in allowed_keys:
                raise ValueError(f"Invalid argument: {key}.")

            if key == "image_resolution":
                if not isinstance(new_value, int):
                    raise TypeError(f"Invalid type for preference parameter: {type(new_value)}. Integer expected.")
                if new_value <= 0 or new_value > MAX_PPMM:
                    raise ValueError(f"Invalid value for image resolution: {new_value}")
                
            elif key == "units":
                if not isinstance(new_value, str):
                    raise TypeError(f"Invalid type for preference parameter: {type(new_value)}. String expected.")
                if new_value not in allowed_units:
                    raise ValueError(f"Invalid value for units: {new_value}")
                
            elif key == "stock":
                stock_path = os.path.join(STOCK_DIRECTORY, new_value)
                if not os.path.exists(stock_path):
                    raise ValueError(f"The stock {new_value} does not exist")
                
            elif key == "router":
                name_with_extension = new_value + '.json'
                router_path = os.path.join(ROUTERS_DIRECTORY, name_with_extension)
                if not os.path.exists(router_path):
                    raise ValueError(f"The router {new_value} does not exist")

        except (TypeError, ValueError) as e:
            print(f"Error: {e}")
            return
        
        else:
            preference_data[key] = new_value

            with open(USER_PREFERENCE_PATH, 'w') as json_file:
                json.dump(preference_data, json_file, indent=4)

            self.initialize_preferences()

    # adding new parts to machine

    def add_new_part_to_tray(self, path: str): # further checks for file 'flatness' etc will be carried out upon conversion to stl

        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file {path} does not exist")
            
            _, extension = os.path.splitext(path)
            extension = extension.lower()[1:] # stored w/o '.'
            if extension not in SUPPORTED_PART_FORMATS:
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

            if extension not in SUPPORTED_IMAGE_FORMATS: 
                raise TypeError(f"The file {path} must be converted to a supported image format")
            
            self.new_plates.append(path)

        except (FileNotFoundError, TypeError) as e:
            print(e)
            return
