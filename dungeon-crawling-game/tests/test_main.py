import os
import shutil
import tempfile
import unittest

import main
from model.game import Room


def create_file(filedir, filename, content):
    filepath = os.path.join(filedir, filename)
    with open(filepath, 'w+') as file_handler:
        file_handler.write(content)
    return filepath


class TestParseConfigFile(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_parse_config_file_correct(self):
        file_content = "[FILE]\nfilepath = example.txt"
        filename = "temp_config.ini"
        config_file = create_file(self.temp_dir, filename, file_content)
        input_file = main.parse_config_file(config_file)
        self.assertEqual(input_file, "example.txt")

    def test_parse_config_file_without_section_headers(self):
        file_content = "filepath = example.txt"
        filename = "temp_config.ini"
        config_file = create_file(self.temp_dir, filename, file_content)
        input_file = main.parse_config_file(config_file)
        self.assertEqual(input_file, None)

    def test_parse_config_file_with_wrong_section_header(self):
        file_content = "[WRONG]\nfilepath = example.txt"
        filename = "temp_config.ini"
        config_file = create_file(self.temp_dir, filename, file_content)
        input_file = main.parse_config_file(config_file)
        self.assertEqual(input_file, None)

    def test_parse_config_file_with_wrong_filepath_field(self):
        file_content = "[FILE]\nwrong_field = example.txt"
        filename = "temp_config.ini"
        config_file = create_file(self.temp_dir, filename, file_content)
        input_file = main.parse_config_file(config_file)
        self.assertEqual(input_file, None)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)


class TestReadFromFile(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_read_rooms_from_file_correct(self):
        file_content = "a0 n:a1 \na1 s:a0"
        filename = "temp_map.txt"
        filepath = create_file(self.temp_dir, filename, file_content)
        rooms = main.read_rooms_from_file(filepath)
        self.assertSetEqual({"a0", "a1"}, set(rooms.keys()))
        self.assertDictEqual(rooms["a0"].doors, {"n": "a1"})
        self.assertDictEqual(rooms["a1"].doors, {"s": "a0"})

    def test_read_rooms_from_file_wrong_file_extension(self):
        file_content = "a0 n:a1 \na1 s:a0"
        filename = "temp_map.csv"
        filepath = create_file(self.temp_dir, filename, file_content)
        with self.assertRaises(ValueError):
            main.read_rooms_from_file(filepath)

    def test_read_rooms_from_file_no_file(self):
        filepath = "nonexistent_file.txt"
        with self.assertRaises(OSError):
            main.read_rooms_from_file(filepath)

    def test_read_rooms_from_file_invalid_content(self):
        file_content = "a0 n:a1 \na1 m:a0"
        filename = "temp_map.txt"
        filepath = create_file(self.temp_dir, filename, file_content)
        with self.assertRaises(ValueError):
            main.read_rooms_from_file(filepath)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)


class TestValidateRooms(unittest.TestCase):

    def test_validate_rooms_correct(self):
        rooms = {
            "a0": Room("a0", {
                "e": "a1", "s": "a3"
            }),
            "a1": Room("a1", {
                "s": "a2", "w": "a0"
            }),
            "a2": Room("a2", {
                "n": "a1", "w": "a3"
            }),
            "a3": Room("a3", {
                "e": "a2", "n": "a0"
            })
        }
        rooms_are_valid = main.validate_rooms(rooms)
        self.assertEqual(rooms_are_valid, True)

    def test_validate_rooms_wrong_name_length(self):
        rooms = {
            "a01": Room("a01", {"e": "a1"}),
            "a1": Room("a1", {"w": "a01"}),
        }
        rooms_are_valid = main.validate_rooms(rooms)
        self.assertEqual(rooms_are_valid, False)

    def test_validate_rooms_cannot_have_self_reference(self):
        rooms = {
            "a0": Room("a0", {
                "e": "a1", "w": "a0"
            }),
            "a1": Room("a1", {"w": "a0"}),
        }
        rooms_are_valid = main.validate_rooms(rooms)
        self.assertEqual(rooms_are_valid, False)

    def test_validate_rooms_wrong_door_directions(self):
        rooms = {
            "a0": Room("a0", {
                "m": "a1", "e": "a1"
            }),
            "a1": Room("a1", {"w": "a0"}),
        }
        rooms_are_valid = main.validate_rooms(rooms)
        self.assertEqual(rooms_are_valid, False)

    def test_validate_rooms_must_have_symmetric_references(self):
        rooms = {
            "a0": Room("a0", {"s": "a1"}),
            "a1": Room("a1", {"w": "a0"}),
        }
        rooms_are_valid = main.validate_rooms(rooms)
        self.assertEqual(rooms_are_valid, False)
