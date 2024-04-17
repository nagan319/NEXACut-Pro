import numpy as np
import cv2
from typing import Tuple

from .feat_detect import detect_contours, detect_corners

class FeatureManager:
    
    def __init__(self, processing_resolution: Tuple[int, int], colors: dict): # checks for all values carried out in ImageConversionManager

        self.background_color = colors['background_color']           
        self.contour_color = colors['contour_color']
        self.selected_element_color = colors['selected_element_color']
        self.plate_edge_color = colors['plate_edge_color']
        self.corner_color = colors['corner_color']

        self.feature_canvas = None
        self.processing_resolution = processing_resolution

        self.contours = []
        self.largest_contour = []
        self.selected_contour = None

        self.corners = []
        self.selected_corner = None

    def get_features(self, image):
        try: 
            self.contours, self.largest_contour = detect_contours(image, self.processing_resolution)
            self.corners = detect_corners(self.largest_contour)
            print(f"Contours: {self.contours} \nCorners: {self.corners}")

        except(ValueError) as e:
            raise e

    def draw_features(self):

        if len(self.largest_contour) == 0 or len(self.corners) == 0:
            raise ValueError("No features detected")

        height, width = self.processing_resolution
        canvas = np.zeros((height, width, 3), dtype=np.uint8)

        cv2.drawContours(canvas, self.contours, -1, self.contour_color, thickness=4)
        cv2.drawContours(canvas, self.largest_contour, -1, self.plate_edge_color, thickness=4)

        if self.selected_contour is not None:
            cv2.drawContours(canvas, self.contours, self.selected_contour, self.selected_element_color, thickness=6)

        for i, corner in enumerate(self.corners):
            color, thickness = self.selected_element_color, 6 if i == self.selected_corner else self.corner_color, 2
            cv2.circle(canvas, corner, radius=32, color=color, thickness=thickness)
        
        self.feature_canvas = canvas

    def sort_corners(corners: Tuple[float, float]): # fix
    
        try:
            if len(corners) != 4:
                raise ValueError("4 corners required")

        except(ValueError) as e:
            print(e)
            return

        else:
            centroid_x = sum(point[0] for point in corners) / len(corners)
            centroid_y = sum(point[1] for point in corners) / len(corners)
            sorted_corners = np.copy(corners)

            for corner in sorted_corners:
                x, y = corner
                if x < centroid_x and y < centroid_y: # top left
                    sorted_corners[0] = corner
                elif x > centroid_x and y < centroid_y: # top right
                    sorted_corners[1] = corner
                elif x < centroid_x and y > centroid_y: # bottom left
                    sorted_corners[2] = corner
                else:
                    sorted_corners[3] = corner
            
            return sorted_corners

    # manual feature editing

    def select_corner(self, n: int):
        try:
            if self.corners is None:
                raise ValueError('No corners detected')
            if n < 0 or n >= len(self.corners):
                raise ValueError('Corner index out of bounds')
            
        except(ValueError) as e:
            print(e)
            return
        
        else:
            self.select_corner = n
    
    def unselect_corner(self):
        self.selected_corner = None

    def remove_corner(self):
        try:
            if self.selected_corner is None:
                raise ValueError("No corner selected")
        
        except(ValueError) as e:
            print(e)
            return
        
        else:
            self.corners.pop(self.selected_corner)
            self.unselect_corner()

    def add_corner(self, coordinates: Tuple[int, int]):
        x, y = coordinates  

        try: 
            if len(self.processing_resolution) < 2:
                raise ValueError("Processed resolution undefined")
            elif not (0 <= x < self.processing_resolution[1] and 0 <= y < self.processing_resolution[0]):
                raise ValueError("Coordinates out of bound, max values are: " + str(self.processing_resolution[1]), str(self.processing_resolution[0]))
            
        except(ValueError) as e:
            print(e)
            return

        else:
            new_corner = np.array([x, y], dtype=np.int32) 
            self.corners.append(new_corner)

    def select_contour(self, n: int):
        try:
            if self.contours is None:
                raise ValueError('No removable contours detected')
            if n < 0 or n >= len(self.contours):
                raise ValueError('Contour index out of bounds')
            
        except(ValueError) as e:
            print(e)
            return
        
        else:
            self.select_contour = n

    def unselect_contour(self):
        self.selected_contour = None

    def remove_contour(self):
        try:
            if self.selected_contour is None:
                raise ValueError("No contour selected")
        
        except(ValueError) as e:
            print(e)
            return
        
        else:
            self.contours.pop(self.selected_contour)
            self.unselect_contour()