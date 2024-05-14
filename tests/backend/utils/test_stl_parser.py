import os
import numpy as np
import pytest
import tempfile
from app.backend.utils.stl_parser import STLParser, Axis

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def stl_file_path_valid():
    parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'stl files')
    stl_file = os.path.abspath(os.path.join(parent_dir, 'RollerConnectorPlate.STL'))
    assert os.path.exists(stl_file), f"STL file {stl_file} does not exist"
    return stl_file

@pytest.fixture
def stl_file_path_invalid():
    parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'stl files')
    invalid_stl_file = os.path.abspath(os.path.join(parent_dir, 'invalid.STL'))
    assert os.path.exists(invalid_stl_file), f"Invalid STL file {invalid_stl_file} does not exist"
    return invalid_stl_file

@pytest.fixture
def stl_parser_valid(stl_file_path_valid, temp_dir):  # Modified fixture
    return STLParser(stl_file_path_valid, temp_dir)  # Pass temp_dir as cad_preview_dst

def test_stl_file_valid(stl_file_path_valid):
    assert STLParser.stl_file_valid(stl_file_path_valid) == True

def test_stl_mesh_valid(stl_parser_valid):
    assert STLParser.stl_mesh_valid(stl_parser_valid.stl_mesh_vector) == True

def test_get_flat_axis(stl_parser_valid):
    assert STLParser.get_flat_axis(stl_parser_valid.stl_mesh_vector) in [Axis.X, Axis.Y, Axis.Z]

def test_get_thickness(stl_parser_valid):
    flat_axis = STLParser.get_flat_axis(stl_parser_valid.stl_mesh_vector)
    assert isinstance(STLParser.get_thickness(stl_parser_valid.stl_mesh_vector, flat_axis), float)

def test_get_flattened_mesh(stl_parser_valid):
    flat_axis = STLParser.get_flat_axis(stl_parser_valid.stl_mesh_vector)
    assert isinstance(STLParser.get_flattened_mesh(stl_parser_valid.stl_mesh_vector, flat_axis), np.ndarray)

def test_get_outer_edges(stl_parser_valid):
    flat_axis = STLParser.get_flat_axis(stl_parser_valid.stl_mesh_vector)
    flattened_mesh = STLParser.get_flattened_mesh(stl_parser_valid.stl_mesh_vector, flat_axis)
    assert isinstance(STLParser.get_outer_edges(flattened_mesh, flat_axis), list)

def test_get_contours(stl_parser_valid):
    flat_axis = STLParser.get_flat_axis(stl_parser_valid.stl_mesh_vector)
    flattened_mesh = STLParser.get_flattened_mesh(stl_parser_valid.stl_mesh_vector, flat_axis)
    outer_edges = STLParser.get_outer_edges(flattened_mesh, flat_axis)
    assert isinstance(STLParser.get_contours(outer_edges), list)

def test_get_outermost_contour(stl_parser_valid):
    flat_axis = STLParser.get_flat_axis(stl_parser_valid.stl_mesh_vector)
    flattened_mesh = STLParser.get_flattened_mesh(stl_parser_valid.stl_mesh_vector, flat_axis)
    outer_edges = STLParser.get_outer_edges(flattened_mesh, flat_axis)
    contours = STLParser.get_contours(outer_edges)
    assert isinstance(STLParser.get_outermost_contour(contours), np.ndarray)

def test_get_smooth_contour(stl_parser_valid):
    flat_axis = STLParser.get_flat_axis(stl_parser_valid.stl_mesh_vector)
    flattened_mesh = STLParser.get_flattened_mesh(stl_parser_valid.stl_mesh_vector, flat_axis)
    outer_edges = STLParser.get_outer_edges(flattened_mesh, flat_axis)
    contours = STLParser.get_contours(outer_edges)
    outermost_contour = STLParser.get_outermost_contour(contours)
    assert isinstance(STLParser.get_smooth_contour(outermost_contour), np.ndarray)

def test_save_image(stl_parser_valid):
    stl_parser_valid.parse_stl()
    stl_parser_valid.save_image()
    assert os.path.exists(stl_parser_valid.dst_path)