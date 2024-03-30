import os
import shutil
import json

# all units in mm
class PreferenceManager:

    def __init__(self, max_img_res: int, router_data_path: str, stock_data_path: str, default_preference_path: str, user_preference_path: str):

        self.max_img_res = max_img_res
        self.router_data_path = router_data_path
        self.stock_data_path = stock_data_path
        self.default_preference_path = default_preference_path
        self.user_preference_path = user_preference_path

        self.preference_data = {}
        self.preference_options = self._load_preference_options() 

        with open(self.user_preference_path, 'r') as f:
            self.preference_data = json.load(f)

    def _load_preference_options(self):
        return {
            "units": ('Metric', 'Imperial'),
            "image_resolution": list(range(1, self.max_img_res + 1)),
            "stock": self._load_folder_contents(self.router_data_path),
            "router": self._load_folder_contents(self.stock_data_path)
        }

    def _load_folder_contents(self, folder_path): # creates list of all files in directory
        if not os.path.exists(folder_path):
            return []
        return os.listdir(folder_path) # only returns names, not full path

    def revert_preferences(self): # copies contents of default_preferences file into user_preferences
        os.remove(self.user_preference_path)
        shutil.copyfile(self.default_preference_path, self.user_preference_path)

    def update_preference(self, key, new_value):
        self.preference_data[key] = new_value
        with open(self.user_preference_path, 'w') as json_file:
            json.dump(self.preference_data, json_file, indent=4)
