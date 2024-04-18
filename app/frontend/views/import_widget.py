from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from frontend.utils.style import Style
from frontend.utils.widget_template import WidgetTemplate
from frontend.utils.widget_viewer import WidgetViewer

class ImportWidget(WidgetTemplate):

    def __init__(self):
        super().__init__()
        self.__init_gui__()
        self.__init_timeout__()
    
    def __init_gui__(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.__file_preview_widget = WidgetViewer(4, 2) 

        self.__import_button_wrapper = QWidget()
        self.__import_button_wrapper_layout = QHBoxLayout()

        self.__import_button = QPushButton()
        Style.apply_stylesheet(self.__import_button, "generic-button.css")
        self.__import_button.clicked.connect(self.import_files)
        self.update_import_button_text()

        self.__import_button_wrapper_layout.addStretch(2)
        self.__import_button_wrapper_layout.addWidget(self.__import_button, 1)
        self.__import_button_wrapper_layout.addStretch(2)
        self.__import_button_wrapper.setLayout(self.__import_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(self.__import_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        Style.apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Import Part Files", main_widget)

    def __init_timeout__(self):
        self.timeout = True

    def _get_total_part_amount(self) -> int:
        total = 0
        for file in self.app.imported_files:
            try:
                total += file['amount']
            except Exception:
                continue
        return total
    
    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.app.imported_files):
            if dict['filename'] == filename: 
                return idx
        return -1
    
    def _save_file_to_data(self, filename: str, outer_contour: list, amount: int = 1):
        new_entry = {
            "filename": filename, 
            "amount": amount, 
            "outer_contour": outer_contour}
        self.app.imported_files.append(new_entry)

    def import_files(self): 
        if self.timeout:
            return

        if self._get_total_part_amount() >= self.app.PART_IMPORT_LIMIT:
            return

        self.timeout = True

        IMPORT_LIMIT = 10 
        
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select File", "", "STL Files (*.stl)")

        widgets = []

        imported = 0

        for path in file_paths:

            if imported >= IMPORT_LIMIT:
                break
            if self._get_total_part_amount() >= self.app.PART_IMPORT_LIMIT:
                break
                
            file_name = os.path.basename(path)

            duplicate = False

            for file in self.app.imported_files:
                if file["filename"] == file_name:
                    duplicate = True

            if duplicate: 
                continue

            try:
                parser = STLParser(path, CAD_PREVIEW_DATA_PATH)
                parser.save_preview_image()
                outer_contour = parser.outer_contour
                png_location = parser.preview_path

                preview_widget = STLFileWidget(self.app, file_name, png_location)
                preview_widget.deleteRequested.connect(self.on_widget_delete_request)
                preview_widget.amountEdited.connect(self.on_widget_amt_edited)
                widgets.append(preview_widget)

                self._save_file_to_data(file_name, outer_contour, 1) 

            except Exception as e:
                continue

            imported += 1

        self.__file_preview_widget.append_widgets(widgets)
        self.update_import_button_text()

        self.timeout = False

    def update_import_button_text(self):
        if self._get_total_part_amount() >= self.app.PART_IMPORT_LIMIT:
            self.app.apply_stylesheet(self.__import_button, "generic-button-red.css")
        else:
            self.app.apply_stylesheet(self.__import_button, "generic-button.css")
        self.__import_button.setText(f"Import Parts ({self._get_total_part_amount()}/{self.app.PART_IMPORT_LIMIT})")

    def on_widget_amt_edited(self, filename: str, value: int): 
        index = self._get_idx_of_filename(filename)
        self.app.imported_files[index]['amount'] = value
        self.update_import_button_text()

    def on_widget_delete_request(self, filename: str):
        if self.timeout:
            return
        
        self.timeout = True
        index = self._get_idx_of_filename(filename)
        self.app.imported_files.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self.update_import_button_text()
        self.timeout = False
