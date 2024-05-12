import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from ..utils.style import apply_stylesheet
from ..utils.util_widgets.widget_template import WidgetTemplate
from ..utils.util_widgets.widget_viewer import WidgetViewer
from ..utils.file_widgets.router_file_widget import RouterFileWidget

from ...backend.utils.router_util import RouterUtil
from ...backend.utils.file_processor import FileProcessor

from ...config import ROUTER_PREVIEW_DATA_PATH

class RouterWidget(WidgetTemplate):

    def __init__(self, router_data: list, router_limit: int):
        super().__init__()

        self.router_util = RouterUtil(ROUTER_PREVIEW_DATA_PATH)
        self.router_data = router_data
        self.router_limit = router_limit

        self.__init_gui__()

    def __init_gui__(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        router_widgets = [RouterFileWidget(self.router_util, router) for router in self.router_data]

        for widget in router_widgets:
            widget.deleteRequested.connect(self.__on_router_delete_requested__)

        self.__file_preview_widget = WidgetViewer(1, 1, router_widgets) 

        self.__add_new_button_wrapper = QWidget()
        self.__add_new_button_wrapper_layout = QHBoxLayout()

        self.__add_new_button = QPushButton()
        apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.clicked.connect(self.add_new_router)

        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper_layout.addWidget(self.__add_new_button, 1)
        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper.setLayout(self.__add_new_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(self.__add_new_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Configure CNC Router", main_widget)
        self.update_add_button_text()

    def _get_router_amount(self) -> int:
        return len(self.router_data) 

    def add_new_router(self):
        if self._get_router_amount() >= self.router_limit:
            return
        
        new_router_data = self.router_util.get_new_router(self.router_data)
        self.router_data.append(new_router_data)
        
        self.router_util.save_router_preview(new_router_data)

        new_router_widget = RouterFileWidget(self.router_util, new_router_data)
        new_router_widget.deleteRequested.connect(self.__on_router_delete_requested__)

        self.__file_preview_widget.append_widgets([new_router_widget])
        self.update_add_button_text() 


    def update_add_button_text(self):
        if self._get_router_amount() >= self.router_limit:
            apply_stylesheet(self.__add_new_button, "generic-button-red.css")
        else:
            apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.setText(f"Add New ({self._get_router_amount()}/{self.router_limit})")

    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.router_data):
            if dict['filename'] == filename: 
                return idx
        return -1

    def __on_router_delete_requested__(self, filename: str):
        index = self._get_idx_of_filename(filename)

        filepath = os.path.join(ROUTER_PREVIEW_DATA_PATH, filename)
        file_processor = FileProcessor()
        file_processor.remove_file(filepath)

        self.router_data.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self.update_add_button_text()