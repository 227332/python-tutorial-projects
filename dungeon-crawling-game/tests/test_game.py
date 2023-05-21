import unittest

from model.game import Room, DungeonCrawlingGame, InvalidMoveException


class TestDungeonCrawlingGame(unittest.TestCase):

    def setUp(self):
        self.rooms = {
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

    def test_initialization_with_initial_room(self):
        game = DungeonCrawlingGame(self.rooms, self.rooms["a3"])
        self.assertDictEqual(game.rooms, self.rooms)
        self.assertEqual(game.current_room.name, "a3")
        self.assertEqual(game.avatar_current_room_location, "**")
        expected_room_coords = {(0, 0), (0, 1), (1, 1), (1, 0)}
        for room_coord in game.room_positions:
            self.assertIn(room_coord, expected_room_coords)
        expected_map_coords = {"x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1}
        for map_coord in expected_map_coords:
            self.assertEqual(getattr(game.map_coords, map_coord), expected_map_coords[map_coord])

    def test_initialization_without_initial_room(self):
        game = DungeonCrawlingGame(self.rooms)
        self.assertDictEqual(game.rooms, self.rooms)
        self.assertEqual(game.current_room.name, "a0")
        self.assertEqual(game.avatar_current_room_location, "**")
        expected_room_coords = {(0, 0), (1, 0), (1, -1), (0, -1)}
        for room_coord in game.room_positions:
            self.assertIn(room_coord, expected_room_coords)
        expected_map_coords = {"x_min": 0, "x_max": 1, "y_min": -1, "y_max": 0}
        for coord in expected_map_coords:
            self.assertEqual(getattr(game.map_coords, coord), expected_map_coords[coord])

    def test_make_move(self):
        game = DungeonCrawlingGame(self.rooms)
        game.make_move("e")
        self.assertEqual(game.current_room.name, "a1")
        with self.assertRaises(InvalidMoveException):
            game.make_move("n")

    def test_get_dungeon_map_with_current_room_location(self):
        game = DungeonCrawlingGame(self.rooms)
        dungeon_map = game.get_dungeon_map_with_current_room_location()
        expected_map = "**-a1\n|  | \na3-a2"
        self.assertEqual(dungeon_map, expected_map)
