import os
import tempfile
import json
import pytest
from unittest.mock import patch
from app.backend.utils.file_operations import FileProcessor

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def file_processor():
    return FileProcessor()

def test_get_json_data(file_processor, temp_dir):
    filepath = os.path.join(temp_dir, "test.json")
    data = {"key": "value"}
    with open(filepath, "w") as f:
        json.dump(data, f)
    assert file_processor.get_json_data(filepath) == data

def test_get_json_data_nonexistent_file(file_processor, temp_dir):
    filepath = os.path.join(temp_dir, "nonexistent.json")
    assert file_processor.get_json_data(filepath) is None

def test_get_json_data_invalid_extension(file_processor, temp_dir):
    filepath = os.path.join(temp_dir, "test.txt")
    with open(filepath, "w") as f:
        f.write("This is not a JSON file.")
    assert file_processor.get_json_data(filepath) is None

def test_save_json(file_processor, temp_dir):
    filepath = os.path.join(temp_dir, "test.json")
    data = {"key": "value"}
    file_processor.save_json(filepath, data)
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        assert json.load(f) == data

def test_get_all_json_in_folder(file_processor, temp_dir):
    data = [{"filename": "file1.json"}, {"filename": "file2.json"}]
    for item in data:
        filepath = os.path.join(temp_dir, item["filename"])
        with open(filepath, "w") as f:
            json.dump(item, f)
    assert file_processor.get_all_json_in_folder(temp_dir) == data

def test_save_all_json_to_folder(file_processor, temp_dir):
    data = [{"filename": "file1.json"}, {"filename": "file2.json"}]
    folder_path = temp_dir
    file_processor.save_all_json_to_folder(data, folder_path)
    for item in data:
        filepath = os.path.join(folder_path, item["filename"])
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            assert json.load(f) == item

def test_load_folder_contents(file_processor, temp_dir):
    filenames = ["file1.json", "file2.json"]
    for filename in filenames:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "w") as f:
            f.write("")
    assert set(file_processor.load_folder_contents(temp_dir)) == set(filenames)

def test_clear_folder_contents(file_processor, temp_dir):
    filenames = ["file1.json", "file2.json"]
    for filename in filenames:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "w") as f:
            f.write("")
    file_processor.clear_folder_contents(temp_dir)
    assert len(os.listdir(temp_dir)) == 0

def test_delete_file(file_processor, temp_dir):
    filepath = os.path.join(temp_dir, "test.json")
    with open(filepath, "w") as f:
        f.write("")
    file_processor.delete_file(filepath)
    assert not os.path.exists(filepath)

def test_copy_file(file_processor, temp_dir):
    src_path = os.path.join(temp_dir, "source.json")
    dst_path = os.path.join(temp_dir, "destination.json")
    with open(src_path, "w") as f:
        f.write("")
    file_processor.copy_file(src_path, dst_path)
    assert os.path.exists(dst_path)