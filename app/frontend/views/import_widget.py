import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog

from ..utils.style import apply_stylesheet
from ..utils.util_widgets.widget_template import WidgetTemplate
from ..utils.util_widgets.widget_viewer import WidgetViewer
from ..utils.file_widgets.stl_file_widget import STLFileWidget

from ...backend.utils.stl_parser import STLParser
from ...backend.utils.file_operations import FileProcessor

from ...config import CAD_PREVIEW_DATA_PATH

class ImportWidget(WidgetTemplate):

    def __init__(self, imported_parts: list, part_import_limit: int):
        super().__init__()

        self.imported_parts = imported_parts
        self.part_import_limit = part_import_limit

        self.__init_gui__()
    
    def __init_gui__(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.__file_preview_widget = WidgetViewer(4, 2) 

        self.__import_button = QPushButton()
        self.__import_button.clicked.connect(self.import_files)
        apply_stylesheet(self.__import_button, "generic-button.css")

        import_button_wrapper = QWidget()
        import_button_wrapper_layout = QHBoxLayout()
        import_button_wrapper_layout.addStretch(2)
        import_button_wrapper_layout.addWidget(self.__import_button, 1)
        import_button_wrapper_layout.addStretch(2)
        import_button_wrapper.setLayout(import_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(import_button_wrapper, 1)
        main_widget.setLayout(main_layout)
        apply_stylesheet(main_widget, "light.css")

        self._update_import_button_text()

        self.__init_template_gui__("Import Part Files", main_widget)

    def _get_total_part_amount(self) -> int:
        total = 0
        for file in self.imported_parts:
            try:
                total += file['amount']
            except Exception:
                continue
        return total
    
    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.imported_parts):
            if dict['filename'] == filename: 
                return idx
        return -1
    
    def _save_file_to_data(self, filename: str, outer_contour: list, amount: int = 1):
        new_entry = {
            "filename": filename, 
            "amount": amount, 
            "outer_contour": outer_contour}
        self.imported_parts.append(new_entry)

    def import_files(self): 
        if self._get_total_part_amount() >= self.part_import_limit:
            return

        IMPORT_LIMIT = 10 
        
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select File", "", "STL Files (*.stl)")

        widgets = []

        imported = 0

        for path in file_paths:

            if imported >= IMPORT_LIMIT:
                break
            if self._get_total_part_amount() >= self.part_import_limit:
                break
                
            file_name = os.path.basename(path)

            duplicate = False

            for file in self.imported_parts:
                if file["filename"] == file_name:
                    duplicate = True

            if duplicate: 
                continue

            try:
                parser = STLParser(path, CAD_PREVIEW_DATA_PATH)
                parser.save_preview_image()
                outer_contour = parser.outer_contour
                png_location = parser.preview_path

                preview_widget = STLFileWidget(file_name, png_location)
                preview_widget.deleteRequested.connect(self.__on_widget_delete_request__)
                preview_widget.amountEdited.connect(self.__on_widget_amt_edited__)
                widgets.append(preview_widget)

                self._save_file_to_data(file_name, outer_contour, 1) 

            except Exception as e:
                continue

            imported += 1

        self.__file_preview_widget.append_widgets(widgets)
        self._update_import_button_text()

    def _update_import_button_text(self):
        if self._get_total_part_amount() >= self.part_import_limit:
            apply_stylesheet(self.__import_button, "generic-button-red.css")
        else:
            apply_stylesheet(self.__import_button, "generic-button.css")
        self.__import_button.setText(f"Import Parts ({self._get_total_part_amount()}/{self.part_import_limit})")

    def __on_widget_amt_edited__(self, filename: str, value: int): 
        index = self._get_idx_of_filename(filename)
        self.imported_parts[index]['amount'] = value
        self._update_import_button_text()

    def __on_widget_delete_request__(self, filename: str): 
        index = self._get_idx_of_filename(filename)

        filepath = os.path.join(CAD_PREVIEW_DATA_PATH, filename)
        file_processor = FileProcessor()
        file_processor.delete_file(filepath)

        self.imported_parts.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self._update_import_button_text()

