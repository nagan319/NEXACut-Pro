import os
import numpy as np
import cv2
import traceback

from .utils import Size, Colors
from .filters import BinaryFilter, FlatFilter
from .features import FeatDetector, FeatDisplay, FeatEditor

class ImageConverter:

    MAX_IMG_W = 2000
    MAX_IMG_H = 2000

    RAW_NAME = 'raw.png'
    BIN_NAME = 'bin.png'
    FEAT_NAME = 'feat.png'
    FLAT_NAME = 'flat.png'

    OUTPUT_RES = 4 # pixels/mm

    def __init__(self, data_folder_path: str, plate_w: float, plate_h: float, pixmap_height: int):
        
        if not os.path.exists(data_folder_path):
            raise FileNotFoundError("Indicated preview folder path does not exist")
        
        if plate_w <= 0 or plate_h <= 0:
            raise ValueError("Invalid plate dimensions")

        self.data_folder = data_folder_path
        self.__init_paths__()

        self.plate_size = Size(plate_w, plate_h)
        self.pixmap_height = pixmap_height
    
    def __init_src_path__(self, path: str):
        self.src_img_path = path
        self._save_raw()

    def __init_paths__(self):
        self.raw_path = os.path.join(self.data_folder, self.RAW_NAME)
        self.bin_path = os.path.join(self.data_folder, self.BIN_NAME)
        self.feat_path = os.path.join(self.data_folder, self.FEAT_NAME)
        self.flat_path = os.path.join(self.data_folder, self.FLAT_NAME)

    def __init_resolution__(self, resolution: tuple):
        self.img_size = Size(resolution[1], resolution[0])

    def __init_features__(self):
        feat_detector = FeatDetector(self.bin_path, self.img_size)
        self.features = feat_detector.features

    def __resize_image(self, image, max_width: int, max_height: int): 
        initial_height, initial_width = image.shape[:2]
        scale_factor = min(max_width / initial_width, max_height / initial_height)

        new_width = round(initial_width * scale_factor)
        new_height = round(initial_height * scale_factor)
        
        new_dim = (new_width, new_height)
        resized_image = cv2.resize(image, new_dim, interpolation=cv2.INTER_LANCZOS4)

        return resized_image

    def _save_raw(self):
        image: np.ndarray = cv2.imread(self.src_img_path, cv2.IMREAD_COLOR)
        image = self.__resize_image(image, self.MAX_IMG_W, self.MAX_IMG_H)
        resolution = image.shape[:2]
        self.__init_resolution__(resolution)
        cv2.imwrite(self.raw_path, image)

    def save_binary(self, threshold: int):
        bin_filter = BinaryFilter(self.raw_path, self.bin_path, threshold)
        bin_filter.save_image()

    def initialize_features(self):
        self.__init_features__()
        self.feature_editor = FeatEditor(self.img_size, self.features, self.pixmap_height)

    def save_features(self):
        feature_display = FeatDisplay(self.feat_path, self.img_size, self.features, Colors())
        feature_display.save_features()
    
    def on_mouse_clicked(self, coordinates: tuple, add_mode: bool) -> bool:
        if add_mode:
            self.feature_editor.add_corner(coordinates)
            return True
        
        return self.feature_editor.on_mouse_clicked(coordinates)

    def _valid_features(self) -> bool:
        if len(self.features.corners) != 4:
            return False
        
        if self.features.plate_contour is None:
            return False
    
        return True

    def save_flattened(self) -> bool:
        if not self._valid_features():
            return False

        new_size = self.plate_size.get_scaled(self.OUTPUT_RES)
        flat_filter = FlatFilter(self.feat_path, self.flat_path, new_size, self.features.corners)
        flat_filter.save_image()

        return True