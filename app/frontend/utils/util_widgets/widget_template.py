from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel

from style import Style

class WidgetTemplate(QWidget): 

    MARGIN_WIDTH = 1
    WIDGET_WIDTH = 68

    def __init__(self):
        super().__init__()

    def __init_template_gui__(self, title_text: str, core_widget: QWidget): # called by child class after gui is configured

        self.__main_layout = QHBoxLayout()

        self.__content_widget = QWidget()
        self.__content_layout = QVBoxLayout()

        self.__title = QLabel(title_text)
        Style.apply_stylesheet(self.__title, "title.css")
        self.__title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__content_layout.addWidget(self.__title, 1)
        self.__content_layout.addWidget(core_widget, 9)
        self.__content_layout.addStretch(1)
        self.__content_widget.setLayout(self.__content_layout)

        self.__main_layout.addStretch(self.MARGIN_WIDTH)
        self.__main_layout.addWidget(self.__content_widget, self.WIDGET_WIDTH)
        self.__main_layout.addStretch(self.MARGIN_WIDTH)

        self.setLayout(self.__main_layout)
