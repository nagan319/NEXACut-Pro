import pytest
import math
from app.backend.utils.image_conversion.features import FeatEditor, Size, Features

# fix these tests

@pytest.fixture
def mock_size():
    return Size(1000, 1000)

@pytest.fixture
def mock_features():
    return Features()

@pytest.fixture
def feat_editor(mock_size, mock_features):
    return FeatEditor(mock_size, mock_features, 200)

def test_select_corner(feat_editor):
    feat_editor.select_corner(1)
    assert feat_editor.features.selected_corner_idx == 1

def test_unselect_corner(feat_editor):
    feat_editor.unselect_corner()
    assert feat_editor.features.selected_corner_idx is None

def test_select_contour(feat_editor):
    feat_editor.select_contour(2)
    assert feat_editor.features.selected_contour_idx == 2

def test_unselect_contour(feat_editor):
    feat_editor.unselect_contour()
    assert feat_editor.features.selected_contour_idx is None

def test_remove_corner(feat_editor):
    feat_editor.features.corners = [(10, 20), (30, 40)]
    feat_editor.select_corner(0)
    feat_editor.remove_corner()
    assert feat_editor.features.corners == [(30, 40)]
    assert feat_editor.features.selected_corner_idx is None

def test_remove_contour(feat_editor):
    feat_editor.features.other_contours = [[(10, 20)], [(30, 40)]]
    feat_editor.select_contour(0)
    feat_editor.remove_contour()
    assert feat_editor.features.other_contours == [[(30, 40)]]
    assert feat_editor.features.selected_contour_idx is None

def test_add_corner(feat_editor):
    feat_editor.features.corners = []
    feat_editor.add_corner((50, 60))
    assert feat_editor.features.corners == [(int(50/feat_editor.pixmap_scale_factor), int(60/feat_editor.pixmap_scale_factor))]