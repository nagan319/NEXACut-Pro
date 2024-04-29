import pytest
from app.backend.utils.input_parser import parse_text

def test_parse_text():
    assert(parse_text("500") == 500)
    assert(parse_text("200", 300, 500) == 300)
    assert(parse_text("600", 300, 500) == 500)
    assert(parse_text("2 feet") == 609.6)
    assert(parse_text("2ft") == 609.6)
    assert(parse_text("3 ft") == 914.4)
    assert(parse_text("166 in") == 4216.4)
    assert(parse_text("5500 cm") == 55000)
    assert(parse_text("634cm") == 6340)
    assert(parse_text("garble") == None)
