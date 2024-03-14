from imports import *

# all units to be stored in mm, input in inches converted automatically
class Controller:
    def __init__(self): # copies user properties to file
        
        self.initialize_preferences()
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

        if key not in allowed_keys:
            raise ValueError(f"Invalid argument: {key}.")
        
        if key == "image_resolution":
            if not isinstance(new_value, int):
                raise TypeError(f"Invalid type for preference parameter: {type(new_value)}. Integer expected.")
        else:
            if not isinstance(new_value, str):
                raise TypeError(f"Invalid type for preference parameter: {type(new_value)}. String expected.")
        
        if key == "units" and new_value not in allowed_units:
            raise ValueError(f"Invalid value for units: {new_value}")
        
        if key == "image_resolution" and (new_value <= 0 or new_value > max_resolution):  # pixels per mm
            raise ValueError(f"Invalid value for image resolution: {new_value}")
        
        if key == "stock": 
            stock_path = os.path.join(stock_path, new_value)
            if not os.path.exists(new_value):
                raise ValueError(f"The stock {new_value} does not exist")
            
        if key == "router": 
            name_with_extension = new_value+'.json'
            router_path = os.path.join(routers_path, name_with_extension)
            if not os.path.exists(router_path):
                raise ValueError(f"The router {new_value} does not exist")
        
        preference_data[key] = new_value

        with open(user_preferences_path, 'w') as json_file:
            json.dump(preference_data, json_file, indent=4)

        self.initialize_preferences()

    # adding new parts to machine

    def add_new_part_to_tray(self, path: str): # further checks for file "flatness" etc will be carried out in separate module

        if not os.path.exists(path):
            raise FileNotFoundError(f"The file {path} does not exist")
        
        _, extension = os.path.splitext(path)
        extension = extension.lower()[1:]  
        if extension not in supported_part_formats: 
            raise TypeError(f"The file {path} must be converted to a supported part format")
        
        self.new_parts.append(path)

    def add_new_plate_to_tray(self, path: str):

        if not os.path.exists(path):
            raise FileNotFoundError(f"The file {path} does not exist")
        
        _, extension = os.path.splitext(path)
        extension = extension.lower()[1:]  

        if extension not in supported_image_formats: # 
            raise TypeError(f"The file {path} must be converted to a supported image format")
        
        self.new_plates.append(path)

