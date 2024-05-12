import os
import numpy as np
import pytest
import tempfile
from ....app.backend.utils.stl_parser import STLParser, Axis

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def stl_file_path_valid():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'stl files', 'RollerConnectorPlate.STL')

@pytest.fixture
def stl_file_path_invalid():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'stl files', 'invalid.STL')

@pytest.fixture
def stl_parser_valid(stl_file_path_valid, temp_dir):
    return STLParser(stl_file_path_valid, temp_dir)

@pytest.fixture
def stl_parser_invalid(stl_file_path_invalid):
    return STLParser(stl_file_path_invalid)

def test_init_valid_stl(stl_parser_valid):
    assert isinstance(stl_parser_valid.stl_mesh, np.ndarray)
    assert stl_parser_valid.flat_axis in Axis
    assert isinstance(stl_parser_valid.thickness, float)
    assert isinstance(stl_parser_valid.flattened_mesh, np.ndarray)
    assert isinstance(stl_parser_valid.outer_edges, list)

def test_init_invalid_stl():
    with pytest.raises(FileNotFoundError):
        STLParser("invalid random file path")

def test_valid_axis(stl_parser_valid):
    assert stl_parser_valid.axis_valid(stl_parser_valid.flat_axis)

def test_invalid_axis(stl_parser_valid):
    assert not stl_parser_valid.axis_valid(Axis.X) 

def test_stl_format_valid(stl_parser_valid):
    assert STLParser.stl_file_valid(stl_parser_valid.stl_filepath)

def test_stl_format_invalid(stl_file_path_invalid):
    assert not STLParser.stl_file_valid(stl_file_path_invalid)

def test_get_thickness(stl_parser_valid):
    assert stl_parser_valid.get_thickness(stl_parser_valid.stl_mesh_vector, stl_parser_valid.flat_axis) > 0

def test_flatten_stl(stl_parser_valid):
    flattened_mesh = stl_parser_valid.get_flattened_mesh(stl_parser_valid.stl_mesh_vector, stl_parser_valid.flat_axis)
    assert isinstance(flattened_mesh, np.ndarray)

def test_get_outer_edges(stl_parser_valid):
    outer_edges = stl_parser_valid.get_outer_edges(stl_parser_valid.flattened_mesh, stl_parser_valid.flat_axis)
    assert isinstance(outer_edges, list)
    assert all(isinstance(edge, tuple) for edge in outer_edges)

def test_get_contours(stl_parser_valid):
    contours = stl_parser_valid.get_contours(stl_parser_valid.outer_edges)
    assert isinstance(contours, list)
    assert all(isinstance(contour, np.ndarray) for contour in contours)

def test_get_outermost_contour(stl_parser_valid):
    outer_contour = stl_parser_valid.get_outermost_contour(stl_parser_valid.contours)
    assert isinstance(outer_contour, np.ndarray)

def test_get_smooth_contour(stl_parser_valid):
    contour = np.array([[0, 0], [5, 5], [10, 0]])
    smooth_contour = STLParser.get_smooth_contour(contour)
    assert isinstance(smooth_contour, np.ndarray)

def test_save_preview_image(stl_parser_valid, temp_dir):
    preview_path = os.path.join(temp_dir, 'preview.png')
    stl_parser_valid.save_preview_image(figsize=(3, 3), dpi=100)
    assert os.path.exists(preview_path)
