from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QStackedWidget

from ..style import apply_stylesheet

from .image_load_widget import ImageLoadWidget
from .image_threshold_widget import ImageThresholdWidget
from .image_feature_widget import ImageFeatureWidget
from .image_flat_widget import ImageFlatWidget

from ....backend.utils.image_conversion.image_converter import ImageConverter

class ImageEditorWidget(QStackedWidget):

    editingFinished = pyqtSignal()

    def __init__(self, image_converter_instance: ImageConverter, pixmap_height: int):
        super().__init__()
        self.image_converter = image_converter_instance
        self.pixmap_height = pixmap_height
        self.__init_gui__()

    def __init_gui__(self):

        apply_stylesheet(self, 'light.css')

        self.setCurrentIndex(0)

        self.image_load_widget = ImageLoadWidget(self.image_converter)
        self.image_load_widget.imageImported.connect(self.on_image_imported)

        self.image_threshold_widget = ImageThresholdWidget(self.image_converter, self.pixmap_height)
        self.image_threshold_widget.binaryFinalized.connect(self.on_binary_finalized)

        self.image_feature_widget = ImageFeatureWidget(self.image_converter, self.pixmap_height)
        self.image_feature_widget.featuresFinalized.connect(self.on_features_finalized)

        self.image_flat_widget = ImageFlatWidget(self.image_converter, self.pixmap_height)
        self.image_flat_widget.saveImage.connect(self.on_image_saved)

        for widget in [
            self.image_load_widget, 
            self.image_threshold_widget,
            self.image_feature_widget,
            self.image_flat_widget]:
            self.addWidget(widget)

    def on_image_imported(self):
        self.setCurrentIndex(1)
        self.image_threshold_widget.update()
    
    def on_binary_finalized(self):
        self.setCurrentIndex(2)
        self.image_converter.initialize_features()
        self.image_converter.save_features()
        self.image_feature_widget.update()

    def on_features_finalized(self):
        self.setCurrentIndex(3)
        self.image_converter.save_flattened()
        self.image_flat_widget.update()

    def on_image_saved(self):
        self.editingFinished.emit()