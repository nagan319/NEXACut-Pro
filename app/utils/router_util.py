import os
import matplotlib.pyplot as plt

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
    
    def get_router_preview(self, router_preview_dst: str, router_data: dict, router_idx: int, bg_color: str='#ffffff', text_color: str='#000000', plot_color: str='#000000', figsize: tuple = (8, 8), dpi: int = 80) -> str:

        if not os.path.exists(router_preview_dst):
            raise FileNotFoundError("Router preview data path is invalid")
        
        image_path = os.path.join(router_preview_dst, "ROUTER-"+str(router_idx)+".png")

        try: 
            router_xy = router_data["machineable_area_(x-axis)"], router_data["machineable_area_(y-axis)"]
            plate_xy = router_data["max_plate_size_(x-axis)"], router_data["max_plate_size_(y-axis)"]
            safe_distance = router_data["min_safe_distance_from_edge"]
        except KeyError:
            return
        
        router_x_offset, router_y_offset = (plate_xy[0] - router_xy[0])/2, plate_xy[1]-router_xy[1]

        plate_rect_x, plate_rect_y = self._generate_rectangle_coordinates(*plate_xy)
        router_rect_x, router_rect_y = self._generate_rectangle_coordinates(*router_xy, router_x_offset, router_y_offset)
        safe_rect_x, safe_rect_y = self._generate_rectangle_coordinates(*tuple(dim - 2 * safe_distance for dim in plate_xy), safe_distance, safe_distance)

        plt.figure(figsize=figsize)

        plt.plot(plate_rect_x, plate_rect_y, color=plot_color, linestyle=':')
        plt.plot(router_rect_x, router_rect_y, color=plot_color)
        plt.plot(safe_rect_x, safe_rect_y, color=plot_color, linestyle='--')

        plt.grid(True)
        plt.gca().set_facecolor(bg_color) # bg color
        plt.gca().set_aspect('equal') 
        plt.grid(False)
        plt.tick_params(axis='x', colors=text_color)  # tick color
        plt.tick_params(axis='y', colors=text_color) 

        plt.gca().spines['top'].set_color(text_color) # graph borders
        plt.gca().spines['bottom'].set_color(text_color)
        plt.gca().spines['left'].set_color(text_color)
        plt.gca().spines['right'].set_color(text_color)

        plt.savefig(image_path, bbox_inches='tight', facecolor='#FFFFFF', dpi=dpi)

        return image_path
    
    def _generate_rectangle_coordinates(self, width, height, offset_x=0, offset_y=0):
        return [offset_x, offset_x + width, offset_x + width, offset_x, offset_x], \
            [offset_y, offset_y, offset_y + height, offset_y + height, offset_y]
