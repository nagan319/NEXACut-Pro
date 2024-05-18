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

def test_contours_extraction(valid_input):  

    detector = FeatDetector(*valid_input)

    features = detector.features

    assert features.plate_contour is not None
    assert isinstance(features.plate_contour, np.ndarray)
    assert isinstance(features.other_contours, list)