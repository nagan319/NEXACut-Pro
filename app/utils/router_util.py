class RouterUtil: # class containing router-related constants

    ROUTER_MAX_DIMENSION = 5000 # all constants in mm
    PLATE_MAX_DIMENSION = 5000
    DRILL_BIT_MAX_DIAMETER = 100
    MILL_BIT_MAX_DIAMETER = 100

    ROUTER_DEFAULT_NAME = "New CNC Router"

    ROUTER_DEFAULT_X = 750
    ROUTER_DEFAULT_Y = 1500
    ROUTER_DEFAULT_Z = 500

    PLATE_DEFAULT_X = 1000
    PLATE_DEFAULT_Y = 2000
    PLATE_DEFAULT_Z = 500

    DEFAULT_SAFE_DISTANCE = 50
    DEFAULT_DRILL_BIT_DIAMETER = 5
    DEFAULT_MILL_BIT_DIAMETER = 10

    def __init__(self):
        self.value_ranges = self._load_value_ranges()
        self.default_router = self._load_default_router()

    def _load_value_ranges(self): 
        return {
            "name": (None, None),
            "machineable_area_(x-axis)": (0, self.ROUTER_MAX_DIMENSION), 
            "machineable_area_(y-axis)": (0, self.ROUTER_MAX_DIMENSION), 
            "machineable_area_(z-axis)": (0, self.ROUTER_MAX_DIMENSION), 
            "max_plate_size_(x-axis)": (0, self.PLATE_MAX_DIMENSION),
            "max_plate_size_(y-axis)": (0, self.PLATE_MAX_DIMENSION),
            "max_plate_size_(z-axis)": (0, self.PLATE_MAX_DIMENSION),
            "min_safe_distance_from_edge": (0, self.ROUTER_MAX_DIMENSION//2),
            "drill_bit_diameter": (0, self.DRILL_BIT_MAX_DIAMETER),
            "mill_bit_diameter": (0, self.MILL_BIT_MAX_DIAMETER)
        }
    
    def _load_default_router(self):
        return {
            "name": self.ROUTER_DEFAULT_NAME,
            "machineable_area_(x-axis)": self.ROUTER_DEFAULT_X, 
            "machineable_area_(y-axis)": self.ROUTER_DEFAULT_Y, 
            "machineable_area_(z-axis)": self.ROUTER_DEFAULT_Z, 
            "max_plate_size_(x-axis)": self.PLATE_DEFAULT_X,
            "max_plate_size_(y-axis)": self.PLATE_DEFAULT_Y,
            "max_plate_size_(z-axis)": self.PLATE_DEFAULT_Z,
            "min_safe_distance_from_edge": self.DEFAULT_SAFE_DISTANCE,
            "drill_bit_diameter": self.DEFAULT_DRILL_BIT_DIAMETER,
            "mill_bit_diameter": self.DEFAULT_MILL_BIT_DIAMETER
        }
    
    # gets next available router filename
    def get_next_router_filename(self, router_names: list) -> str: 
        return "ROUTER-0.json" if len(router_names) == 0 else "ROUTER-"+str(int(router_names[-1].split('-')[1][:-5])+1)+".json"
