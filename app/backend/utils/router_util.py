import os
import matplotlib.pyplot as plt
from typing import List, Dict, Any

class RouterUtil: 

    # all constants in mm
    ROUTER_MAX_DIMENSION = 5000 
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

    def __init__(self, router_preview_folder_path: str):
        self.router_preview_folder_path = router_preview_folder_path
        self.plot_bg_color: str='#ffffff' 
        self.plot_text_color: str='#000000'
        self.plot_line_color: str='#000000'

    @property
    @staticmethod
    def editable_keys():
        return [
            "machineable_area_(x-axis)",
            "machineable_area_(y-axis)",
            "machineable_area_(z-axis)",
            "max_plate_size_(x-axis)",
            "max_plate_size_(y-axis)",
            "max_plate_size_(z-axis)",
            "min_safe_distance_from_edge",
            "drill_bit_diameter",
            "mill_bit_diameter"
        ]

    @property
    @staticmethod
    def value_ranges(): 
        return {
            "machineable_area_(x-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION), 
            "machineable_area_(y-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION), 
            "machineable_area_(z-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION), 
            "max_plate_size_(x-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
            "max_plate_size_(y-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
            "max_plate_size_(z-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
            "min_safe_distance_from_edge": (0, RouterUtil.ROUTER_MAX_DIMENSION//2),
            "drill_bit_diameter": (0, RouterUtil.DRILL_BIT_MAX_DIAMETER),
            "mill_bit_diameter": (0, RouterUtil.MILL_BIT_MAX_DIAMETER)
        }
        
    @property    
    @staticmethod
    def get_new_router(router_data: list) -> dict:
        filename =  RouterUtil._get_next_router_filename(router_data)
        preview_path = RouterUtil.get_preview_path(filename)

        return {
            "filename": filename,
            "preview_path": preview_path,
            "name": RouterUtil.ROUTER_DEFAULT_NAME,
            "machineable_area_(x-axis)": RouterUtil.ROUTER_DEFAULT_X, 
            "machineable_area_(y-axis)": RouterUtil.ROUTER_DEFAULT_Y, 
            "machineable_area_(z-axis)": RouterUtil.ROUTER_DEFAULT_Z, 
            "max_plate_size_(x-axis)": RouterUtil.PLATE_DEFAULT_X,
            "max_plate_size_(y-axis)": RouterUtil.PLATE_DEFAULT_Y,
            "max_plate_size_(z-axis)": RouterUtil.PLATE_DEFAULT_Z,
            "min_safe_distance_from_edge": RouterUtil.DEFAULT_SAFE_DISTANCE,
            "drill_bit_diameter": RouterUtil.DEFAULT_DRILL_BIT_DIAMETER,
            "mill_bit_diameter": RouterUtil.DEFAULT_MILL_BIT_DIAMETER
        }

    @staticmethod
    def _get_next_router_filename(router_data: list) -> str: 
        router_filenames = [router['filename'] for router in router_data]
        if len(router_filenames) == 0:
            return "ROUTER-0.json"  
        
        router_name_values = [int(router_filename.split('-')[1].split('.')[0]) for router_filename in router_filenames]
        sorted_values = sorted(router_name_values)

        for i, value in enumerate(sorted_values[:-1]):
            next_value = sorted_values[i+1]
            if next_value != value+1:
                return "ROUTER-"+str(value+1)+'.json'

        return "ROUTER-"+str(sorted_values[-1]+1)+".json"
    
    @staticmethod
    def get_preview_path(self, router_filename: str) -> str:

        filename_no_extension = os.path.splitext(router_filename)[0]
        preview_path = os.path.join(self.router_preview_folder_path, filename_no_extension+'.png')
        return preview_path
    
    def save_router_preview(self, router_data: dict, figsize: tuple = (8, 8), dpi: int = 80):

        try: 
            image_path = router_data['preview_path']
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

        plt.plot(plate_rect_x, plate_rect_y, color=self.plot_line_color, linestyle=':')
        plt.plot(router_rect_x, router_rect_y, color=self.plot_line_color)
        plt.plot(safe_rect_x, safe_rect_y, color=self.plot_line_color, linestyle='--')

        plt.grid(True)
        plt.gca().set_facecolor(self.plot_bg_color) # bg color
        plt.gca().set_aspect('equal') 
        plt.grid(False)
        plt.tick_params(axis='x', colors=self.plot_text_color)  # tick color
        plt.tick_params(axis='y', colors=self.plot_text_color) 

        plt.gca().spines['top'].set_color(self.plot_text_color) # graph borders
        plt.gca().spines['bottom'].set_color(self.plot_text_color)
        plt.gca().spines['left'].set_color(self.plot_text_color)
        plt.gca().spines['right'].set_color(self.plot_text_color)

        plt.savefig(image_path, bbox_inches='tight', facecolor='#FFFFFF', dpi=dpi)
    
    def _generate_rectangle_coordinates(self, width, height, offset_x=0, offset_y=0):
        x_coordinates = [offset_x, offset_x + width, offset_x + width, offset_x, offset_x]
        y_coordinates = [offset_y, offset_y, offset_y + height, offset_y + height, offset_y]
        return x_coordinates, y_coordinates
            
