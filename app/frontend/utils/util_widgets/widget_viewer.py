import math
from PyQt6.QtWidgets import QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout

from ..style import apply_stylesheet
from .arrow_button import ArrowButton

from ....config import MIN_HEIGHT

class WidgetViewer(QStackedWidget): # grid view

    MAX_WIDGETS_X = 4 
    MAX_WIDGETS_Y = 2

    def __init__(self, widgets_x: int, widgets_y: int, widgets: list = []): 

        if widgets_x > self.MAX_WIDGETS_X or widgets_x <= 0:
            raise ValueError(f"widgets_x must be in range 0-{self.MAX_WIDGETS_X}")
        if widgets_y > self.MAX_WIDGETS_Y or widgets_y <= 0:    
            raise ValueError(f"widgets_y must be in range 0-{self.MAX_WIDGETS_Y}")

        super().__init__()

        self.widgets_x = widgets_x
        self.widgets_y = widgets_y

        self.curr_tab = 0
        self.widgets = widgets 
        
        self.update_view()

    def update_view(self):

        for i in reversed(range(self.count())):
            widget = self.widget(i)
            self.removeWidget(widget)

        for i in range(self._get_max_tab_idx()+1):
            widget = self.get_tab(i)
            self.addWidget(widget)

        self.setCurrentIndex(self.curr_tab)

    def append_widgets(self, widgets: list): 
        for widget in widgets:
            self.widgets.append(widget)
        self.update_view()

    def pop_widget(self, widget_idx: int):
        if widget_idx >= 0 and widget_idx < len(self.widgets):
            try: 
                self.widgets.pop(widget_idx)
                self.update_view()
            except Exception: 
                return

    def _get_max_tab_idx(self):
        return 0 if len(self.widgets) == 0 else math.ceil(len(self.widgets) / (self.widgets_x * self.widgets_y)) - 1
    
    def prev_tab(self):
        if self.curr_tab > 0:
            self.curr_tab -= 1
        self.update_view()

    def next_tab(self):
        if self.curr_tab < self._get_max_tab_idx():
            self.curr_tab += 1
        self.update_view()

    def get_tab(self, tab_idx: int) -> QWidget:

        if tab_idx < 0 or tab_idx > self._get_max_tab_idx():
            return

        min_widget_idx = tab_idx * self.widgets_x * self.widgets_y
        all_slots_used_max_idx = (tab_idx+1) * self.widgets_x * self.widgets_y 
        max_widget_idx = all_slots_used_max_idx if all_slots_used_max_idx < len(self.widgets) else len(self.widgets) - 1

        main_widget = QWidget()
        main_layout = QHBoxLayout() 

        if tab_idx > 0:
            left_arrow = ArrowButton(False)
            left_arrow.pressed.connect(self.prev_tab)
            main_layout.addWidget(left_arrow, 1)
        else:
            main_layout.addStretch(1)

        view_widget = self._get_tab_central_widget(min_widget_idx, max_widget_idx)
        main_layout.addWidget(view_widget, 18)

        if tab_idx < self._get_max_tab_idx():
            right_arrow = ArrowButton(True)
            right_arrow.pressed.connect(self.next_tab)
            main_layout.addWidget(right_arrow, 1)
        else:
            main_layout.addStretch(1)

        main_widget.setLayout(main_layout)

        return main_widget

    def _get_tab_central_widget(self, min_widget_idx: int, max_widget_idx: int) -> QWidget:

        view_widget = QWidget()
        view_layout = QVBoxLayout()

        for i in range(self.widgets_y):

            row_widget = QWidget()
            row_widget.setMinimumHeight(int(MIN_HEIGHT*.8/self.widgets_y)) # get min height
            apply_stylesheet(row_widget, "light.css")
            row_widget_layout = QHBoxLayout()

            for j in range(self.widgets_x):

                curr_widget_idx = min_widget_idx + i*self.widgets_x + j

                if curr_widget_idx > max_widget_idx:
                    row_widget_layout.addStretch(1)

                else: # add widget from widgets list
                    curr_widget = self.widgets[curr_widget_idx]
                    row_widget_layout.addWidget(curr_widget, 1)
            
            row_widget.setLayout(row_widget_layout)
            view_layout.addWidget(row_widget, 1)
        
        view_widget.setLayout(view_layout)

        return view_widget