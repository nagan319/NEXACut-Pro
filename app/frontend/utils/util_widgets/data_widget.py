from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel

from ..style import Style
from ....backend.utils.input_parser import InputParser

class DataWidget(QWidget):

    deleteRequested = pyqtSignal() 
    saveRequested = pyqtSignal(dict) # data

    def __init__(self, data: dict, editable_keys: list, value_ranges: list, has_name_property: False, is_small: False):

        if len(value_ranges) != len(editable_keys):
            raise ValueError("Each editable key must have a corresponding value range")
        
        if has_name_property and 'name' not in data.keys():
            raise ValueError("Data must include name property")

        super().__init__()

        if is_small:
            self.button_stylesheet = 'small-button.css'
            self.text_stylesheet = 'small-text.css'
            self.key_val_ratio = (3, 2)
        else:
            self.button_stylesheet = 'generic-button.css'
            self.text_stylesheet = 'generic-text.css'
            self.key_val_ratio = (3, 1)

        self.data = data
        self.editable_keys = editable_keys
        self.value_ranges = value_ranges

        layout = QVBoxLayout()

        if has_name_property:
            name_widget = QLineEdit()
            name_widget.setText(self.data['name'])
            Style.apply_stylesheet(name_widget, "data-title-input-box.css")
            name_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_widget.editingFinished.connect(lambda box=name_widget: self.__on_name_edited__(box.text()))

            layout.addWidget(name_widget)

        for key in self.editable_keys:
            data_row_widget = self._get_data_row_widget(key, self.data[key])
            layout.addWidget(data_row_widget)
        
        button_container = QWidget()
        button_container_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        Style.apply_stylesheet(save_button, self.button_stylesheet)
        save_button.pressed.connect(self.__on_save_requested__)

        delete_button = QPushButton("Delete")
        Style.apply_stylesheet(delete_button, self.button_stylesheet)
        delete_button.pressed.connect(self.__on_delete_requested__)

        button_container_layout.addStretch(1)
        button_container_layout.addWidget(save_button, 2)
        button_container_layout.addWidget(delete_button, 2)
        button_container_layout.addStretch(1)

        button_container.setLayout(button_container_layout)

        layout.addWidget(button_container)
        self.setLayout(layout)

    def _get_data_row_widget(self, key: str, value: float) -> QWidget:

        data_row_widget = QWidget()
        data_row_layout = QHBoxLayout()

        key_label = QLabel()
        key_text = self._edit_key_text(key)
        key_label.setText(key_text)
        Style.apply_stylesheet(key_label, self.text_stylesheet)

        value_box = QLineEdit()
        value_box.setText(str(value))
        value_box.editingFinished.connect(lambda key=key, box=value_box: self.__on_value_edited__(box.text(), key, box))
        if type(self.value_ranges[key]) == tuple and self.value_ranges[key] is not None: 
            min_value, max_value = self.value_ranges[key]
            value_box.setPlaceholderText(f"{min_value}-{max_value}")
        else:
            value_box.setPlaceholderText(f"")
        Style.apply_stylesheet(value_box, "small-input-box.css")
  
        data_row_layout.addWidget(key_label, self.key_val_ratio[0])
        data_row_layout.addWidget(value_box, self.key_val_ratio[1])
        data_row_widget.setLayout(data_row_layout)

        return data_row_widget

    def _edit_key_text(self, str: str):
        words = str.split("_")
        for i, word in enumerate(words):
            words[i] = word.capitalize()     
        return " ".join(words)

    def __on_name_edited__(self, text: str):
        self.data['name'] = text

    def __on_value_edited__(self, string: str, key_edited: str, box: QLineEdit):
        
        if string == str(self.data[key_edited]):
            return
        
        if self.value_ranges[key_edited]:
            min, max = self.value_ranges[key_edited]
            value = InputParser.parse_text(string, min, max)
        else:
            value = InputParser.parse_text(string)

        if value is not None:
            box.setText(str(value))
            self.data[key_edited] = value

    def __on_save_requested__(self):
        self.saveRequested.emit(self.data)

    def __on_delete_requested__(self):
        self.deleteRequested.emit()