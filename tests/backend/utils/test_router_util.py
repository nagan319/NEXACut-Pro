import os
import pytest
import tempfile
from unittest.mock import patch
from app.backend.utils.router_util import RouterUtil

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def router_util_no_path():
    return RouterUtil('')

@pytest.fixture
def router_util_temp_dir(temp_dir):
    return RouterUtil(temp_dir)

def test_get_new_router(router_util_no_path):
    router_data = []
    new_router = router_util_no_path.get_new_router(router_data)
    assert new_router["filename"] == "ROUTER-0.json"
    assert new_router["preview_path"] == os.path.join(router_util_no_path.router_preview_folder_path, "ROUTER-0.png")
    assert new_router["name"] == RouterUtil.ROUTER_DEFAULT_NAME
    assert new_router["machineable_area_(x-axis)"] == RouterUtil.ROUTER_DEFAULT_X
    assert new_router["machineable_area_(y-axis)"] == RouterUtil.ROUTER_DEFAULT_Y
    assert new_router["machineable_area_(z-axis)"] == RouterUtil.ROUTER_DEFAULT_Z
    assert new_router["max_plate_size_(x-axis)"] == RouterUtil.PLATE_DEFAULT_X
    assert new_router["max_plate_size_(y-axis)"] == RouterUtil.PLATE_DEFAULT_Y
    assert new_router["max_plate_size_(z-axis)"] == RouterUtil.PLATE_DEFAULT_Z
    assert new_router["min_safe_distance_from_edge"] == RouterUtil.DEFAULT_SAFE_DISTANCE
    assert new_router["drill_bit_diameter"] == RouterUtil.DEFAULT_DRILL_BIT_DIAMETER
    assert new_router["mill_bit_diameter"] == RouterUtil.DEFAULT_MILL_BIT_DIAMETER

def test__get_editable_keys(router_util_no_path):
    expected_keys = [
        "machineable_area_(x-axis)",
        "machineable_area_(y-axis)",
        "machineable_area_(z-axis)",
        "max_plate_size_(x-axis)",
        "max_plate_size_(y-axis)",
        "max_plate_size_(z-axis)",
        "min_safe_distance_from_edge",
        "drill_bit_diameter",
        "mill_bit_diameter"
    ]
    assert router_util_no_path._get_editable_keys() == expected_keys

def test__load_value_ranges(router_util_no_path):
    expected_ranges = {
        "machineable_area_(x-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION), 
        "machineable_area_(y-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION), 
        "machineable_area_(z-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION), 
        "max_plate_size_(x-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
        "max_plate_size_(y-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
        "max_plate_size_(z-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
        "min_safe_distance_from_edge": (0, RouterUtil.ROUTER_MAX_DIMENSION//2),
        "drill_bit_diameter": (0, RouterUtil.DRILL_BIT_MAX_DIAMETER),
        "mill_bit_diameter": (0, RouterUtil.MILL_BIT_MAX_DIAMETER)
    }
    assert router_util_no_path._load_value_ranges() == expected_ranges

def test_get_next_router_filename_empty_list(router_util_no_path):
    router_data = []
    assert router_util_no_path._get_next_router_filename(router_data) == "ROUTER-0.json"

def test_get_next_router_filename_non_empty_list(router_util_no_path):
    router_data = [{"filename": "ROUTER-0.json"}, {"filename": "ROUTER-2.json"}]
    assert router_util_no_path._get_next_router_filename(router_data) == "ROUTER-1.json"

def test_get_preview_path(temp_dir, router_util_temp_dir):
    router_filename = "ROUTER-0.json"
    expected_path = os.path.join(temp_dir, "ROUTER-0.png")
    assert router_util_temp_dir.get_preview_path(router_filename) == expected_path

def test_save_router_preview(router_util_temp_dir):
    router_data = {
        "filename": "ROUTER-1.json",
        "preview_path": os.path.join(router_util_temp_dir.router_preview_folder_path, "ROUTER-1.png"),
        "machineable_area_(x-axis)": 100,
        "machineable_area_(y-axis)": 200,
        "max_plate_size_(x-axis)": 300,
        "max_plate_size_(y-axis)": 400,
        "min_safe_distance_from_edge": 10
    }
    router_util_temp_dir.save_router_preview(router_data)
    assert os.path.exists(router_data["preview_path"])
