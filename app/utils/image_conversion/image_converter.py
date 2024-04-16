import os
import sys
import numpy as np
import cv2
from typing import Tuple
import traceback

from .constants import *

from .util_funcs import read_image, write_image, resize_image, convert_image_to_binary, apply_color_mask, get_transformation_matrix, warp_perspective, clear_all_files
from .feat_mgr import FeatureManager

class ImageConverter:

    def __init__(self, preview_folder_path: str, plate_size: Tuple[int, int, int], colors: dict = DEFAULT_COLORS): 

        if not os.path.exists(preview_folder_path):
            raise FileNotFoundError("Indicated preview path does not exist")
        
        for color in colors.values():
            if len(color) != 3:
                raise ValueError("Colors must be comprised of 3 integers")
            
            for value in color:
                if not isinstance(value, int):
                    raise ValueError("Colors must be comprised of 3 integers")
                if value < 0 or value > 255:
                    raise ValueError("Color values must be in range 0-255")

        self.state = NONE_STATE
        self.output_resolution = [plate_size[0]*MAX_PPMM, plate_size[1]*MAX_PPMM]

        self.preview_folder_path = preview_folder_path

        try:
            self.colors = colors # necessary for feature controller
            self.background_color = colors['background_color']
            self.contour_color = colors['contour_color']
            self.selected_element_color = colors['selected_element_color']
            self.plate_edge_color = colors['plate_edge_color']
            self.corner_color = colors['corner_color']
        except(KeyError):
            raise KeyError("Color dict missing keys")
        
        self.feature_manager = FeatureManager(self.output_resolution, self.colors)

    def _check_state(self, min_state, max_state):
        if self.state < min_state:
            raise FileNotFoundError("Invalid state: {}".format(self.state))
        elif self.state > max_state:
            raise FileExistsError("Operation already finalized")

    def reset_preview(self):
        try:
            clear_all_files(self.preview_folder_path)
        except(Exception):
            traceback.print_exc()

    def save_external_image_as_raw(self, external_image_path): 
        try:
            self._check_state(NONE_STATE, NONE_STATE)
            image = read_image(external_image_path, True)
            image = resize_image(image, MAX_PROCESSING_WIDTH, MAX_PROCESSING_HEIGHT)
            write_image(self.preview_folder_path, RAW_EXTENSION, image)
            self.state = RAW_STATE
                
        except(Exception):
            traceback.print_exc()

    def save_binary_image(self, threshold_value: int = 100): 
        try:
            self._check_state(RAW_STATE, BINARY_STATE)
            raw_image_path = os.path.join(self.preview_folder_path, RAW_EXTENSION)
            image = read_image(raw_image_path, True)
            image = convert_image_to_binary(image, threshold_value)
            write_image(self.preview_folder_path, BINARY_EXTENSION, image)
            self.processing_resolution = image.shape[:2]
            self.state = BINARY_STATE
        
        except(Exception):
            traceback.print_exc()
            
    def save_contour_image(self): # saves blank canvas with contours
        try:
            self._check_state(BINARY_STATE, BINARY_STATE)
            self.feature_manager.draw_features()
            image = self.feature_manager.feature_canvas
            write_image(self.preview_folder_path, CONTOUR_EXTENSION, image)
            self.state = CONTOUR_STATE
        
        except(Exception):
            traceback.print_exc()
    
    def get_contours_from_binary(self):
        try:
            binary_image_path = os.path.join(self.preview_folder_path, BINARY_EXTENSION)
            image = read_image(binary_image_path, True)
            self.feature_manager.get_features(image)

        except(Exception):
            traceback.print_exc()

    def save_flattened_image(self):
        try:
            
            self._check_state(CONTOUR_STATE)
            contour_image_path = os.path.join(self.preview_folder_path, CONTOUR_EXTENSION)
            image = read_image(contour_image_path, True)
            width, height = self.output_resolution

            top_left = [0, 0]
            top_right = [width, 0]
            bottom_right = [width, height]
            bottom_left = [0, height]

            initial_corner_points = self.feature_manager.corners
            final_corner_points = np.array([top_left, top_right, bottom_left, bottom_right], dtype=np.float32)

            transformation_matrix = get_transformation_matrix(initial_corner_points, final_corner_points)
            image = warp_perspective(image, transformation_matrix, (width, height))
            image = apply_color_mask(image, self.background_color, self.contour_color)

            write_image(self.preview_folder_path, FLATTENED_EXTENSION, image)
            self.state = FLATTENED_STATE
            
        except(Exception):
            traceback.print_exc()    
