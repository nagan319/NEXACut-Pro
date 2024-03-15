import os
import numpy as np
import cv2
from typing import Tuple

from constants import *

# module interacts directly with files in image preview folder
# image file only bounded to plate after svg is generated
# percent used will be calculated in different module

# missing svg functionality
class ImageProcessor:

    # configure init to run with preferences file
    def __init__(self, plate_size: Tuple[int, int, int] = (100, 100, 10)): # plate size in mm

        self.state = none_state
        self.processing_resolution = []

        for dimension in plate_size: # try except to be located outsize of class
            if dimension <= 0 or dimension > plate_max_dimension:
                raise ValueError("Invalid plate size")

        self.output_resolution = [plate_size[0]*max_resolution, plate_size[1]*max_resolution]

        self.contours = []
        self.largest_contour = []
        self.selected_contour = None

        self.minimum_contour_area = 1500
        self.minimum_contour_distance_from_edge = 100

        self.contour_color = (30, 144, 255)
        self.selected_element_color = (255, 255, 255)
        self.plate_edge_color = (255, 165, 0)
        self.corner_color = (153, 102, 204)

        self.corners = []
        self.selected_corner = None

    def clear_preview(self): # clears all files in image preview folder
        files = os.listdir(preview_path)
    
        for file_name in files:
            file_path = os.path.join(preview_path, file_name)
            os.remove(file_path)

    # raw image generation

    def save_external_image_as_raw(self, path): # this assumes reading an image from the tray, i.e. file checks not necessary

        try:
            if self.state != none_state:
                raise FileExistsError("Raw image already imported")
                
        except(FileExistsError) as e:
            print(e)
            return
        
        else:
            image = cv2.imread(path, cv2.IMREAD_COLOR)
            image = self.resize_image(image, processing_max_width, processing_max_height)
            cv2.imwrite(preview_path+raw_extension, image) # saves all images as png

            self.processing_resolution = image.shape[:2]
            self.state = raw_state

    def resize_image(self, image, max_width: int, max_height: int): # resizes image to fit within max dimensions
        
        try:
            if max_width < 0 or max_width > processing_max_width:
                raise ValueError(f"New width value must be within range 0-"+processing_max_width)
            if max_height < 0 or max_height > processing_max_height:
                raise ValueError(f"New height value must be within range 0-"+processing_max_height)
            if len(image.shape) < 2 or len(image.shape) > 3:
                raise ValueError(f"Invalid image array")
            
        except(ValueError) as e:
            print(e)
            return
        
        else:
            initial_height, initial_width = image.shape[:2]

            scale_factor = min(max_width / initial_width, max_height / initial_height)

            new_width = round(initial_width * scale_factor)
            new_height = round(initial_height * scale_factor)
            new_dim = (new_width, new_height)

            resized_img = cv2.resize(image, new_dim, interpolation=cv2.INTER_LANCZOS4) # high quality interpolation
            return resized_img

    # binary image generation

    def save_binary_image(self, threshold_value: int = 100): # saves binary image 

        raw_image_path = preview_path + raw_extension

        try:
            if not os.path.exists(raw_image_path):
                raise FileNotFoundError(f"The file {raw_image_path} does not exist")
            if not (self.state == raw_state or self.state == binary_state):
                raise FileExistsError("Contours already finalized")
        
        except(FileNotFoundError, FileExistsError) as e:
            print(e)
            return
        
        else:
            image = cv2.imread(raw_image_path, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # converts to grayscale, blurs
            image = cv2.GaussianBlur(image, (7, 7), 0)
            _, image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY) # applies binary threshold
            image = cv2.morphologyEx(image, cv2.MORPH_OPEN, np.ones((10, 10), np.uint8)) # gets rid of random noise

            cv2.imwrite(preview_path + binary_extension, image) # saves all images as png
            self.state = binary_state

    # feature generation

    def save_contour_image(self): # draws contours on image
        
        try:
            if self.state <= raw_state:
                raise FileNotFoundError("Binary image not yet generated")
            elif self.state >= flattened_state: 
                raise FileExistsError("Contours already finalized")
            if not self.contours or not self.largest_contour or not self.corners:
                raise ValueError("Image features not defined")

        except(FileNotFoundError, FileExistsError, ValueError) as e:
            print(e)
            return
        
        else:
            height, width = self.processing_resolution
            contour_canvas = np.zeros((height, width, 3), dtype=np.uint8)

            cv2.drawContours(contour_canvas, self.contours, -1, self.contour_color, thickness=4)
            cv2.drawContours(contour_canvas, self.largest_contour, -1, self.plate_edge_color, thickness=4)

            if self.selected_contour is not None:
                cv2.drawContours(contour_canvas, self.contours, self.selected_contour, self.selected_element_color, thickness=6)

            for i, corner in enumerate(self.corners):
                color, thickness = self.selected_element_color, 6 if i == self.selected_corner else self.corner_color, 2
                cv2.circle(contour_canvas, corner, radius=32, color=color, thickness=thickness)
            
            cv2.imwrite(preview_path + contour_extension, contour_canvas)
            self.state = contour_state

    # automatic feature detection

    def detect_features(self):
        binary_image_path = preview_path + binary_extension

        try:
            if not os.path.exists(binary_image_path):
                raise FileNotFoundError(f"The file {binary_image_path} does not exist")
            if not (self.state == binary_state or self.state == contour_state):
                raise FileExistsError("Flattened image already generated")
        
        except(FileNotFoundError, FileExistsError) as e:
            print(e)
            return
        
        else:
            image = cv2.imread(binary_image_path, cv2.IMREAD_GRAYSCALE)

            contours, largest_contour = self.detect_contours(image)

            self.contours = contours
            self.largest_contour = largest_contour

            corners = self.detect_corners()
            self.corners = corners
    
    def detect_contours(self, image) -> Tuple[list, list]: # only called by one method, few checks necessary - returns contours and max contour
        
        try: 
            width, height = self.processing_resolution
            if width <= 0 or height <= 0:
                raise ValueError("Invalid image dimension values")
        
        except(ValueError) as e:
            print(e)
            return
        
        else:
            contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            filtered_contours = []

            for contour in contours:
                area = cv2.contourArea(contour)

                if area < self.minimum_contour_area:
                    continue

                edge_flag = False
                for point in contour:
                    x, y = point[0] # points stored as [[x, y]]

                    if x < self.minimum_contour_distance_from_edge or x > width - self.minimum_contour_distance_from_edge or y < self.minimum_contour_distance_from_edge or y > width - self.minimum_contour_distance_from_edge:
                        edge_flag = True
                        break
            
                if edge_flag and area < width*height/4: # checks size in case plate is close to edge
                    continue

                filtered_contours.append(contour)
            
            try:
                if not filtered_contours:
                    raise ValueError("No contours found")
            
            except(ValueError) as e:
                print(e)
                return
            
            else:
                areas = [cv2.contourArea(contour) for contour in filtered_contours]
                max_area_idx = areas.index(max(areas))
                max_contour = filtered_contours[max_area_idx]
                filtered_contours.remove(max_contour)

                return filtered_contours, max_contour

    def detect_corners(self):

        try:
            if not self.largest_contour:
                raise ValueError("Plate contour not detected")
        
        except(ValueError) as e:
            print(e)
            return
        
        else:
            corners = []
            length = len(self.largest_contour)

            # searches for contour points with large angle between them

            for i, point in enumerate(self.largest_contour):
                prev_idx = (i - corner_search_point_delta) % length # compares slightly distant points to avoid diagonal angles
                next_idx = (i + corner_search_point_delta) % length

                x_prev, y_prev = self.largest_contour[prev_idx][0]
                x, y = point[0]
                x_next, y_next = self.largest_contour[next_idx][0]
                
                # gets derivative between adjacent points
                dx1, dy1 = x - x_prev, y - y_prev
                dx2, dy2 = x_next - x, y_next - y

                # gets angle between points using dot product
                dot_product = dx1 * dx2 + dy1 * dy2
                norm_product = np.sqrt((dx1 ** 2 + dy1 ** 2) * (dx2 ** 2 + dy2 ** 2))
                if norm_product == 0:
                    angle = 0
                else:
                    cos_theta = max(min(dot_product / norm_product, 1.0), -1.0) # ensures valid range
                    angle = np.arccos(cos_theta) * (180.0 / np.pi)

                if angle > min_corner_angle:
                    corners.append((x, y))

            # removes duplicate adjacent corners

            filtered_corners = [corners[0]]  

            for i in range(1, len(corners)):
                distance = ((corners[i][0] - filtered_corners[-1][0]) ** 2 + (corners[i][1] - filtered_corners[-1][1]) ** 2) ** 0.5 # pythagorean formula
                if distance > min_corner_separation:
                    filtered_corners.append(corners[i])
    
            return filtered_corners

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

    # flattened image generation

    def save_flattened_image(self):
        contour_image_path = preview_path + contour_extension

        try:
            if not os.path.exists(contour_image_path):
                raise FileNotFoundError(f"The file {contour_image_path} does not exist")
            if self.state < contour_state:
                raise FileNotFoundError("No image to flatten")
            elif self.state > contour_state:
                raise FileExistsError("Flattened image already finalized")
            if self.largest_contour:
                raise ValueError("Image contour not defined")
            if len(self.corners) != 4:
                raise ValueError("Image must have 4 corners")

        except(FileNotFoundError, FileExistsError, ValueError) as e:
            print(e)
            return
        
        else:
            image = cv2.imread(contour_image_path, cv2.IMREAD_COLOR)
            self.sort_corners()

            width, height = self.output_resolution
            top_left = [0, 0]
            top_right = [width, 0]
            bottom_right = [width, height]
            bottom_left = [0, height]

            final_corner_points = np.array([top_left, top_right, bottom_left, bottom_right], dtype=np.float32)

            transformation_matrix = self.get_transformation_matrix(self.corners, final_corner_points) # maps corners to new locations
            image = cv2.warpPerspective(image, transformation_matrix, (width, height))
            image = self.hide_unnecessary_features(image)

            flattened_image_path = preview_path+flattened_extension
            cv2.imwrite(flattened_image_path, image)
            self.state = flattened_state

    def sort_corners(self): # check already done in method call
        centroid_x = sum(point[0] for point in self.corners) / len(self.corners)
        centroid_y = sum(point[1] for point in self.corners) / len(self.corners)
        sorted_corners = np.copy(self.corners)

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
        
        self.corners = sorted_corners

    def get_transformation_matrix(self, src_points: np.array, dst_points: np.array): # check already in method call
        src_points = np.array(src_points, dtype=np.float32)
        dst_points = np.array(dst_points, dtype=np.float32)
        return cv2.getPerspectiveTransform(src_points, dst_points)

    def hide_unnecessary_features(self, image): # applies mask to get rid of excess contours
        black = np.array([0, 0, 0]) 
        range = 32

        contour_min = np.clip(np.array(self.contour_color) - range, 0, 255)
        contour_max = np.clip(np.array(self.contour_color) + range, 0, 255)

        mask_bg = cv2.inRange(image, black, black)
        mask_contour = cv2.inRange(image, contour_min, contour_max)

        combined_mask = cv2.bitwise_or(mask_bg, mask_contour)
        result = cv2.bitwise_and(image, image, mask=combined_mask)

        return result
