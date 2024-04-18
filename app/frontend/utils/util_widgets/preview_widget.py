import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap

class PreviewWidget(QLabel):

    def __init__(self, png_path: str):

        if not os.path.exists(png_path): 
            raise ValueError("Attempted to create preview widget with invalid file ")

        super().__init__()
        
        self.png_path = png_path
        self.pixmap = QPixmap(self.png_path)
        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update(self):
        self.pixmap = QPixmap(self.png_path)
        self.setPixmap(self.pixmap)