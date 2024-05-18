import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from typing import List, Dict

import logging

from ..utils.style import Style
from ..utils.util_widgets.widget_template import WidgetTemplate
from ..utils.util_widgets.widget_viewer import WidgetViewer
from ..utils.file_widgets.stl_file_widget import STLFileWidget

from ...backend.utils.stl_parser import STLParser
from ...backend.utils.file_processor import FileProcessor

from ...config import CAD_PREVIEW_DATA_PATH

class ImportWidget(WidgetTemplate):
    """
    Tab for handling imported CAD files. 

    ### Parameters:
    - imported_parts: List of imported CAD files.
    - part_import_limit: Limit on maximum number of parts able to be imported.
    """
    def __init__(self, imported_parts: List[dict], part_import_limit: int): # check format of imported parts
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info(f"@{self.__class__.__name__}: Initializing import widget...")
        super().__init__()

        self.imported_parts = imported_parts
        self.part_import_limit = part_import_limit

        self._setup_ui()
        self.logger.info(f"@{self.__class__.__name__}: Initialization complete.")
    
    def _setup_ui(self):
        """
        Initialize widget ui.
        """
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self._file_preview_widget = WidgetViewer(4, 2) 

        self._import_button = QPushButton()
        self._import_button.clicked.connect(self.import_files)
        Style.apply_stylesheet(self._import_button, "generic-button.css")

        import_button_wrapper = QWidget()
        import_button_wrapper_layout = QHBoxLayout()
        import_button_wrapper_layout.addStretch(2)
        import_button_wrapper_layout.addWidget(self._import_button, 1)
        import_button_wrapper_layout.addStretch(2)
        import_button_wrapper.setLayout(import_button_wrapper_layout)

        main_layout.addWidget(self._file_preview_widget, 7)
        main_layout.addWidget(import_button_wrapper, 1)
        main_widget.setLayout(main_layout)
        Style.apply_stylesheet(main_widget, "light.css")

        self._update_import_button_text()

        self.__init_template_gui__("Import Part Files", main_widget)

    def _get_total_part_amount(self) -> int:
        """
        Get total amount of imported parts. 
        """
        total = 0
        for file in self.imported_parts:
            try:
                total += file['amount']
            except Exception:
                continue
        return total
    
    def _get_idx_of_filename(self, filename: str) -> int:
        """
        Get index of certain file in imports list.
        """
        for idx, dict in enumerate(self.imported_parts):
            if dict['filename'] == filename: 
                return idx
        return -1
    
    def _save_file_to_data(self, filename: str, outer_contour: list, amount: int = 1):
        """
        Save widget info to list of imported parts.
        """
        new_entry = {
            "filename": filename, 
            "amount": amount, 
            "outer_contour": outer_contour}
        self.imported_parts.append(new_entry)

    def import_files(self): 
        """
        Add files from QFileDialog to import list, excluding duplicates and stopping when the import limit is reached.
        Note: Max number of files importable at once set to 10.
        """
        if self._get_total_part_amount() >= self.part_import_limit:
            return

        self.logger.info(f"@{self.__class__.__name__}: Importing files...")

        max_files_at_once: int = 10 
        
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select File", "", "STL Files (*.stl)")

        widgets = []

        imported: int = 0

        for path in file_paths:

            if imported >= max_files_at_once or self._get_total_part_amount() >= self.part_import_limit:
                break       

            duplicate = False

            filename = os.path.basename(path)

            for file in self.imported_parts:
                if file["filename"] == filename:
                    duplicate = True
                    break

            if duplicate: 
                continue

            try:
                self.logger.info(f"@{self.__class__.__name__}: Importing file {filename}...")
                parser = STLParser(path, CAD_PREVIEW_DATA_PATH)
                parser.parse_stl()
                parser.save_image()
                
                outer_contour = parser.outer_contour
                png_location = parser.dst_path

                self.logger.info(f"@{self.__class__.__name__}: Creating widget for file {filename}...")
                preview_widget = STLFileWidget(filename, png_location)
                preview_widget.deleteRequested.connect(self.__on_widget_delete_request__)
                preview_widget.amountEdited.connect(self.__on_widget_amt_edited__)
                widgets.append(preview_widget)

                self.logger.info(f"@{self.__class__.__name__}: Saving {filename} to data...")
                self._save_file_to_data(filename, outer_contour, 1) 

                self.logger.info(f"@{self.__class__.__name__}: File {filename} imported successfully.")

            except Exception as e:
                continue

            imported += 1

        self._file_preview_widget.append_widgets(widgets)
        self._update_import_button_text()

    def _update_import_button_text(self):
        """
        Update button based on amount of parts and whether or not the import limit is reached.
        """
        stylesheet = "generic-button-red.css" if self._get_total_part_amount() >= self.part_import_limit else "generic-button.css" 
        Style.apply_stylesheet(self._import_button, stylesheet)
        self._import_button.setText(f"Import Parts ({self._get_total_part_amount()}/{self.part_import_limit})")

    def __on_widget_amt_edited__(self, filename: str, value: int): 
        index = self._get_idx_of_filename(filename)
        self.imported_parts[index]['amount'] = value
        self._update_import_button_text()

    def __on_widget_delete_request__(self, filename: str): 
        """
        Logic for updating widget when a file is deleted from the preview list.
        """
        self.logger.info(f"@{self.__class__.__name__}: Removing file {filename}...")
        index = self._get_idx_of_filename(filename)

        filepath = os.path.join(CAD_PREVIEW_DATA_PATH, filename)
        file_processor = FileProcessor()
        file_processor.remove_file(filepath)

        self.imported_parts.pop(index)
        self._file_preview_widget.pop_widget(index)
        self.logger.info(f"@{self.__class__.__name__}: File {filename} removed successfully.")
        self._update_import_button_text()

