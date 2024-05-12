import pytest
from app.backend.utils.input_parser import InputParser

def test_parse_text_single_value():
    assert InputParser.parse_text("500") == 500

def test_parse_text_with_range_within_bounds():
    assert InputParser.parse_text("200", 300, 500) == 300

def test_parse_text_with_range_exceeding_upper_bound():
    assert InputParser.parse_text("600", 300, 500) == 500

def test_parse_text_feet_to_inches():
    assert InputParser.parse_text("2 feet") == 609.6
    assert InputParser.parse_text("2ft") == 609.6
    assert InputParser.parse_text("3 ft") == 914.4

def test_parse_text_inches_to_mm():
    assert InputParser.parse_text("166 in") == 4216.4

def test_parse_text_cm_to_mm():
    assert InputParser.parse_text("5500 cm") == 55000
    assert InputParser.parse_text("634cm") == 6340

def test_parse_text_invalid_input():
    assert InputParser.parse_text("garble") is None

def test_parse_text_mm():
    assert InputParser.parse_text("25 mm") == 25

