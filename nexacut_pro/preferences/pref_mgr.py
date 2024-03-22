import os
import shutil
import json
from typing import Tuple

from .constants import INVENTORY_FOLDER, ROUTER_FOLDER, ROUTER_DATA_FOLDER, STOCK_FOLDER, STOCK_DATA_FOLDER, USER_PREFERENCE_FILE, DEFAULT_PREFERENCE_FILE, ALLOWED_UNITS, MAX_PPMM

current_dir = os.getcwd()
main_dir = os.path.dirname(current_dir)

ROUTER_DATA_PATH = os.path.join(main_dir, INVENTORY_FOLDER, ROUTER_FOLDER, ROUTER_DATA_FOLDER)
STOCK_DATA_PATH = os.path.join(main_dir, INVENTORY_FOLDER, STOCK_FOLDER, STOCK_DATA_FOLDER)
# figure out how to deal with other constants - have to duplicate MAX_PPMM, ROUTERS_DIRECTORY, STOCK_DIRECTORY, not ideal

# all units to be stored in mm, input in inches converted automatically
class PreferenceManager:

    def __init__(self): # copies user properties to file
        
        self.initialize_preferences()

        self.new_parts = []
        self.new_plates = []

    # preferences

    def initialize_preferences(self): # loads preferences from file

        with open(USER_PREFERENCE_FILE, 'r') as f:
            preference_data = json.load(f)
        
        self.units = preference_data["units"]
        self.image_resolution = preference_data["image_resolution"]
        self.stock = preference_data["stock"]
        self.router = preference_data["router"]

    def revert_preferences(self): # copies default preferences to user preferences

        if os.path.exists(USER_PREFERENCE_FILE):
            os.remove(USER_PREFERENCE_FILE)

        shutil.copyfile(DEFAULT_PREFERENCE_FILE, USER_PREFERENCE_FILE)

        self.initialize_preferences() # re-initializes self

    def configure_units_preference(self, new_value):
        if new_value not in ALLOWED_UNITS:
            raise ValueError(f"Invalid value for units: {new_value}")
        self._update_preference("units", new_value)

    def configure_image_resolution_preference(self, new_value):
        if not isinstance(new_value, int):
            raise TypeError(f"Invalid type for image resolution: {type(new_value)}. Integer expected.")
        if new_value <= 0 or new_value > MAX_PPMM:
            raise ValueError(f"Invalid value for image resolution: {new_value}")
        self._update_preference("image_resolution", new_value)

    def configure_stock_preference(self, new_value):
        stock_path = os.path.join(STOCK_DATA_PATH, new_value)
        if not os.path.exists(stock_path):
            raise ValueError(f"The stock {new_value} does not exist")
        self._update_preference("stock", new_value)

    def configure_router_preference(self, new_value):
        router_path = os.path.join(ROUTER_DATA_PATH, new_value + '.json')
        if not os.path.exists(router_path):
            raise ValueError(f"The router {new_value} does not exist")
        self._update_preference("router", new_value)

    def _update_preference(self, key, new_value):
        with open(USER_PREFERENCE_FILE, 'r') as f:
            preference_data = json.load(f)

        preference_data[key] = new_value

        with open(USER_PREFERENCE_FILE, 'w') as json_file:
            json.dump(preference_data, json_file, indent=4)

        self.initialize_preferences()