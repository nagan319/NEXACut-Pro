import pytest
import tempfile
import os
from app.backend.utils.plate_util import PlateUtil

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def plate_util_empty():
    return PlateUtil('')

@pytest.fixture
def plate_util_temp_dir(temp_dir):
    return PlateUtil(temp_dir)

def test__get_editable_keys(plate_util_empty):
    editable_keys = plate_util_empty._get_editable_keys()
    expected_keys = ["width_(x)", "height_(y)", "thickness_(z)", "material"]
    assert editable_keys == expected_keys

def test__get_value_ranges(plate_util_empty):
    value_ranges = plate_util_empty._get_value_ranges()
    expected_ranges = {
        "width_(x)": (0, plate_util_empty.MAX_DIMENSION),
        "height_(y)": (0, plate_util_empty.MAX_DIMENSION),
        "thickness_(z)": (0, plate_util_empty.MAX_DIMENSION),
        "material": None
    }
    assert value_ranges == expected_ranges

def test__get_next_plate_filename_empty(plate_util_empty):
    plate_data = []
    next_filename = plate_util_empty._get_next_plate_filename(plate_data)
    assert next_filename == "PLATE-0.json"

def test__get_next_plate_filename_nonempty(plate_util_empty):
    plate_data = [{"filename": "PLATE-1.json"}]
    next_filename = plate_util_empty._get_next_plate_filename(plate_data)
    assert next_filename == "PLATE-2.json"

def test_get_preview_path(plate_util_empty):
    plate_filename = "PLATE-1.json"
    preview_path = plate_util_empty.get_preview_path(plate_filename)
    expected_path = os.path.join(plate_util_empty.plate_preview_folder_path, "PLATE-1.png")
    assert preview_path == expected_path

def test_save_preview_image(plate_util_temp_dir):
    plate_data = {
        "filename": "PLATE-1.json",
        "preview_path": os.path.join(plate_util_temp_dir.plate_preview_folder_path, "PLATE-1.png"),
        "width_(x)": 100,
        "height_(y)": 100,
        "thickness_(z)": 10,
        "material": "Aluminum",
        "contours": None
    }
    plate_util_temp_dir.save_preview_image(plate_data)
    assert os.path.exists(plate_data["preview_path"])

def test__generate_rectangle_coordinates(plate_util_empty):
    width = 100
    height = 50
    x_coords, y_coords = plate_util_empty._generate_rectangle_coordinates(width, height)
    expected_x_coords = [0, 100, 100, 0, 0]
    expected_y_coords = [0, 0, 50, 50, 0]
    assert x_coords == expected_x_coords
    assert y_coords == expected_y_coords