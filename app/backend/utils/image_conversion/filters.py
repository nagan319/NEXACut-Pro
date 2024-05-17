import numpy as np
import cv2
from typing import Tuple, List

from .utils import Size, Colors

class BinaryFilter:
    """
    Filter for converting color image to thresholded binary. Assumes valid src and dst paths.

    ### Parameters:
    - src_path: source path.
    - dst_path: destination path.
    - threshold: threshold value that separates white from black, must be in range [0, 255].

    ### Raises
    - ValueError or TypeError if threshold value is invalid.
    """

    def __init__(self, src_path: str, dst_path: str, threshold: int):

        if threshold < 0 or threshold > 255:
            raise ValueError("Threshold value must be in range 0-255")
        
        if not isinstance(threshold, int):
            raise TypeError("Threshold must be integer value")
        
        self.threshold = threshold

        self.src_path = src_path
        self.dst_path = dst_path

        self.image = cv2.imread(self.src_path, cv2.IMREAD_COLOR)
    
    def save_image(self):
        """
        Saves thresholded image to dst path specified at initialization.
        """
        self._apply_binary_filter()
        cv2.imwrite(self.dst_path, self.image)

    def _apply_binary_filter(self):
        """
        Applies CV binary filter after preprocessing using Gaussian blur.
        """
        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) 
        image = cv2.GaussianBlur(image, (7, 7), 0)
        _, image = cv2.threshold(image, self.threshold, 255, cv2.THRESH_BINARY) 
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, np.ones((10, 10), np.uint8))
        self.image = image



class FlatFilter:
    """
    Filter for flattening 3D images to 2D based on plate corners. Assumes valid src and dst paths.

    ### Parameters:
    - src_path: source path.
    - dst_path: destination path.
    - size: size of output image.  
    - corners: List of corners containing four elements.

    ### Raises:
    - TypeError for invalid input types.
    - ValueError for invalid corner array.
    """

    COLOR_DELETION_THRESHOLD = 30

    def __init__(self, src_path: str, dst_path: str, size: Size, corners: List[Tuple[float, float]]):

        if not isinstance(size, Size):
            raise TypeError("size must be a Size object")
        if not isinstance(corners, list):
            raise TypeError("corners must be a list")
        if len(corners) != 4 or not all(isinstance(point, tuple) and len(point) == 2 for point in corners):
            raise ValueError("corners must be a list of four (x, y) tuples")

        self.src_path = src_path
        self.dst_path = dst_path

        self.size = size
        self.EDGE_THRESHOLD = int(min(size.w, size.h)//25)

        self.src_corners = self._sort_corners(corners)
        self.dst_corners = self._get_rect_corners(self.size)

    def _sort_corners(self, corners: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Sorts list of input corners in top left, top right, bottom left, and bottom right order.
        """
        avg_x = sum(point[0] for point in corners) / len(corners)
        avg_y = sum(point[1] for point in corners) / len(corners)
        sorted_corners = [None for _ in range(4)]

        for corner in corners:
            x, y = corner
            if x < avg_x and y < avg_y: 
                sorted_corners[0] = corner
            elif x > avg_x and y < avg_y: 
                sorted_corners[1] = corner
            elif x < avg_x and y > avg_y: 
                sorted_corners[2] = corner
            else:
                sorted_corners[3] = corner
        
        return sorted_corners

    def _get_rect_corners(self, size: Size) -> List[Tuple[float, float]]:
        """
        Returns array of rectangle corners based on input size.
        """
        top_left = [0, 0]
        top_right = [size.w, 0]
        bottom_right = [size.w, size.h]
        bottom_left = [0, size.h]
        return [top_left, top_right, bottom_left, bottom_right]

    def _get_transformation_matrix(self, src_pts: List[Tuple[float, float]], dst_pts: List[Tuple[float, float]]) -> np.ndarray:
        """
        Gets CV transformation matrix based on desired input and output points.

        Arguments:
        - src_pts: list of sorted input corners.
        - dst_pts: list of sorted output corners.

        Returns:
        - Numpy array containing CV transformation matrix.
        """
        src_pts = np.array(src_pts, dtype=np.float32)
        dst_pts = np.array(dst_pts, dtype=np.float32)
        return cv2.getPerspectiveTransform(src_pts, dst_pts)

    def _remove_edge_ctr(self, image, colors: Colors):
        """
        Removes edge contour from image by setting edge pixels to white. 

        Arguments: 
        - image: source image.
        - colors: color object.

        Returns:
        - Filtered image.
        """
        edge_width = self.EDGE_THRESHOLD

        height, width = image.shape[:2]

        mask = np.zeros((height, width), dtype=np.uint8)
        mask[:edge_width, :] = 255  
        mask[-edge_width:, :] = 255  
        mask[:, :edge_width] = 255  
        mask[:, -edge_width:] = 255  

        result_image = image.copy() 
        result_image[mask != 0] = colors.background_color

        return result_image

    def save_image(self):
        """
        Saves filtered image to dst path specified at initialization.
        """
        transformation_matrix = self._get_transformation_matrix(self.src_corners, self.dst_corners)
        image: np.ndarray = cv2.imread(self.src_path, cv2.IMREAD_COLOR)
        image = cv2.warpPerspective(image, transformation_matrix, (int(self.size.w), int(self.size.h)))
        image = self._remove_edge_ctr(image, Colors())
        cv2.imwrite(self.dst_path, image)
     