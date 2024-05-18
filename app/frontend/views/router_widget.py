import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

import logging

from ..utils.style import Style
from ..utils.util_widgets.widget_template import WidgetTemplate
from ..utils.util_widgets.widget_viewer import WidgetViewer
from ..utils.file_widgets.router_file_widget import RouterFileWidget

from ...backend.utils.router_util import RouterUtil
from ...backend.utils.file_processor import FileProcessor

from ...config import ROUTER_PREVIEW_DATA_PATH

class RouterWidget(WidgetTemplate):
    """
    Tab for managing CNC routers.
    """
    def __init__(self, router_data: list, router_limit: int):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info(f"@{self.__class__.__name__}: Initializing router widget...")
        super().__init__()

        self.router_data = router_data
        self.router_limit = router_limit

        self._setup_ui()
        self.logger.info(f"@{self.__class__.__name__}: Initialization complete.")

    def _setup_ui(self):
        """
        Initialize widget ui.
        """
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        router_widgets = [RouterFileWidget(router) for router in self.router_data]

        for widget in router_widgets:
            widget.deleteRequested.connect(self.__on_router_delete_requested__)

        self._file_preview_widget = WidgetViewer(1, 1, router_widgets) 

        self.__add_new_button_wrapper = QWidget()
        self.__add_new_button_wrapper_layout = QHBoxLayout()

        self._add_new_button = QPushButton()
        Style.apply_stylesheet(self._add_new_button, "generic-button.css")
        self._add_new_button.clicked.connect(self.add_new_router)

        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper_layout.addWidget(self._add_new_button, 1)
        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper.setLayout(self.__add_new_button_wrapper_layout)

        main_layout.addWidget(self._file_preview_widget, 7)
        main_layout.addWidget(self.__add_new_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        Style.apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Configure CNC Router", main_widget)
        self.update_add_button_text()

    def _get_router_amount(self) -> int:
        """
        Get amount of routers in list.
        """
        return len(self.router_data) 

    def _get_router_list_idx(self, id: int) -> int:
        for i, router in enumerate(self.router_data):
            if router['id'] == id:
                return i
        return -1

    def add_new_router(self):
        """
        Add new router to list, create new widget.
        """
        if self._get_router_amount() >= self.router_limit:
            return
        
        self.logger.info(f"@{self.__class__.__name__}: Adding new router...")
        new_router_data = RouterUtil.get_new_router(self.router_data)
        self.router_data.append(new_router_data)
        
        RouterUtil.save_router_preview(new_router_data)

        self.logger.info(f"@{self.__class__.__name__}: Creating widget for new router...")
        new_router_widget = RouterFileWidget(new_router_data)
        new_router_widget.deleteRequested.connect(self.__on_router_delete_requested__)

        self._file_preview_widget.append_widgets([new_router_widget])
        self.update_add_button_text() 
        self.logger.info(f"@{self.__class__.__name__}: New router added successfully.")

    def update_add_button_text(self):
        """
        Update button based on amount of parts and whether or not the router limit is reached.
        """
        stylesheet = "generic-button-red.css" if self._get_router_amount() >= self.router_limit else "generic-button.css"
        Style.apply_stylesheet(self._add_new_button, stylesheet)
        self._add_new_button.setText(f"Add New ({self._get_router_amount()}/{self.router_limit})")

    def __on_router_delete_requested__(self, id: int):
        """
        Removes router from data, deleting preview path.
        """
        self.logger.info(f"@{self.__class__.__name__}: Removing router #{str(id)}.")
        filepath = os.path.join(ROUTER_PREVIEW_DATA_PATH, str(id)+'.png')
        FileProcessor.remove_file(filepath)

        router_list_idx = self._get_router_list_idx(id)
        self.router_data.pop(router_list_idx)
        self._file_preview_widget.pop_widget(router_list_idx)
        self.update_add_button_text()
        self.logger.info(f"@{self.__class__.__name__}: Router #{str(id)} removed successfully.")