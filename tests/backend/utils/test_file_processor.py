import os
import tempfile
import json
import csv
import pytest
from app.backend.utils.file_processor import FileProcessor

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_read_json(temp_dir):
    filepath = os.path.join(temp_dir, "test.json")
    data = {"key": "value"}
    with open(filepath, "w") as f:
        json.dump(data, f)
    assert FileProcessor.read_file(filepath) == data

def test_read_json_nonexistent_file(temp_dir):
    filepath = os.path.join(temp_dir, "nonexistent.json")
    assert FileProcessor.read_file(filepath) is None

def test_read_json_invalid_extension(temp_dir):
    filepath = os.path.join(temp_dir, "test.txt")
    with open(filepath, "w") as f:
        f.write("This is not a JSON file.")
    assert FileProcessor.read_file(filepath) is None

def test_write_json(temp_dir):
    filepath = os.path.join(temp_dir, "test.json")
    data = {"key": "value"}
    FileProcessor.write_file(filepath, data, format='json')
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        assert json.load(f) == data

def test_read_csv(temp_dir):
    filepath = os.path.join(temp_dir, "test.csv")
    data = [{"name": "Aleksandr", "age": "17"}, {"name": "Lucas", "age": "18"}]
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age"])
        writer.writeheader()
        writer.writerows(data)
    assert FileProcessor.read_file(filepath) == data

def test_read_csv_nonexistent_file(temp_dir):
    filepath = os.path.join(temp_dir, "nonexistent.csv")
    assert FileProcessor.read_file(filepath) is None

def test_read_csv_invalid_extension(temp_dir):
    filepath = os.path.join(temp_dir, "test.txt")
    with open(filepath, "w") as f:
        f.write("This is not a CSV file.")
    assert FileProcessor.read_file(filepath) is None

def test_write_csv(temp_dir):
    filepath = os.path.join(temp_dir, "test.csv")
    data = [{"name": "Aleksandr", "age": "17"}, {"name": "Lucas", "age": "18"}]
    FileProcessor.write_file(filepath, data)
    assert os.path.exists(filepath)
    with open(filepath, "r", newline="") as f:
        reader = csv.DictReader(f)
        assert list(reader) == data

def test_read_all_json_in_folder(temp_dir):
    data = [{"filename": "file1.json"}, {"filename": "file2.json"}]
    for item in data:
        filepath = os.path.join(temp_dir, item["filename"])
        with open(filepath, "w") as f:
            json.dump(item, f)
    assert FileProcessor.read_all_json_in_folder(temp_dir) == data

def test_write_multiple_json_to_folder(temp_dir):
    data = [{"filename": "file1.json"}, {"filename": "file2.json"}]
    folder_path = temp_dir
    FileProcessor.write_multiple_json_to_folder(data, folder_path)
    for item in data:
        filepath = os.path.join(folder_path, item["filename"])
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            assert json.load(f) == item

def test_get_all_filenames_in_folder(temp_dir):
    filenames = ["file1.json", "file2.json"]
    for filename in filenames:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "w") as f:
            f.write("")
    assert set(FileProcessor.get_all_filenames_in_folder(temp_dir)) == set(filenames)

def test_clear_folder_contents(temp_dir):
    filenames = ["file1.json", "file2.json"]
    for filename in filenames:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "w") as f:
            f.write("")
    FileProcessor.clear_folder_contents(temp_dir)
    assert len(os.listdir(temp_dir)) == 0

def test_remove_file(temp_dir):
    filepath = os.path.join(temp_dir, "test.json")
    with open(filepath, "w") as f:
        f.write("")
    FileProcessor.remove_file(filepath)
    assert not os.path.exists(filepath)

def test_copy_file(temp_dir):
    src_path = os.path.join(temp_dir, "source.json")
    dst_path = os.path.join(temp_dir, "destination.json")
    with open(src_path, "w") as f:
        f.write("")
    FileProcessor.copy_file(src_path, dst_path)
    assert os.path.exists(dst_path)
