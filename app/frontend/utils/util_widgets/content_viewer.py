from PyQt6.QtWidgets import QStackedWidget

from frontend.utils.style import Style

class ContentViewer(QStackedWidget):

    def __init__(self, widgets: list):
        super().__init__()

        self.amt_widgets = len(widgets)

        Style.apply_stylesheet(self, "light.css")

        for widget in widgets:
            self.addWidget(widget)

        self.setCurrentIndex(0)

    def set_view(self, index: int):
        if 0 <= index < len(self.amt_widgets):
            self.setCurrentIndex(index)