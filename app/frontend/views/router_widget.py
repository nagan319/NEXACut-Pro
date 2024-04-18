from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from frontend.utils.style import Style
from frontend.utils.widget_template import WidgetTemplate
from frontend.utils.widget_viewer import WidgetViewer
from frontend.file_widgets.router_file_widget import RouterFileWidget

from backend.utils.router_util import RouterUtil


class RouterWidget(WidgetTemplate):

    def __init__(self):
        super().__init__()

        self.router_util = RouterUtil(ROUTER_PREVIEW_DATA_PATH)

        self.__init_gui__()
        self.__init_timeout__()

    def __init_gui__(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        router_widgets = [RouterFileWidget(self.app, self.router_util, router) for router in self.app.router_data]

        for widget in router_widgets:
            widget.deleteRequested.connect(self.on_router_delete_requested)

        self.__file_preview_widget = WidgetViewer(self.app, 1, 1, router_widgets) 

        self.__add_new_button_wrapper = QWidget()
        self.__add_new_button_wrapper_layout = QHBoxLayout()

        self.__add_new_button = QPushButton()
        self.app.apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.clicked.connect(self.add_new_router)

        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper_layout.addWidget(self.__add_new_button, 1)
        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper.setLayout(self.__add_new_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(self.__add_new_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        self.app.apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Configure CNC Router", main_widget)
        self.update_add_button_text()

    def __init_timeout__(self):
        self.timeout = False

    def _get_router_amount(self) -> int:
        return len(self.app.router_data) 

    def add_new_router(self):
        if self.timeout:
            return

        self.timeout = True
        if self._get_router_amount() < self.app.ROUTER_LIMIT:
            new_router_data = self.router_util.get_new_router(self.app.router_data)
            self.app.router_data.append(new_router_data)
            
            self.router_util.save_router_preview(new_router_data)

            new_router_widget = RouterFileWidget(self.app, self.router_util, new_router_data)
            new_router_widget.deleteRequested.connect(self.on_router_delete_requested)

            self.__file_preview_widget.append_widgets([new_router_widget])
            self.update_add_button_text() 
        self.timeout = False

    def update_add_button_text(self):
        if self._get_router_amount() >= self.app.ROUTER_LIMIT:
            self.app.apply_stylesheet(self.__add_new_button, "generic-button-red.css")
        else:
            self.app.apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.setText(f"Add New ({self._get_router_amount()}/{self.app.ROUTER_LIMIT})")

    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.app.router_data):
            if dict['filename'] == filename: 
                return idx
        return -1

    def on_router_delete_requested(self, filename: str):
        if self.timeout:
            return
    
        self.timeout = True
        index = self._get_idx_of_filename(filename)
        self.app.file_processor.delete_file(self.app.router_data[index]['preview_path'])
        self.app.router_data.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self.update_add_button_text()
        self.timeout = False