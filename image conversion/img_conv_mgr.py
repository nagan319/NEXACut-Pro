import os
import numpy as np
import cv2
from typing import Tuple

from constants.image_conversion import *
from constants.hardware import PLATE_MAX_DIMENSION

from .img_io import *
from .img_proc import *
from .feat_mgr import FeatureManager

# image file only bounded to plate after svg is generated
# percent used will be calculated in different module

# missing svg functionality
class ImageConversionManager:

    def __init__(self, plate_size: Tuple[int, int, int], colors: Tuple): # plate size in mm

        for dimension in plate_size: # try except to be located outsize of class
            if dimension <= 0 or dimension > PLATE_MAX_DIMENSION:
                raise ValueError("Invalid plate size")

        if len(colors) != 5:
            raise ValueError("ImageConversionManager requires 5 colors to initialize")
        
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
            clear_all_files(PREVIEW_FOLDER_PATH)
        except(FileNotFoundError) as e:
            print(e)

    def save_external_image_as_raw(self, external_image_path): 
        try:
            self._check_state(NONE_STATE, NONE_STATE)
            image = read_image(external_image_path, True)
            image = resize_image(image, MAX_PROCESSING_WIDTH, MAX_PROCESSING_HEIGHT)
            write_image(PREVIEW_FOLDER_PATH, RAW_EXTENSION, image)
            self.state = RAW_STATE
                
        except(ValueError, FileExistsError, FileNotFoundError) as e:
            print(e)

    def save_binary_image(self, threshold_value: int = 100): 
        try:
            self._check_state(RAW_STATE, BINARY_STATE)
            raw_image_path = os.path.join(PREVIEW_FOLDER_PATH, RAW_EXTENSION)
            image = read_image(raw_image_path, True)
            image = convert_image_to_binary(image, threshold_value)
            write_image(PREVIEW_FOLDER_PATH, BINARY_EXTENSION, image)
            self.processing_resolution = image.shape[:2]
            self.state = BINARY_STATE
        
        except(ValueError, FileExistsError, FileNotFoundError) as e:
            print(e)
            
    def save_contour_image(self): # saves blank canvas with contours
        try:
            self._check_state(BINARY_STATE, BINARY_STATE)
            self.feature_manager.draw_features()
            image = self.feature_manager.feature_canvas
            write_image(PREVIEW_FOLDER_PATH, CONTOUR_EXTENSION, image)
            self.state = CONTOUR_STATE
        
        except(ValueError, FileExistsError, FileNotFoundError, NameError) as e:
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
            binary_image_path = os.path.join(PREVIEW_FOLDER_PATH, BINARY_EXTENSION)
            image = read_image(binary_image_path, True)
            self.__initialize_feature_manager()
            self.feature_manager.get_features(image)
            write_image(PREVIEW_FOLDER_PATH, CONTOUR_EXTENSION, image)

        except(FileNotFoundError, FileExistsError, ValueError, NameError) as e:
            print(e)

    def save_flattened_image(self):
        try:
            
            self._check_state(CONTOUR_STATE)
            contour_image_path = os.path.join(PREVIEW_FOLDER_PATH, CONTOUR_EXTENSION)
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

            write_image(PREVIEW_FOLDER_PATH, FLATTENED_EXTENSION, image)
            self.state = FLATTENED_STATE
            
        except(FileNotFoundError, FileExistsError, ValueError, NameError, TypeError) as e:
            print(e)    
