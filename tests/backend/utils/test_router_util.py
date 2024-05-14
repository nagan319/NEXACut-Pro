import os
import pytest
import tempfile
from unittest.mock import patch
from app.backend.utils.router_util import RouterUtil
from app.config import ROUTER_PREVIEW_DATA_PATH

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_get_new_router():
    router_data = []
    new_router = RouterUtil.get_new_router(router_data)
    assert new_router["id"] == 0
    assert new_router["preview_path"] == os.path.join(ROUTER_PREVIEW_DATA_PATH, "0.png")
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

def test__get_editable_keys():
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
    assert RouterUtil.editable_keys() == expected_keys

def test_value_ranges():
    expected_ranges = {
        "machineable_area_(x-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION),
        "machineable_area_(y-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION),
        "machineable_area_(z-axis)": (0, RouterUtil.ROUTER_MAX_DIMENSION),
        "max_plate_size_(x-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
        "max_plate_size_(y-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
        "max_plate_size_(z-axis)": (0, RouterUtil.PLATE_MAX_DIMENSION),
        "min_safe_distance_from_edge": (0, RouterUtil.ROUTER_MAX_DIMENSION // 2),
        "drill_bit_diameter": (0, RouterUtil.DRILL_BIT_MAX_DIAMETER),
        "mill_bit_diameter": (0, RouterUtil.MILL_BIT_MAX_DIAMETER)
    }
    assert RouterUtil.value_ranges() == expected_ranges

def test_get_next_router_id_empty_list():
    router_data = []
    assert RouterUtil._get_next_router_id(router_data) == 0

def test_get_next_router_id_non_empty_list():
    router_data = [{"id": 0}, {"id": 2}]
    assert RouterUtil._get_next_router_id(router_data) == 3

def test_get_preview_path():
    router_id = 0
    expected_path = os.path.join(ROUTER_PREVIEW_DATA_PATH, str(router_id)+'.png')
    assert RouterUtil.get_preview_path(router_id) == expected_path

def test_save_router_preview(temp_dir):
    router_data = {
        "id": 1,
        "preview_path": os.path.join(temp_dir, "1.png"),
        "machineable_area_(x-axis)": 100,
        "machineable_area_(y-axis)": 200,
        "max_plate_size_(x-axis)": 300,
        "max_plate_size_(y-axis)": 400,
        "min_safe_distance_from_edge": 10
    }
    RouterUtil.save_router_preview(router_data)
    assert os.path.exists(router_data["preview_path"])
