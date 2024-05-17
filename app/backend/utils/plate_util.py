import os
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any

from ...config import PLATE_PREVIEW_DATA_PATH, PROCESSING_SCALE_FACTOR

class PlateUtil:

    """
    Functional class for creating and modifying plate data. All constants are stored in millimeters.
    """
    
    MAX_DIMENSION = 5000
    DEFAULT_X = 1000
    DEFAULT_Y = 1000
    DEFAULT_Z = 10
    DEFAULT_MATERIAL = "Aluminum"

    PLOT_BG_COLOR = '#ffffff' 
    PLOT_TEXT_COLOR = '#000000'
    PLOT_LINE_COLOR = '#000000'

    @staticmethod
    def editable_keys() -> List[str]:
        """
        Returns a list of editable keys for plates. 
        """
        return [
            "width_(x)",
            "height_(y)",
            "thickness_(z)",
            "material"
        ]
    
    @staticmethod
    def value_ranges() -> Dict[str, Any]:
        """
        Returns a list of value ranges for relevant plate parameters.
        """
        return {
            "width_(x)": (0, PlateUtil.MAX_DIMENSION),
            "height_(y)": (0, PlateUtil.MAX_DIMENSION),
            "thickness_(z)": (0, PlateUtil.MAX_DIMENSION),
            "material": None
        }
    
    @staticmethod
    def get_new_plate(plate_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Returns a new plate based on existing plates.

        Arguments:
        - plate_data: List of existing plates, necessary for getting next plate's index.

        Returns:
        - New plate as a dictionary.
        """
        id = PlateUtil._get_next_plate_id(plate_data)
        preview_path = PlateUtil.get_preview_path(id)

        return {
            "id": id,
            "preview_path": preview_path,
            "width_(x)": PlateUtil.DEFAULT_X,
            "height_(y)": PlateUtil.DEFAULT_Y,
            "thickness_(z)": PlateUtil.DEFAULT_Z,
            "material": PlateUtil.DEFAULT_MATERIAL,
            "contours": None
        }
    
    @staticmethod
    def _get_next_plate_id(plate_data: List[Dict[str, Any]]) -> int: 
        """
        Gets the next available plate id.

        Arguments:
        - plate_data: List of existing plates.

        Returns:
        - Next available index.
        """
        plate_ids = [plate.get('id') for plate in plate_data]
        return max(plate_ids) + 1 if plate_ids else 0
 
    @staticmethod
    def get_preview_path(id: int) -> str:
        """
        Gets the image preview path for the plate with the given id.

        Arguments:
        - id: Target plate id.

        Returns:
        - Preview path for plate.
        """
        preview_path = os.path.join(PLATE_PREVIEW_DATA_PATH, str(id)+'.png')
        return preview_path

    # receives upscaled (processing resolution) contours, converts down
    @staticmethod
    def save_preview_image(plate_data: Dict[str, Any], figsize: tuple = (4, 4), dpi: int = 80):
        """
        Saves preview image for a plate using matplotlib.

        Arguments:
        - plate_data: Data for plate to be saved in dict format.
        - figsize: width, height in inches (defaults to 4x4).
        - dpi: pixels per inch (defaults to 80).
        """
        try:
            image_path = plate_data.get('preview_path')
            image_contours = plate_data.get("contours")
            plate_xy = (plate_data.get("width_(x)"), plate_data.get("height_(y)"))
            plate_rect_x, plate_rect_y = PlateUtil._generate_rectangle_coordinates(*plate_xy)

        except KeyError:
            return

        plt.figure(figsize=figsize)
        
        plt.plot(plate_rect_x, plate_rect_y, color = PlateUtil.PLOT_LINE_COLOR)

        if image_contours is not None:
            for contour in image_contours:
                contour_array = np.array(contour)
                x_coords = contour_array[:, 0, 0] / PROCESSING_SCALE_FACTOR
                y_coords = contour_array[:, 0, 1] / PROCESSING_SCALE_FACTOR
                plt.plot(x_coords, y_coords, color=PlateUtil.PLOT_LINE_COLOR, linewidth=1)

        plt.grid(True)
        plt.gca().set_facecolor(PlateUtil.PLOT_BG_COLOR)
        plt.gca().set_aspect('equal') 
        plt.grid(False)
        plt.tick_params(axis='x', colors=PlateUtil.PLOT_TEXT_COLOR)  
        plt.tick_params(axis='y', colors=PlateUtil.PLOT_TEXT_COLOR) 

        plt.gca().spines['top'].set_color(PlateUtil.PLOT_TEXT_COLOR) 
        plt.gca().spines['bottom'].set_color(PlateUtil.PLOT_TEXT_COLOR)
        plt.gca().spines['left'].set_color(PlateUtil.PLOT_TEXT_COLOR)
        plt.gca().spines['right'].set_color(PlateUtil.PLOT_TEXT_COLOR)

        plt.savefig(image_path, bbox_inches='tight', facecolor='#FFFFFF', dpi=dpi)

    @staticmethod
    def _generate_rectangle_coordinates(width: float, height: float, offset_x: float = 0, offset_y: float = 0) -> Tuple[List[float], List[float]]:
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
