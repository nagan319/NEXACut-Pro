import os
import sys
import numpy as np
import cv2
from typing import Tuple

from .constants import MAX_PPMM, MAX_PROCESSING_WIDTH, MAX_PROCESSING_HEIGHT, NONE_STATE, RAW_STATE, BINARY_STATE, CONTOUR_STATE, FLATTENED_STATE, RAW_EXTENSION, BINARY_EXTENSION, CONTOUR_EXTENSION, FLATTENED_EXTENSION 

import app.utils.image_conversion.img_util as img_util
from .feat_mgr import FeatureManager

class ImageConverter:

    def __init__(self, preview_folder_path: str, plate_size: Tuple[int, int, int], colors: Tuple): 

        if not os.path.exists(preview_folder_path):
            raise FileNotFoundError("Indicated preview path does not exist")

        if len(colors) != 5:
            raise ValueError("ImageConverter requires 5 colors to initialize")
        
        for color in colors:
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

        self.colors = colors # necessary for feature controller
        self.background_color = colors[0]
        self.contour_color = colors[1]
        self.selected_element_color = colors[2]
        self.plate_edge_color = colors[3]
        self.corner_color = colors[4]

    def _check_state(self, min_state, max_state):
        if self.state < min_state:
            raise FileNotFoundError("Invalid state: {}".format(self.state))
        elif self.state > max_state:
            raise FileExistsError("Operation already finalized")

    def reset_preview(self):
        try:
            img_util.clear_all_files(self.preview_folder_path)
        except(Exception) as e:
            print(e)

    def save_external_image_as_raw(self, external_image_path): 
        try:
            self._check_state(NONE_STATE, NONE_STATE)
            image = img_util.read_image(external_image_path, True)
            image = img_util.resize_image(image, MAX_PROCESSING_WIDTH, MAX_PROCESSING_HEIGHT)
            img_util.write_image(self.preview_folder_path, RAW_EXTENSION, image)
            self.state = RAW_STATE
                
        except(Exception) as e:
            print(e)

    def save_binary_image(self, threshold_value: int = 100): 
        try:
            self._check_state(RAW_STATE, BINARY_STATE)
            raw_image_path = os.path.join(self.preview_folder_path, RAW_EXTENSION)
            image = img_util.read_image(raw_image_path, True)
            image = img_util.convert_image_to_binary(image, threshold_value)
            img_util.write_image(self.preview_folder_path, BINARY_EXTENSION, image)
            self.processing_resolution = image.shape[:2]
            self.state = BINARY_STATE
        
        except(Exception) as e:
            print(e)
            
    def save_contour_image(self): # saves blank canvas with contours
        try:
            self._check_state(BINARY_STATE, BINARY_STATE)
            self.feature_manager.draw_features()
            image = self.feature_manager.feature_canvas
            img_util.write_image(self.preview_folder_path, CONTOUR_EXTENSION, image)
            self.state = CONTOUR_STATE
        
        except(Exception) as e:
            print(e)

    def __initialize_feature_manager(self):
        if not self.processing_resolution:
            raise ValueError("Processing resolution not initialized")
        if not self.colors: 
            raise ValueError("Color palletes not initialized")
        self.feature_manager = FeatureManager(self.processing_resolution, self.colors)
    
    def get_contours_from_binary(self):
        try:
            self._check_state(BINARY_STATE, CONTOUR_STATE)
            binary_image_path = os.path.join(self.preview_folder_path, BINARY_EXTENSION)
            image = img_util.read_image(binary_image_path, True)
            self.__initialize_feature_manager()
            self.feature_manager.get_features(image)
            img_util.write_image(self.preview_folder_path, CONTOUR_EXTENSION, image)

        except(Exception) as e:
            print(e)

    def save_flattened_image(self):
        try:
            
            self._check_state(CONTOUR_STATE)
            contour_image_path = os.path.join(self.preview_folder_path, CONTOUR_EXTENSION)
            image = img_util.read_image(contour_image_path, True)
            width, height = self.output_resolution

            top_left = [0, 0]
            top_right = [width, 0]
            bottom_right = [width, height]
            bottom_left = [0, height]

            initial_corner_points = self.feature_manager.corners
            final_corner_points = np.array([top_left, top_right, bottom_left, bottom_right], dtype=np.float32)

            transformation_matrix = img_util.get_transformation_matrix(initial_corner_points, final_corner_points)
            image = img_util.warp_perspective(image, transformation_matrix, (width, height))
            image = img_util.apply_color_mask(image, self.background_color, self.contour_color)

            img_util.write_image(self.preview_folder_path, FLATTENED_EXTENSION, image)
            self.state = FLATTENED_STATE
            
        except(Exception) as e:
            print(e)    
