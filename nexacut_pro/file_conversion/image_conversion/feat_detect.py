import numpy as np
import cv2
from typing import Tuple

from constants import MIN_CONTOUR_AREA, MIN_CONTOUR_DISTANCE_FROM_EDGE, CORNER_SEARCH_POINT_DELTA, MIN_CORNER_ANGLE, MIN_CORNER_SEPARATION

def detect_contours(image, processing_resolution) -> Tuple[list, list]: # returns (all contours except max, max contour)
        
    width, height = processing_resolution
    if width <= 0 or height <= 0:
        raise ValueError("Invalid image dimension values")

    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    filtered_contours = []

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < MIN_CONTOUR_AREA:
            continue

        edge_flag = False
        for point in contour:
            x, y = point[0] # points stored as [[x, y]]

            if x < MIN_CONTOUR_DISTANCE_FROM_EDGE or x > width - MIN_CONTOUR_DISTANCE_FROM_EDGE or y < MIN_CONTOUR_DISTANCE_FROM_EDGE or y > width - MIN_CONTOUR_DISTANCE_FROM_EDGE:
                edge_flag = True
                break
    
        if edge_flag and area < width*height/4: # checks size in case plate is close to edge
            continue

        filtered_contours.append(contour)

    if not filtered_contours:
        raise ValueError("No contours found")
    
    areas = [cv2.contourArea(contour) for contour in filtered_contours]
    max_area_idx = areas.index(max(areas))
    max_contour = filtered_contours[max_area_idx]
    filtered_contours.remove(max_contour)

    return filtered_contours, max_contour

def detect_corners(contour):

    if not contour:
        raise ValueError("Plate contour not detected")

    corners = []
    length = len(contour)

    # searches for contour points with large angle between them

    for i, point in enumerate(contour):
        prev_idx = (i - CORNER_SEARCH_POINT_DELTA) % length # compares slightly distant points to avoid diagonal angles
        next_idx = (i + CORNER_SEARCH_POINT_DELTA) % length

        x_prev, y_prev = contour[prev_idx][0]
        x, y = point[0]
        x_next, y_next = contour[next_idx][0]
        
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

        if angle > MIN_CORNER_ANGLE:
            corners.append((x, y))

    # removes duplicate adjacent corners

    filtered_corners = [corners[0]]  

    for i in range(1, len(corners)):
        distance = ((corners[i][0] - filtered_corners[-1][0]) ** 2 + (corners[i][1] - filtered_corners[-1][1]) ** 2) ** 0.5 # pythagorean formula
        if distance > MIN_CORNER_SEPARATION:
            filtered_corners.append(corners[i])

    return filtered_corners