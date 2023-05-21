from typing import NamedTuple


class DungeonMapCoordinates(NamedTuple):
    x_min: int
    x_max: int
    y_min: int
    y_max: int


class Room:
    """Representation of a dungeon room."""

    def __init__(self, name: str, doors: dict[str, str] = {}) -> None:
        self._name = name
        self._doors = doors

    @property
    def name(self) -> str:
        return self._name

    @property
    def doors(self) -> dict[str, str]:
        return self._doors


class InvalidMoveException(Exception):
    """Exception raised when an invalid move is made."""


class DungeonCrawlingGame:
    """Representation of the Dungeon Crawling Game."""

    def __init__(self, rooms: dict[str, Room], initial_room: Room = None) -> None:
        self._rooms = rooms
        self._current_room = initial_room if initial_room is not None else next(iter(rooms.values()))
        self._room_positions = self._compute_rooms_coordinates(
            initial_room=self._current_room, coordinates_initial_room=(0, 0)
        )
        self._map_coords = self._compute_dungeon_map_coordinates()
        self._avatar_current_room_location = "*" * len(self._current_room.name)

    @property
    def rooms(self) -> dict[str, Room]:
        return self._rooms

    @property
    def current_room(self) -> Room:
        return self._current_room

    @property
    def room_positions(self) -> dict[tuple[int, int], str]:
        return self._room_positions

    @property
    def map_coords(self) -> DungeonMapCoordinates:
        return self._map_coords

    @property
    def avatar_current_room_location(self) -> str:
        return self._avatar_current_room_location

    def make_move(self, door_direction: str) -> None:
        """Move the current room location through the specified door direction."""
        try:
            name_next_room = self._current_room.doors[door_direction]
        except KeyError:
            raise InvalidMoveException(f"Room {self._current_room.name} has no door in direction {door_direction}")
        else:
            self._current_room = self._rooms[name_next_room]

    def get_dungeon_map_with_current_room_location(self) -> str:
        """Return the dungeon map in string representation,
        with the current room location indicated by an avatar."""
        room_name_length = len(self.current_room.name)
        no_room_tile = " " * room_name_length
        vertical_move_tile = "|" + " " * (room_name_length - 1)
        vertical_empty_move_tile = " " * len(vertical_move_tile)
        horizontal_move_tile = "-"
        horizontal_empty_move_tile = " " * len(horizontal_move_tile)
        dungeon_map = ""
        # for every (x,y) coordinate in the dungeon map, check whether it contains a room or not
        # and, if so, whether it has doors in directions "e" and "s"
        for y_coord in range(self._map_coords.y_max, self._map_coords.y_min - 1, -1):
            vertical_tiles = ""
            for x_coord in range(self._map_coords.x_min, self._map_coords.x_max + 1):
                if (x_coord, y_coord) in self._room_positions:
                    room_name = self._room_positions[(x_coord, y_coord)]
                    if self._current_room.name == room_name:
                        dungeon_map += self._avatar_current_room_location
                    else:
                        dungeon_map += room_name
                    # check whether to add a tile below containing a vertical move
                    if y_coord > self._map_coords.y_min:
                        if 's' in self._rooms[room_name].doors:
                            vertical_tiles += vertical_move_tile
                        else:
                            vertical_tiles += vertical_empty_move_tile
                    # check whether to add a tile to the right containing a horizontal move
                    if x_coord < self._map_coords.x_max:
                        if 'e' in self._rooms[room_name].doors:
                            dungeon_map += horizontal_move_tile
                        else:
                            dungeon_map += horizontal_empty_move_tile
                        # add an empty tile below the last horizontal (empty) move tile
                        if y_coord > self._map_coords.y_min:
                            vertical_tiles += horizontal_empty_move_tile
                else:
                    dungeon_map += no_room_tile
                    if y_coord > self._map_coords.y_min:
                        vertical_tiles += vertical_empty_move_tile
                    if x_coord < self._map_coords.x_max:
                        dungeon_map += horizontal_empty_move_tile
                        if y_coord > self._map_coords.y_min:
                            vertical_tiles += horizontal_empty_move_tile
            if y_coord > self._map_coords.y_min:
                dungeon_map = "".join((dungeon_map, "\n", vertical_tiles, "\n"))
        return dungeon_map

    def _compute_rooms_coordinates(
        self, initial_room: Room, coordinates_initial_room: tuple[int, int] = (0, 0)
    ) -> dict[tuple[int, int], str]:
        """Get (x,y) coordinates for each room, with respect to an initial room."""
        room_positions = {}
        self._traverse_rooms_with_dfs(
            initial_room, position=coordinates_initial_room, room_positions_visited=room_positions
        )
        return room_positions

    def _traverse_rooms_with_dfs(
        self, room: Room, position: tuple[int, int], room_positions_visited: dict[tuple[int, int], str]
    ) -> None:
        """Traverse all the rooms from an initial room, computing their (x,y) coordinates.
        Depth-first search (DFS) strategy is used, which modifies the input argument room_positions_visited."""
        if room.name in room_positions_visited.values():
            return room_positions_visited
        room_positions_visited[position] = room.name

        for door_direction, next_room_name in room.doors.items():
            if door_direction == 's':
                next_room_position = (position[0], position[1] - 1)
            elif door_direction == 'n':
                next_room_position = (position[0], position[1] + 1)
            elif door_direction == 'e':
                next_room_position = (position[0] + 1, position[1])
            elif door_direction == 'w':
                next_room_position = (position[0] - 1, position[1])
            next_room = self._rooms[next_room_name]
            self._traverse_rooms_with_dfs(next_room, next_room_position, room_positions_visited)

    def _compute_dungeon_map_coordinates(self) -> DungeonMapCoordinates:
        """Compute coordinates of the dungeon map, where the dungeon map
        is the smallest rectangle containing all rooms."""
        room_coordinates = self._room_positions.keys()
        x_coords = [coord[0] for coord in room_coordinates]
        y_coords = [coord[1] for coord in room_coordinates]
        map_coords = DungeonMapCoordinates(
            x_min=min(x_coords), x_max=max(x_coords), y_min=min(y_coords), y_max=max(y_coords)
        )
        return map_coords
