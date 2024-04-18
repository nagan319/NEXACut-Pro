from PyQt6.QtWidgets import QStackedWidget

from style import Style

from image_load_widget import ImageLoadWidget
from image_threshold_widget import ImageThresholdWidget
from image_feature_widget import ImageFeatureWidget

from backend.utils.image_conversion.image_converter import ImageConverter

class ImageEditorWidget(QStackedWidget):

    def __init__(self, image_converter_instance: ImageConverter):
        super().__init__()
        self.image_converter = image_converter_instance
        self.__init_gui__()

    def __init_gui__(self):

        Style.apply_stylesheet(self, 'light.css')

        self.setCurrentIndex(0)

        params = (self.app, self.image_converter)

        self.image_load_widget = ImageLoadWidget(*params)
        self.image_load_widget.imageImported.connect(self.on_image_imported)

        self.image_threshold_widget = ImageThresholdWidget(*params)
        self.image_threshold_widget.binaryFinalized.connect(self.on_binary_finalized)

        self.image_feature_widget = ImageFeatureWidget(*params)
        self.image_feature_widget.featuresFinalized.connect(self.on_features_finalized)

        for widget in [
            self.image_load_widget, 
            self.image_threshold_widget,
            self.image_feature_widget]:
            self.addWidget(widget)

    def on_image_imported(self):
        self.setCurrentIndex(1)
        self.image_threshold_widget.update_preview()
    
    def on_binary_finalized(self):
        self.setCurrentIndex(2)
        self.image_converter.get_contours_from_binary()
        self.image_feature_widget.update_preview()

    def on_features_finalized(self):
        self.setCurrentIndex(3)