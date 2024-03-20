import numpy as np
import cv2
from typing import Tuple

from constants import MAX_PROCESSING_WIDTH, MAX_PROCESSING_HEIGHT, COLOR_DELETION_THRESHOLD

def resize_image(image, max_width: int, max_height: int): # resizes image to fit within max dimensions
        
    if max_width < 0 or max_width > MAX_PROCESSING_WIDTH:
        raise ValueError(f"New width value must be within range 0-"+MAX_PROCESSING_WIDTH)
    if max_height < 0 or max_height > MAX_PROCESSING_HEIGHT:
        raise ValueError(f"New height value must be within range 0-"+MAX_PROCESSING_HEIGHT)
    if len(image.shape) < 2 or len(image.shape) > 3:
        raise ValueError(f"Invalid image array")
    
    initial_height, initial_width = image.shape[:2]

    scale_factor = min(max_width / initial_width, max_height / initial_height)

    new_width = round(initial_width * scale_factor)
    new_height = round(initial_height * scale_factor)
    new_dim = (new_width, new_height)

    resized_image = cv2.resize(image, new_dim, interpolation=cv2.INTER_LANCZOS4) # high quality interpolation
    return resized_image
        
def convert_image_to_binary(image, threshold_value: int=100):
    
    if threshold_value < 0 or threshold_value > 255:
        raise ValueError("Threshold value must be in range 0-255")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # converts to grayscale, blurs
    image = cv2.GaussianBlur(image, (7, 7), 0)
    _, image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY) # applies binary threshold
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, np.ones((10, 10), np.uint8))
    return image
    
def apply_color_mask(image, background_color: Tuple[int, int, int], contour_color: Tuple[int, int, int]): # applies mask to get rid of excess contours
    range = COLOR_DELETION_THRESHOLD

    for value in background_color:
            if value > 255 or value < 0:
                raise ValueError("Background color values must be in range 0-255")
    for value in contour_color:
            if value > 255 or value < 0:
                raise ValueError("Contour color values must be in range 0-255")
            
    background_min = np.clip(np.array(background_color) - range, 0, 255)
    background_max = np.clip(np.array(background_color) + range, 0, 255)

    contour_min = np.clip(np.array(contour_color) - range, 0, 255)
    contour_max = np.clip(np.array(contour_color) + range, 0, 255)

    mask_background = cv2.inRange(image, background_min, background_max)
    mask_contour = cv2.inRange(image, contour_min, contour_max)

    combined_mask = cv2.bitwise_or(mask_background, mask_contour)
    final_image = cv2.bitwise_and(image, image, mask=combined_mask)

    return final_image

def get_transformation_matrix(src_points, dst_points):
    if len(src_points) != 4:
        raise ValueError("Image must have 4 corners")
    if len(dst_points) != 4:
        raise ValueError("Image must have 4 destination points")   
    for point in src_points, dst_points:
        if not isinstance(point, float):
            raise TypeError("Points must be in float format") 
        if len(point) != 2:
            raise ValueError("Points must consist of 2 coordinates")
        
    src_points = np.array(src_points, dtype=np.float32)
    dst_points = np.array(dst_points, dtype=np.float32)
    return cv2.getPerspectiveTransform(src_points, dst_points)

def warp_perspective(image, transformation_matrix, dimensions):
    width, height = dimensions

    if not isinstance(width, int):
        raise TypeError("Width must be an integer")
    if not isinstance(height, int):
        raise TypeError("Height must be an integer")
    if not isinstance(transformation_matrix, cv2.UMat):
        raise TypeError("Invalid value for transformation matrix")
    
    warped_image = cv2.warpPerspective(image, transformation_matrix, dimensions)
    return warped_image
    
     