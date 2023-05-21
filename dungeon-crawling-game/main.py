import configparser
import warnings

from model.game import Room, DungeonCrawlingGame, InvalidMoveException

_ROOM_NAME_LENGTH = 2
_OPPOSITE_DIRECTION = {'s': 'n', 'n': 's', 'e': 'w', 'w': 'e'}
_DOOR_DIRECTIONS = {"s", "n", "w", "e"}
_CONFIG_SECTION = "FILE"
_MAX_SIZE_DUNGEON_MAP = (20, 20)


def main(config_file: str = "config.ini") -> None:
    """Run the application."""
    print("Welcome to the Dungeon Crawling Game!")
    print("Preparing the game...")
    input_file = parse_config_file(config_file)
    if not input_file:
        print(
            f"Error in parsing the config file {config_file}. "
            f"Please specify the correct parameters under section {_CONFIG_SECTION}."
        )
        print("Game Over")
        return
    try:
        rooms = read_rooms_from_file(input_file)
    except ValueError as error:
        print(f"Error: {error}")
        print("Game Over")
        return
    game = DungeonCrawlingGame(rooms=rooms)
    if game.map_coords.x_max - game.map_coords.x_min + 1 > _MAX_SIZE_DUNGEON_MAP[0] \
            or game.map_coords.y_max - game.map_coords.y_min + 1 > _MAX_SIZE_DUNGEON_MAP[1]:
        print(f"Error: The size of the dungeon map must be at most {_MAX_SIZE_DUNGEON_MAP}")
        print("Game Over")
        return
    print("Ready to start!")
    print(
        "This is the current map of the dungeon. "
        f"Your room location is indicated by '{game.avatar_current_room_location}'."
    )
    while True:
        dungeon_map = game.get_dungeon_map_with_current_room_location()
        print(dungeon_map)
        print(f"You are in room {game.current_room.name}")
        print(f"Possible moves: {' '.join(game.current_room.doors.keys())}")
        user_input = input("Enter your choice (Z or z to interrupt):")
        print("You typed: " + user_input)
        user_input = user_input.strip().lower()
        if user_input == "z":
            print("Thank you for playing. See you soon!")
            return
        if not set(user_input).issubset(_DOOR_DIRECTIONS):
            print("What you typed does not exist. Try again.")
        else:
            moves = tuple(user_input)
            for move_idx, move in enumerate(moves):
                try:
                    game.make_move(move)
                except InvalidMoveException as error:
                    print(error)
                    print(f"These moves get skipped: {' '.join(moves[move_idx:])}")
                    break
        print()


def parse_config_file(config_file: str) -> str:
    """Read and parse configuration file to retrieve filepath info."""
    config = configparser.ConfigParser()
    filepath = None
    try:
        config.read(config_file)
    except configparser.MissingSectionHeaderError:
        return filepath
    if config.has_section(_CONFIG_SECTION):
        file_config = config[_CONFIG_SECTION]
        filepath = file_config.get("filepath", None)
    return filepath


def read_rooms_from_file(filepath: str) -> dict[str, Room]:
    """Read and parse file containing rooms information."""
    supported_file_extension = ".txt"
    if not filepath.endswith(supported_file_extension):
        raise ValueError(f"File format is not supported. Extension must be {supported_file_extension}")
    rooms = {}
    try:
        with open(filepath) as file_handler:
            for line in file_handler:
                room_name, *doors_list = line.strip().split()
                room_doors = {door[0]: door[2:] for door in doors_list}
                room = Room(name=room_name, doors=room_doors)
                if room_name in rooms:
                    warnings.warn(f"Found a duplicate for room {room_name}. The latest row is kept.")
                rooms[room_name] = room
    except IOError as error:
        raise OSError(f"Cannot locate or access file {filepath}. Error: {error}.")
    rooms_are_valid = validate_rooms(rooms)
    if not rooms_are_valid:
        raise ValueError(f"Rooms in {filepath} are not specified in a valid format.")
    return rooms


def validate_rooms(rooms: dict[str, Room]) -> bool:
    """Validate whether rooms are provided in the right format and with correct door connections."""
    for room in rooms.values():
        if len(room.name) != _ROOM_NAME_LENGTH or room.name in room.doors.values() or not set(
            room.doors.keys()
        ).issubset(_DOOR_DIRECTIONS):
            return False
        for door_direction, next_room_name in room.doors.items():
            next_room = rooms[next_room_name]
            next_room_connection = next_room.doors.get(_OPPOSITE_DIRECTION[door_direction])
            if next_room_connection is None or next_room_connection != room.name:
                return False
    return True


if __name__ == '__main__':
    main()
