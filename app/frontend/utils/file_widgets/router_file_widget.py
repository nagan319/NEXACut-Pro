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

        layout = QHBoxLayout()

        self.data_widget = DataWidget(self.data, self.router_util.editable_keys, self.router_util.value_ranges, True, False)
        self.data_widget.deleteRequested.connect(self.__on_delete_requested__)
        self.data_widget.saveRequested.connect(self.__on_save_requested__)

        self.preview_widget = PreviewWidget(self.data['preview_path'])

        layout.addWidget(self.data_widget, 5)
        layout.addWidget(self.preview_widget, 4)
        self.setLayout(layout)

    def _update_preview(self):
        self.router_util.save_router_preview(self.data)
        self.preview_widget.update()

    def __on_save_requested__(self, data):
        self.data = data
        self._update_preview()

    def __on_delete_requested__(self):
        self.deleteRequested.emit(self.data['filename'])