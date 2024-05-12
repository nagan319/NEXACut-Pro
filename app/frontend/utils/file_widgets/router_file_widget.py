from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout

from ..util_widgets.data_widget import DataWidget
from ...utils.util_widgets.preview_widget import PreviewWidget

from ....backend.utils.router_util import RouterUtil

class RouterFileWidget(QWidget): 
    
    deleteRequested = pyqtSignal(str) 

    def __init__(self, router_util: RouterUtil, router_data: dict): 

        super().__init__()

        self.router_util = router_util
        self.data = router_data 

        self._setup_ui()

    # ui initialization functions

    def _setup_ui(self):
        layout = QHBoxLayout()

        data_widget = DataWidget(self.data, self.router_util.editable_keys, self.router_util.value_ranges, True, False)
        data_widget.deleteRequested.connect(self.__on_delete_requested)
        data_widget.saveRequested.connect(self.__on_save_requested)

        self.preview_widget = PreviewWidget(self.data['preview_path'])

        layout.addWidget(data_widget, 5)
        layout.addWidget(self.preview_widget, 4)
        self.setLayout(layout)

    # runtime functions

    def _update_preview(self):
        self.router_util.save_router_preview(self.data)
        self.preview_widget.update()

    def __on_save_requested(self, data):
        self.data = data
        self._update_preview()

    def __on_delete_requested(self):
        self.deleteRequested.emit(self.data['filename'])