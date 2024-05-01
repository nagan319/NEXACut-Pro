import os
import numpy as np
import pytest
from app.backend.utils.image_conversion.utils import Size
from app.backend.utils.image_conversion.features import FeatDetector

@pytest.fixture
def valid_input():
    src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'plate images', 'image0bin.png')
    size = Size(1000, 1000)  
    return src_path, size

@pytest.mark.parametrize("invalid_src_path", ["pathpath.jpg", None, 123, 3.14, True, {}])
def test_invalid_src_path_type(invalid_src_path, valid_input):
    _, size = valid_input
    with pytest.raises((TypeError, FileNotFoundError)):
        FeatDetector(invalid_src_path, size)

@pytest.mark.parametrize("invalid_size", [None, "invalid", 3.14, (100, 100), [100, 100], Size(100, "invalid")])
def test_invalid_size(invalid_size, valid_input):
    src_path, _ = valid_input
    with pytest.raises((TypeError, ValueError)):
        FeatDetector(src_path, invalid_size)

def test_contours_extraction(valid_input):  

    detector = FeatDetector(*valid_input)

    features = detector.features

    assert features.plate_contour is not None
    assert isinstance(features.plate_contour, np.ndarray)
    assert isinstance(features.other_contours, list)