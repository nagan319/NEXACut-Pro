import os
import numpy as np
import pytest
import tempfile
from app.backend.utils.stl_parser import STLParser

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def stl_file_path_valid():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'stl files', 'RollerConnectorPlate.STL')

@pytest.fixture
def stl_file_path_invalid():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'stl files', 'invalid.STL')

@pytest.fixture
def stl_parser_valid(stl_file_path_valid, temp_dir):
    return STLParser(stl_file_path_valid, temp_dir)

@pytest.fixture
def stl_parser_invalid(stl_file_path_invalid):
    return STLParser(stl_file_path_invalid)

def test_init_valid_stl(stl_parser_valid):
    assert stl_parser_valid.is_valid_stl(stl_parser_valid.stl_filepath)

def test_init_invalid_stl():
    with pytest.raises(FileNotFoundError):
        STLParser("invalid random file path")

def test_valid_axis(stl_parser_valid):
    assert stl_parser_valid.is_valid_axis(0)
    assert stl_parser_valid.is_valid_axis(1)
    assert stl_parser_valid.is_valid_axis(2)

def test_invalid_axis(stl_parser_valid):
    assert not stl_parser_valid.is_valid_axis(-1)
    assert not stl_parser_valid.is_valid_axis(3)

def test_stl_format_valid(stl_parser_valid):
    assert stl_parser_valid.is_stl_format_valid()

def test_stl_format_invalid(stl_file_path_invalid):
    with pytest.raises(ValueError):
        STLParser(stl_file_path_invalid)

def test_determine_axis_to_flatten(stl_parser_valid):
    assert stl_parser_valid.is_valid_axis(stl_parser_valid.flat_axis)

def test_get_thickness(stl_parser_valid):
    assert stl_parser_valid.thickness > 0

def test_flatten_stl(stl_parser_valid):
    flattened_mesh = stl_parser_valid.flatten_stl()
    assert isinstance(flattened_mesh, np.ndarray)

def test_get_outer_edges(stl_parser_valid):
    outer_edges = stl_parser_valid.get_outer_edges()
    assert isinstance(outer_edges, list)
    assert all(isinstance(edge, tuple) for edge in outer_edges)

def test_get_contours(stl_parser_valid):
    contours = stl_parser_valid.get_contours()
    assert isinstance(contours, list)
    assert all(isinstance(contour, np.ndarray) for contour in contours)

def test_get_outermost_contour(stl_parser_valid):
    outer_contour = stl_parser_valid.get_outermost_contour()
    assert isinstance(outer_contour, np.ndarray)

def test_get_smooth_contour(stl_parser_valid):
    contour = np.array([[0, 0], [5, 5], [10, 0]])
    smooth_contour = stl_parser_valid.get_smooth_contour(contour)
    assert isinstance(smooth_contour, np.ndarray)

def test_get_bounding_box(stl_parser_valid):
    contour = np.array([[0, 0], [5, 5], [10, 0]])
    min_x, max_x, min_y, max_y = stl_parser_valid.get_bounding_box(contour)
    assert min_x == 0
    assert max_x == 10
    assert min_y == 0
    assert max_y == 5

def test_save_preview_image(stl_parser_valid, temp_dir):
    preview_path = temp_dir
    stl_parser_valid.save_preview_image(figsize=(3, 3), dpi=100)
    assert os.path.exists(preview_path)
