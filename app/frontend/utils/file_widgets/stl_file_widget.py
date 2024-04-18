from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QPixmap

from utils.style import Style

class STLFileWidget(QWidget): 
    
    deleteRequested = pyqtSignal(str)
    amountEdited = pyqtSignal(str, int)

    def __init__(self, file_name: str, png_location: str):

        super().__init__()

        self.file_name = file_name
        self.png_location = png_location

        layout = QVBoxLayout()

        preview_widget = QLabel()
        preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_image = QPixmap(self.png_location)
        preview_widget.setPixmap(preview_image)

        bottom_widget = self._get_bottom_widget()

        layout.addWidget(preview_widget, 5)
        layout.addWidget(bottom_widget, 1)
        self.setLayout(layout)

    def _get_bottom_widget(self) -> QWidget:
        bottom_widget = QWidget()
        bottom_widget_layout = QHBoxLayout()

        amt_input = QLineEdit()
        amt_input.setPlaceholderText("Amount")
        Style.apply_stylesheet(amt_input, 'small-input-box.css')
        amt_input.textEdited.connect(self.on_amount_edited)
        amt_input.setText("1")

        delete_button = QPushButton("Delete")
        Style.apply_stylesheet(delete_button, 'small-button.css')
        delete_button.pressed.connect(self.on_delete_button_clicked) 

        bottom_widget_layout.addStretch(2)
        bottom_widget_layout.addWidget(amt_input, 1)
        bottom_widget_layout.addWidget(delete_button, 1)
        bottom_widget_layout.addStretch(2)
        bottom_widget.setLayout(bottom_widget_layout)
        return bottom_widget

    def on_delete_button_clicked(self):
        self.deleteRequested.emit(self.file_name)

    def on_amount_edited(self, new_text):
        try:
            new_amount = int(new_text)
            self.amountEdited.emit(self.file_name, new_amount) 
        except ValueError:
            pass

