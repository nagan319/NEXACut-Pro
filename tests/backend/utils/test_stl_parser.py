import os
import numpy as np
import pytest
from app.backend.utils.stl_parser import STLParser

@pytest.fixture
def stl_file_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', 'test.stl')

@pytest.fixture
def stl_parser(stl_file_path):
    return STLParser(stl_file_path)

def test_init_valid_stl(stl_parser):
    assert stl_parser.is_valid_stl(stl_parser.stl_filepath)

def test_init_invalid_stl():
    with pytest.raises(FileNotFoundError):
        STLParser("invalid_file.stl")

def test_valid_axis():
    assert STLParser().is_valid_axis(0)
    assert STLParser().is_valid_axis(1)
    assert STLParser().is_valid_axis(2)

def test_invalid_axis():
    assert not STLParser().is_valid_axis(-1)
    assert not STLParser().is_valid_axis(3)

def test_stl_format_valid(stl_parser):
    assert stl_parser.is_stl_format_valid()

def test_stl_format_invalid():
    with pytest.raises(ValueError):
        STLParser("invalid_format.stl")

def test_determine_axis_to_flatten(stl_parser):
    assert stl_parser.is_valid_axis(stl_parser.flat_axis)

def test_get_thickness(stl_parser):
    assert isinstance(stl_parser.thickness, float)
    assert stl_parser.thickness > 0

def test_flatten_stl(stl_parser):
    flattened_mesh = stl_parser.flatten_stl()
    assert isinstance(flattened_mesh, np.ndarray)

def test_get_outer_edges(stl_parser):
    outer_edges = stl_parser.get_outer_edges()
    assert isinstance(outer_edges, list)
    assert all(isinstance(edge, tuple) for edge in outer_edges)

def test_get_contours(stl_parser):
    contours = stl_parser.get_contours()
    assert isinstance(contours, list)
    assert all(isinstance(contour, np.ndarray) for contour in contours)

def test_get_outermost_contour(stl_parser):
    outer_contour = stl_parser.get_outermost_contour()
    assert isinstance(outer_contour, np.ndarray)

def test_get_smooth_contour(stl_parser):
    contour = np.array([[0, 0], [5, 5], [10, 0]])
    smooth_contour = stl_parser.get_smooth_contour(contour)
    assert isinstance(smooth_contour, np.ndarray)

def test_get_bounding_box():
    contour = np.array([[0, 0], [5, 5], [10, 0]])
    min_x, max_x, min_y, max_y = STLParser().get_bounding_box(contour)
    assert min_x == 0
    assert max_x == 10
    assert min_y == 0
    assert max_y == 5

def test_save_preview_image(stl_parser, tmpdir):
    preview_path = os.path.join(tmpdir, "test_preview.png")
    stl_parser.save_preview_image(figsize=(3, 3), dpi=100, cad_preview_dst=tmpdir)
    assert os.path.exists(preview_path)

def test_save_preview_image_invalid_args(stl_parser):
    with pytest.raises(ValueError):
        stl_parser.save_preview_image(figsize=(3, 3), dpi=100)