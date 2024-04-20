from PyQt6.QtCore import QPoint
from PyQt6.QtWidgets import QLabel

class InteractivePreview(QLabel):

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.relative_pos = None

    def mouseMoveEvent(self, event):
        label_size = self.size()
        pixmap_size = self.pixmap().size()

        if pixmap_size.height == 0:
            return
        
        image_pos = QPoint((label_size.width() - pixmap_size.width()) // 2,
                           (label_size.height() - pixmap_size.height()) // 2)
        mouse_pos = event.pos()
        self.relative_pos = mouse_pos - image_pos