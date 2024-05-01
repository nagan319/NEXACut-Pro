import pytest
from app.backend.utils.image_conversion.utils import Size, Colors
from app.backend.utils.image_conversion.filters import FlatFilter

@pytest.fixture
def valid_input():
    src_path = "valid_src_path.png"
    dst_path = "valid_dst_path.png"
    size = Size(100, 100)  
    corners = [(0, 0), (100, 0), (100, 100), (0, 100)]  #
    return src_path, dst_path, size, corners

@pytest.mark.parametrize("invalid_src_path", [None, 123, True, Size(100, 100)])
def test_invalid_src_path(valid_input, invalid_src_path):
    src_path, dst_path, size, corners = valid_input
    with pytest.raises(TypeError):
        FlatFilter(invalid_src_path, dst_path, size, corners)

@pytest.mark.parametrize("invalid_dst_path", [None, 123, True, Size(100, 100)])
def test_invalid_dst_path(valid_input, invalid_dst_path):
    src_path, dst_path, size, corners = valid_input
    with pytest.raises(TypeError):
        FlatFilter(src_path, invalid_dst_path, size, corners)

@pytest.mark.parametrize("invalid_size", [None, "invalid", True, [(100, 100)]])
def test_invalid_size(valid_input, invalid_size):
    src_path, dst_path, _, corners = valid_input
    with pytest.raises(TypeError):
        FlatFilter(src_path, dst_path, invalid_size, corners)

@pytest.mark.parametrize("invalid_size", [1.5, 3.14, -42.0])
def test_invalid_size_float(valid_input, invalid_size):
    src_path, dst_path, _, corners = valid_input
    with pytest.raises(TypeError):
        FlatFilter(src_path, dst_path, invalid_size, corners)

@pytest.mark.parametrize("invalid_corners", [None, "invalid", True, Size(100, 100)])
def test_invalid_corners(valid_input, invalid_corners):
    src_path, dst_path, size, _ = valid_input
    with pytest.raises(TypeError):
        FlatFilter(src_path, dst_path, size, invalid_corners)
