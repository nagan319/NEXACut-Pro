import numpy as np
import cv2

from .utils import Size, Colors

class BinaryFilter:

    def __init__(self, src_path: str, dst_path: str, threshold: int):

        if threshold < 0 or threshold > 255:
            raise ValueError("Threshold value must be in range 0-255")
        
        self.threshold = threshold

        self.src_path = src_path
        self.dst_path = dst_path

        self.image = cv2.imread(self.src_path, cv2.IMREAD_COLOR)
    
    def save_image(self):

        self._apply_binary_filter()
        cv2.imwrite(self.dst_path, self.image)

    def _apply_binary_filter(self):

        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) 
        image = cv2.GaussianBlur(image, (7, 7), 0)
        _, image = cv2.threshold(image, self.threshold, 255, cv2.THRESH_BINARY) 
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, np.ones((10, 10), np.uint8))
        self.image = image



class FlatFilter:

    COLOR_DELETION_THRESHOLD = 30

    def __init__(self, src_path: str, dst_path: str, size: Size, corners: list):

        self.src_path = src_path
        self.dst_path = dst_path

        self.size = size
        self.EDGE_THRESHOLD = int(min(size.w, size.h)//25)

        self.src_corners = self._sort_corners(corners)
        self.dst_corners = self._get_rect_corners(self.size)

    def _sort_corners(self, corners: list) -> list:

        avg_x = sum(point[0] for point in corners) / len(corners)
        avg_y = sum(point[1] for point in corners) / len(corners)
        sorted_corners = [None for _ in range(4)]

        for corner in corners:
            x, y = corner
            if x < avg_x and y < avg_y: # top left
                sorted_corners[0] = corner
            elif x > avg_x and y < avg_y: # top right
                sorted_corners[1] = corner
            elif x < avg_x and y > avg_y: # bottom left
                sorted_corners[2] = corner
            else:
                sorted_corners[3] = corner
        
        return sorted_corners

    def _get_rect_corners(self, size: Size) -> list:
        top_left = [0, 0]
        top_right = [size.w, 0]
        bottom_right = [size.w, size.h]
        bottom_left = [0, size.h]
        return [top_left, top_right, bottom_left, bottom_right]

    def _get_transformation_matrix(self, src_pts: list, dst_pts: list) -> np.ndarray:
        src_pts = np.array(src_pts, dtype=np.float32)
        dst_pts = np.array(dst_pts, dtype=np.float32)
        return cv2.getPerspectiveTransform(src_pts, dst_pts)

    def _remove_edge_ctr(self, image, colors: Colors):

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
        transformation_matrix = self._get_transformation_matrix(self.src_corners, self.dst_corners)
        image: np.ndarray = cv2.imread(self.src_path, cv2.IMREAD_COLOR)
        image = cv2.warpPerspective(image, transformation_matrix, (int(self.size.w), int(self.size.h)))
        image = self._remove_edge_ctr(image, Colors())
        cv2.imwrite(self.dst_path, image)
     