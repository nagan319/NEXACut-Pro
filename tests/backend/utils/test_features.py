import numpy as np
import pytest
from app.backend.utils.image_conversion.features import Features

def test_features_init_valid():
    plate_contour = np.array([[1, 2], [3, 4], [5, 6]])
    other_contours = [np.array([[7, 8], [9, 10], [11, 12]])]
    corners = [(13, 14), (15, 16)]
    selected_contour = 0
    selected_corner = 1

    features = Features(plate_contour, other_contours, corners, selected_contour, selected_corner)

    assert np.array_equal(features.plate_contour, plate_contour)
    assert features.other_contours == other_contours
    assert features.corners == corners
    assert features.selected_contour_idx == selected_contour
    assert features.selected_corner_idx == selected_corner
