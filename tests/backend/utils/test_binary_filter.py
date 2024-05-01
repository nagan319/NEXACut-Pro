import os
import numpy as np
import cv2
import pytest
from app.backend.utils.image_conversion.filters import BinaryFilter

def test_binary_filter_invalid_threshold():

    with pytest.raises(ValueError):
        BinaryFilter("src_path.png", "dst_path.png", -1)

    with pytest.raises(ValueError):
        BinaryFilter("src_path.png", "dst_path.png", 256)

    with pytest.raises(TypeError):
        BinaryFilter("src_path.png", "dst_path.png", 128.5)

    with pytest.raises(TypeError):
        BinaryFilter("src_path.png", "dst_path.png", "invalid")

    with pytest.raises(TypeError):
        BinaryFilter("src_path.png", "dst_path.png", None)

@pytest.fixture
def src_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'plate images', 'image4.jpeg')

@pytest.fixture
def setup_binary_filter(src_path):
    src_path = src_path
    dst_path = "binary_filter_test.png"
    threshold = 127

    image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(src_path, image)

    yield src_path, dst_path, threshold

    os.remove(dst_path)

def test_binary_filter_save_image(setup_binary_filter):
    src_path, dst_path, threshold = setup_binary_filter

    binary_filter = BinaryFilter(src_path, dst_path, threshold)
    binary_filter.save_image()

    assert os.path.exists(dst_path)

    original_image = cv2.imread(src_path)
    saved_image = cv2.imread(dst_path)
    assert original_image.shape == saved_image.shape