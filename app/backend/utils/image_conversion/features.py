import numpy as np
import cv2

from utils import Size, Colors

class Features:
    def __init__(self, plate_contour=None, other_contours=None, corners=None, selected_contour=None, selected_corner=None):
        self.plate_contour: np.ndarray = plate_contour
        self.other_contours: list = other_contours
        self.corners: list = corners
        self.selected_contour: int = selected_contour
        self.selected_corner: int = selected_corner


class FeatDetector:

    MIN_CTR_AREA = 1000
    MIN_CTR_DIST_FROM_EDGE = 100

    CORNER_DIST_DELTA = 16
    MIN_CORNER_ANGLE = 60
    MIN_CORNER_SEPARATION = 1000

    def __init__(self, src_path: str, size: Size):
        
        image = cv2.imread(src_path, cv2.IMREAD_GRAYSCALE)

        max_contour, other_contours = self._get_contours(image, size)

        if max_contour is not None:
            corners = self._get_corners(max_contour)

        self.features = Features(plate_contour=max_contour, other_contours=other_contours, corners=corners)
    
    def _get_contours(self, image, size: Size):

        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        filtered_contours = []

        for contour in contours:
            area = cv2.contourArea(contour)

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

    def _get_corners(self, max_contour: np.ndarray):

        corners = []
        length = len(max_contour)

        for i, point in enumerate(max_contour):

            delta: int = self.CORNER_DIST_DELTA

            prev_idx = (i - delta) % length 
            next_idx = (i + delta) % length

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

    def __init__(self, dst_path: str, size: Size, features: Features, colors: Colors):

        self.dst_path = dst_path
        self.size = size
        self.features = features
        self.colors = colors
    
    def save_features(self):

        canvas = np.zeros((self.size.h, self.size.w, 3), dtype=np.uint8)
        canvas[:, :] = list(self.colors.background_color)

        if self.features.plate_contour is not None:
            cv2.drawContours(canvas, self.features.plate_contour, -1, self.colors.plate_color, thickness=4)

        if self.features.other_contours is not None:
            cv2.drawContours(canvas, self.features.other_contours, -1, self.colors.contour_color, thickness=4)

        if self.features.selected_contour is not None:
            cv2.drawContours(canvas, self.features.other_contours, self.features.selected_contour, self.colors.selected_element_color, thickness=6)

        for i, corner in enumerate(self.features.corners):

            if i == self.features.selected_corner:
                color = self.colors.selected_element_color
                thickness = 6
            else:
                color = self.colors.corner_color
                thickness = 2

            cv2.circle(canvas, corner, radius=32, color=color, thickness=thickness)
        
        cv2.imwrite(self.dst_path, canvas)



class FeatEditor:

    def __init__(self, size: Size, features: Features):
        self.size = size
        self.features = features

    def select_corner(self, n: int):
        self.features.selected_corner = n
    
    def unselect_corner(self):
        self.features.selected_corner = None

    def select_contour(self, n: int):
        self.features.selected_contour = n

    def unselect_contour(self):
        self.features.selected_contour = None

    def remove_corner(self):
        if self.features.selected_corner is None:
            return
        self.features.corners.pop(self.features.selected_corner)
        self.unselect_corner()

    def remove_contour(self):
        if self.features.selected_contour is None:
            return
        self.features.other_contours.pop(self.features.selected_contour)
        self.unselect_contour()

    def add_corner(self, coordinates: tuple):
        x, y = coordinates  

        if not (0 <= x < self.size.w) or not (0 <= y < self.size.h):
            return
            
        new_corner = (x, y)
        self.features.corners.append(new_corner)
            