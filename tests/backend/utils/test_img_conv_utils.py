import pytest
from app.backend.utils.image_conversion.utils import Colors, Size

@pytest.fixture
def default_colors():
    return {
        'background_color': (255, 255, 255),
        'contour_color': (0, 0, 0),
        'selected_element_color': (0, 0, 255),
        'plate_edge_color': (55, 55, 55),
        'corner_color': (255, 0, 0)
    }

@pytest.fixture
def custom_colors():
    return {
        'bg_col': (200, 200, 200),
        'ctr_col': (100, 100, 100),
        'select_elem_col': (50, 50, 50),
        'plate_col': (150, 150, 150),
        'corner_col': (0, 255, 0)
    }

def test_size_get_scaled():
    size = Size(5.0, 10.0)
    scaled_size = size.get_scaled(2.0)
    assert scaled_size.w == 10.0
    assert scaled_size.h == 20.0

def test_colors_default(default_colors):
    colors = Colors()
    assert colors.background_color == default_colors['background_color']
    assert colors.contour_color == default_colors['contour_color']
    assert colors.selected_element_color == default_colors['selected_element_color']
    assert colors.plate_color == default_colors['plate_edge_color']
    assert colors.corner_color == default_colors['corner_color']

def test_colors_custom(custom_colors):
    colors = Colors(**custom_colors)
    assert colors.background_color == custom_colors['bg_col']
    assert colors.contour_color == custom_colors['ctr_col']
    assert colors.selected_element_color == custom_colors['select_elem_col']
    assert colors.plate_color == custom_colors['plate_col']
    assert colors.corner_color == custom_colors['corner_col']