import os
import pytest
from controller import Controller

@pytest.fixture
def controller():
    return Controller()

def test_initialize_preferences(controller):
    controller.initialize_preferences()
    assert controller.units in ["metric", "imperial"]
    assert isinstance(controller.image_resolution, int)
    assert isinstance(controller.stock, str)
    assert isinstance(controller.router, str)

def test_revert_preferences(controller):
    controller.revert_preferences()
    assert controller.units in ["metric", "imperial"]
    assert isinstance(controller.image_resolution, int)
    assert isinstance(controller.stock, str)
    assert isinstance(controller.router, str)

# Add more tests for other methods in the Controller class

if __name__ == "__main__":
    pytest.main()