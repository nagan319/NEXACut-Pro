import math
import os
import numpy as np
import cv2
from typing import List, Tuple, Union

from .utils import Size, Colors

class Features:
    """
    Class for storing detected plate features (for use with non-flattened image).

    ### Parameters:
    - plate_contour: Main contour of plate.
    - other_contours: Other found contours.
    - corners: Plate corners.
    - selected_contour: Index of selected contour.
    - selected_corner: Index of selected corner.
    """
    def __init__(self, plate_contour: np.array=None, other_contours: List[np.array]=None, corners: List[tuple]=None, selected_contour_idx: int=None, selected_corner_idx: int=None):
        self.plate_contour: np.ndarray = plate_contour
        self.other_contours: List[np.array] = other_contours
        self.corners: List[tuple] = corners
        self.selected_contour_idx: int = selected_contour_idx
        self.selected_corner_idx: int = selected_corner_idx

class FeatDetector:
    """
    Class for retrieving critical features from plate image. Saves features in Features class as an attribute.

    ### Parameters:
    - src_path: Source image filepath.
    - size: Size of image.    

    ### Attributes:
    - features: Found features.
    
    ### Raises:
    - FileNotFoundError, ValueError for invalid input parameters.
    """
    MIN_CTR_AREA = 1000
    MIN_CTR_DIST_FROM_EDGE = 100

    CORNER_DIST_DELTA = 16
    MIN_CORNER_ANGLE = 60
    MIN_CORNER_SEPARATION = 1000

    def __init__(self, src_path: str, size: Size):
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"File '{src_path}' not found.")
        if size.w <= 0 or size.h <= 0:
            raise ValueError("Size dimensions must be positive numbers.")

        image = cv2.imread(src_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Unable to read image file '{src_path}'.")

        max_contour, other_contours = self._get_contours(image, size)
        corners = self._get_corners(max_contour) if max_contour is not None else None

        self.features = Features(plate_contour=max_contour, other_contours=other_contours, corners=corners)
    
    def _get_contours(self, image, size: Size) -> Tuple[np.array, List[np.array]]:
        """
        Finds contours that exceed area threshold and are a certain threshold away from the edge of the image. 
        """
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        filtered_contours: List[np.array] = []

        for contour in contours:
            area: float = cv2.contourArea(contour)

            if area < self.MIN_CTR_AREA:
                continue

            edge_flag = False

            for point in contour:
                x, y = point[0] # points stored as [[x, y]]

                epsilon: float = self.MIN_CTR_DIST_FROM_EDGE

                if x < epsilon or x > size.w - epsilon or y < epsilon or y > size.h - epsilon:
                    edge_flag = True
                    break
        
            if edge_flag and area < size.w * size.h // 4: # checks size in case plate is close to edge
                continue

            filtered_contours.append(contour)

        if not filtered_contours:
            return (None, None)
        
        areas = [cv2.contourArea(contour) for contour in filtered_contours]
        max_area_idx = areas.index(max(areas))
        max_contour = filtered_contours.pop(max_area_idx)
        other_contours = filtered_contours

        if len(other_contours) == 0:
            other_contours = None

        return max_contour, other_contours

    def _get_corners(self, max_contour: np.ndarray) -> List[Tuple[float, float]]:
        """
        Finds plate corners using derivatives and norm product.

        Arguments:
        - max_contour: Plate contour.
        
        Returns:
        - List of found corners stored as tuples of floats.
        """
        corners: List[Tuple[float, float]] = []
        length = len(max_contour)

        for i, point in enumerate(max_contour):

            delta: int = self.CORNER_DIST_DELTA

            prev_idx: int = (i - delta) % length 
            next_idx: int = (i + delta) % length

            x_prev, y_prev = max_contour[prev_idx][0]
            x, y = point[0]
            x_next, y_next = max_contour[next_idx][0]
            
            dx1, dy1 = x - x_prev, y - y_prev
            dx2, dy2 = x_next - x, y_next - y

            dot_product = dx1 * dx2 + dy1 * dy2
            norm_product = np.sqrt((dx1 ** 2 + dy1 ** 2) * (dx2 ** 2 + dy2 ** 2))

            if norm_product == 0:
                angle = 0
            else:
                cos_theta = max(min(dot_product / norm_product, 1.0), -1.0) # ensures valid range
                angle = np.arccos(cos_theta) * (180.0 / np.pi)

            if angle > self.MIN_CORNER_ANGLE:
                corners.append((x, y))

        filtered_corners = [corners[0]]  

        for i in range(1, len(corners)):
            distance = ((corners[i][0] - filtered_corners[-1][0]) ** 2 + (corners[i][1] - filtered_corners[-1][1]) ** 2) ** 0.5 
            if distance > self.MIN_CORNER_SEPARATION:
                filtered_corners.append(corners[i])

        return filtered_corners

class FeatDisplay: 
    """
    Saves features as an image.

    ### Parameters:
    - dst_path: Image save path.
    - size: Output image resolution.
    - features: Features to be mapped.
    - colors: Color palette to be used when saving.
    """
    def __init__(self, dst_path: str, size: Size, features: Features, colors: Colors):

        self.dst_path = dst_path
        self.size = size
        self.features = features
        self.colors = colors
    
    def save_features(self):
        """
        Saves images with properties specified at initialization.
        """
        canvas = np.zeros((self.size.h, self.size.w, 3), dtype=np.uint8)
        canvas[:, :] = list(self.colors.background_color)

        if self.features.plate_contour is not None:
            cv2.drawContours(canvas, self.features.plate_contour, -1, self.colors.plate_color, thickness=8)

        if self.features.other_contours is not None:
            cv2.drawContours(canvas, self.features.other_contours, -1, self.colors.contour_color, thickness=8)

        if self.features.selected_contour_idx is not None:
            cv2.drawContours(canvas, self.features.other_contours, self.features.selected_contour_idx, self.colors.selected_element_color, thickness=12)

        for i, corner in enumerate(self.features.corners):

            if i == self.features.selected_corner_idx:
                color = self.colors.selected_element_color
                thickness = 12
            else:
                color = self.colors.corner_color
                thickness = 8

            cv2.circle(canvas, corner, radius=32, color=color, thickness=thickness)
        
        cv2.imwrite(self.dst_path, canvas)



class FeatEditor:
    """
    Class for manually editing features.
    """
    def __init__(self, size: Size, features: Features, pixmap_height: int):
        self.size = size
        self.pixmap_height = pixmap_height
        self.pixmap_scale_factor = pixmap_height/self.size.h
        self.features = features

    def select_corner(self, n: int):
        self.features.selected_corner_idx = n
    
    def unselect_corner(self):
        self.features.selected_corner_idx = None

    def select_contour(self, n: int):
        self.features.selected_contour_idx = n

    def unselect_contour(self):
        self.features.selected_contour_idx = None

    def remove_corner(self):
        if self.features.selected_corner_idx is None:
            return
        self.features.corners.pop(self.features.selected_corner_idx)
        self.unselect_corner()

    def remove_contour(self):
        if self.features.selected_contour_idx is None:
            return
        self.features.other_contours.pop(self.features.selected_contour_idx)
        self.unselect_contour()

    def add_corner(self, coordinates: tuple):

        x, y = coordinates  
        x_scaled, y_scaled = int(x/self.pixmap_scale_factor), int(y/self.pixmap_scale_factor)

        if not (0 <= x_scaled < self.size.w) or not (0 <= y_scaled < self.size.h):
            return
            
        new_corner = (x_scaled, y_scaled)
        self.features.corners.append(new_corner)

    def feature_selected(self, coordinates: tuple) -> bool:

        MIN_DISTANCE = 20
        
        for i, contour in enumerate(self.features.other_contours):

            for point in contour[::int(MIN_DISTANCE*2)]:
    
                point_scaled = (point[0][0]*self.pixmap_scale_factor, point[0][1]*self.pixmap_scale_factor)

                if self._is_close(coordinates, point_scaled, MIN_DISTANCE):
                    self.unselect_corner()
                    self.select_contour(i)
                    return True
                
        for i, corner in enumerate(self.features.corners):

            corner_scaled = (coordinate * self.pixmap_scale_factor for coordinate in corner)

            if self._is_close(coordinates, corner_scaled, MIN_DISTANCE):
                self.unselect_contour()
                self.select_corner(i)
                return True
        
        return False
    
    def _is_close(self, point_1: tuple, point_2: tuple, threshold: int):
        x1, y1 = point_1
        x2, y2 = point_2
        distance = math.sqrt(abs(x2 - x1)**2 + abs(y2 - y1)**2)
        return distance <= threshold
