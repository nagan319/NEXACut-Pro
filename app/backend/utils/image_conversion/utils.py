class Size:
    """
    Class to represent dimensions with width and height.

    ### Parameters:
    - width
    - height
    """

    def __init__(self, width: float, height: float):
        self.w = width
        self.h = height

    def get_scaled(self, factor: float):
        """
        Gets a new Size object scaled by a given factor.

        - factor: The factor by which to scale the size.

        Returns:
        - A new Size object with scaled dimensions.
        """
        return Size(self.w * factor, self.h * factor)

class Colors:
    """
    A class to manage colors for different elements.

    ### Parameters (kwargs):
    - bg_col: Background color, defaults to (255, 255, 255).
    - ctr_col: Contour color, defaults to (0, 0, 0).
    - select_elem_col: Selected element color, defaults to (0, 0, 255).
    - plate_col: Plate edge color, defaults to (55, 55, 55).
    - corner_col: Corner color, defaults to (255, 0, 0).
    """

    DEFAULT_COLORS = {
    'background_color': (255, 255, 255),
    'contour_color': (0, 0, 0),
    'selected_element_color': (0, 0, 255),
    'plate_edge_color': (55, 55, 55),
    'corner_color': (255, 0, 0)
    }

    def __init__(self, **kwargs):
        self.background_color = kwargs.get('bg_col', self.DEFAULT_COLORS['background_color'])
        self.contour_color = kwargs.get('ctr_col', self.DEFAULT_COLORS['contour_color'])
        self.selected_element_color = kwargs.get('select_elem_col', self.DEFAULT_COLORS['selected_element_color'])
        self.plate_color = kwargs.get('plate_col', self.DEFAULT_COLORS['plate_edge_color'])
        self.corner_color = kwargs.get('corner_col', self.DEFAULT_COLORS['corner_color'])
        