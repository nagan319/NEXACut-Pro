import os
import pytest
import tempfile
import numpy as np
from app.backend.utils.plate_util import PlateUtil
from app.config import PLATE_PREVIEW_DATA_PATH

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_get_new_plate():
    plate_data = []
    new_plate = PlateUtil.get_new_plate(plate_data)
    assert new_plate["id"] == 0
    assert new_plate["preview_path"] == os.path.join(PLATE_PREVIEW_DATA_PATH, "0.png")
    assert new_plate["width_(x)"] == PlateUtil.DEFAULT_X
    assert new_plate["height_(y)"] == PlateUtil.DEFAULT_Y
    assert new_plate["thickness_(z)"] == PlateUtil.DEFAULT_Z
    assert new_plate["material"] == PlateUtil.DEFAULT_MATERIAL
    assert new_plate["contours"] == None

def test__get_next_plate_id_empty_list():
    plate_data = []
    assert PlateUtil._get_next_plate_id(plate_data) == 0

def test__get_next_plate_id_non_empty_list():
    plate_data = [{"id": 0}, {"id": 2}]
    assert PlateUtil._get_next_plate_id(plate_data) == 3

def test_get_preview_path():
    plate_id = 0
    expected_path = os.path.join(PLATE_PREVIEW_DATA_PATH, str(plate_id)+'.png')
    assert PlateUtil.get_preview_path(plate_id) == expected_path

def test_save_plate_preview(temp_dir):
    plate_data = {
        "id": 1,
        "preview_path": os.path.join(temp_dir, "1.png"),
        "width_(x)": 100,
        "height_(y)": 200,
        "thickness_(z)": 10,
        "material": "Aluminum",
        "contours": None
    } 
    PlateUtil.save_preview_image(plate_data)
    assert os.path.exists(plate_data["preview_path"])