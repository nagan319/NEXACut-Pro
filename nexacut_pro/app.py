import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

# from constants.gui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXACut Pro")
        self.setMinimumSize(1600, 900)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0) # outside
        main_layout.setSpacing(0)

        left_layout = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: rgb(30, 30, 30);") 
        left_layout.addWidget(QLabel("Logo"))
        left_widget.setLayout(left_layout)

        main_layout.addWidget(left_widget, 20)

        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: rgb(45, 45, 45);")

        logo_label = QLabel()
        logo_path = os.path.join('graphics', 'NEXACut Logo.png')
        pixmap = QPixmap(logo_path)
        print(pixmap.width())
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(logo_label)
        right_widget.setLayout(right_layout)    

        main_layout.addWidget(right_widget, 80)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())