class Size:

    def __init__(self, width: float, height: float):
        self.w = width
        self.h = height

    def get_scaled(self, factor: float):
        return Size(self.w * factor, self.h * factor)

class Colors:

    DEFAULT_COLORS = {
    'background_color': (255, 255, 255),
    'contour_color': (0, 0, 0),
    'selected_element_color': (0, 0, 255),
    'plate_edge_color': (0, 0, 0),
    'corner_color': (255, 0, 0)
    }

    def __init__(self, **kwargs):
        self.background_color = kwargs.get('bg_col', self.DEFAULT_COLORS['background_color'])
        self.contour_color = kwargs.get('ctr_col', self.DEFAULT_COLORS['contour_color'])
        self.selected_element_color = kwargs.get('select_elem_col', self.DEFAULT_COLORS['selected_element_color'])
        self.plate_color = kwargs.get('plate_col', self.DEFAULT_COLORS['plate_edge_color'])
        self.corner_color = kwargs.get('corner_col', self.DEFAULT_COLORS['corner_color'])
        