import os
import matplotlib.pyplot as plt
from typing import List, Dict, Any

from ...config import ROUTER_PREVIEW_DATA_PATH

class RouterUtil: 

    """
    Functional class for creating and modifying router data. All constants are stored in millimeters.
    """

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

    PLOT_BG_COLOR = '#ffffff' 
    PLOT_TEXT_COLOR = '#000000'
    PLOT_LINE_COLOR = '#000000'

    @staticmethod
    def editable_keys() -> List[str]:
        """
        Returns a list of editable keys for routers. 
        """
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

    @staticmethod
    def value_ranges() -> Dict[str, Any]: 
        """
        Returns a list of value ranges for relevant router parameters.
        """
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
           
    @staticmethod
    def get_new_router(router_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Returns a new router based on existing routers.

        Arguments:
        - router_data: List of existing routers, necessary for getting next router's index.

        Returns:
        - New router as a dictionary
        """
        id = RouterUtil._get_next_router_id(router_data)
        preview_path = RouterUtil.get_preview_path(id)
        return {
            "id": id,
            "preview_path": preview_path,
            "name": RouterUtil.ROUTER_DEFAULT_NAME,
            **RouterUtil._get_default_dimensions()
        }

    @staticmethod
    def _get_default_dimensions() -> Dict[str, Any]:
        """
        Returns a list of default dimensions for routers.
        """
        return {
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
    def _get_next_router_id(router_data: List[Dict[str, Any]]) -> int: 
        """
        Gets the next available router id.

        Arguments:
        - router_data: List of existing routers.

        Returns:
        - Next available index.
        """
        router_ids = [router.get('id') for router in router_data]
        return max(router_ids) + 1 if router_ids else 0

    @staticmethod
    def get_preview_path(id: int) -> str:
        """
        Gets the image preview path for the router with the given id.

        Arguments:
        - id: Target router id.

        Returns:
        - Preview path for router.
        """
        preview_path = os.path.join(ROUTER_PREVIEW_DATA_PATH, str(id)+'.png')
        return preview_path
    
    @staticmethod
    def save_router_preview(router_data: Dict[str, Any], figsize: tuple = (8, 8), dpi: int = 80):
        """
        Saves preview image for a router using matplotlib.

        Arguments:
        - router_data: Data for router to be saved in dict format.
        - figsize: width, height in inches (defaults to 4x4).
        - dpi: pixels per inch (defaults to 80).
        """
        try:
            image_path = router_data.get('preview_path')
            router_xy = (router_data.get("machineable_area_(x-axis)"), router_data.get("machineable_area_(y-axis)"))
            plate_xy = (router_data.get("max_plate_size_(x-axis)"), router_data.get("max_plate_size_(y-axis)"))
            safe_distance = router_data.get("min_safe_distance_from_edge")
            
        except KeyError:
            return

        if not all(coord is not None for coord in router_xy + plate_xy + (safe_distance,)):
            return

        router_x_offset = (plate_xy[0] - router_xy[0]) / 2
        router_y_offset = plate_xy[1] - router_xy[1]

        plate_rect_x, plate_rect_y = RouterUtil._generate_rectangle_coordinates(*plate_xy)
        router_rect_x, router_rect_y = RouterUtil._generate_rectangle_coordinates(*router_xy, router_x_offset, router_y_offset)
        safe_rect_x, safe_rect_y = RouterUtil._generate_rectangle_coordinates(*(dim - 2 * safe_distance for dim in plate_xy), safe_distance, safe_distance)

        plt.figure(figsize=figsize)

        plt.plot(plate_rect_x, plate_rect_y, color=RouterUtil.PLOT_LINE_COLOR, linestyle=':')
        plt.plot(router_rect_x, router_rect_y, color=RouterUtil.PLOT_LINE_COLOR)
        plt.plot(safe_rect_x, safe_rect_y, color=RouterUtil.PLOT_LINE_COLOR, linestyle='--')

        plt.grid(True)
        plt.gca().set_facecolor(RouterUtil.PLOT_BG_COLOR)
        plt.gca().set_aspect('equal') 
        plt.grid(False)
        plt.tick_params(axis='x', colors=RouterUtil.PLOT_TEXT_COLOR)
        plt.tick_params(axis='y', colors=RouterUtil.PLOT_TEXT_COLOR)

        plt.gca().spines['top'].set_color(RouterUtil.PLOT_TEXT_COLOR)
        plt.gca().spines['bottom'].set_color(RouterUtil.PLOT_TEXT_COLOR)
        plt.gca().spines['left'].set_color(RouterUtil.PLOT_TEXT_COLOR)
        plt.gca().spines['right'].set_color(RouterUtil.PLOT_TEXT_COLOR)

        plt.savefig(image_path, bbox_inches='tight', facecolor='#FFFFFF', dpi=dpi)
    
    @staticmethod
    def _generate_rectangle_coordinates(width: float, height: float, offset_x: float = 0, offset_y: float = 0):
        """
        Gets rectangle coordinates given width, height, and offset.

        Arguments:
        - width
        - height
        - offset_x
        - offset_y
        All arguments are floating point values.

        Returns:
        - Tuple of x and y coordinates in plotting format.
        """
        x_coordinates = [offset_x, offset_x + width, offset_x + width, offset_x, offset_x]
        y_coordinates = [offset_y, offset_y, offset_y + height, offset_y + height, offset_y]
        return x_coordinates, y_coordinates
            
