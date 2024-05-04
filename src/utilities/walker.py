import math
from typing import List, Literal, Tuple, Union

import utilities.api.locations as loc
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.pathfinder import Pathfinder
from utilities.geometry import Point

WalkPath = List[Point]
NamedDest = Union[str, Tuple[int, int], List[int]]


class Walker:
    DEGREES_PER_YAW: float = 360 / 2048  # 2048 units of camera yaw equals 360 degrees.
    PIXELS_PER_TILE: int = 4  # There are 4 pixels per tile on a default-scale minimap.
    MAX_TILE_DISTANCE: int = 12  # Click max 12 tiles ahead
    AREA_PRECISION: int = 5  # our position in tile-space is within a bounding area.
    NODE_DISTANCE: int = 10  # Max Distance between waypoints

    def __init__(self, runeLiteBot) -> None:
        """Initialize a walking `RuneLiteBot`.

        Args:
            runeLiteBot (RuneLiteBot): The `RuneLiteBot` to walk with.
        """
        self.bot = runeLiteBot
        self.api_m = MorgHTTPSocket()
        self.run_bool = False

    def update_position(self) -> None:
        """Update the `position`, `x`, and `y` attributes via the Morg API.

        Note that the returned position is measured in game tiles (rather than pixels).
        """
        self.position = self.api_m.get_player_position()
        self.x = self.position[0]
        self.y = self.position[1]
        self.z = self.position[2]

    def update_camera_angle(self) -> None:
        """Update the `camera_angle` attribute via the Morg API.

        The camera angle consists of both "pitch" and "yaw", but since we are
        navigating via the flat minimap, "yaw" is the only relevant value.
        """
        self.camera_angle = self.api_m.get_camera_position().get("yaw")

    def get_pixel_distance(self, dest: Point) -> Point:
        """Find the distance from minimap center to a destination point in pixels.

        The minimap should be brought to its default zoom level via right-clicking. It
        need not be aligned in any direction, however.

        Yaw increases as the camera POV rotates anticlockwise. Our calculations to
        follow, however, require angles measured from a clockwise frame of reference.
        We need to convert anticlockwise yaw in the player frame into degrees clockwise
        from North in the minimap frame.

        For example, if the camera angle, when converted from yaw to degrees, has a
        magnitude of 5 degrees anticlockwise from North, a 355-degree clockwise
        rotation from North would rotate to an equivalent perspective.

        Args:
            Point: Destination xy-coordinate, measured in minimap pixel space.

        Returns:
            Point: A `Point` representing a pixel coordinate relative to the center of
                the minimap, accounting for any rotation.
        """
        self.update_camera_angle()
        degrees = 360 - self.DEGREES_PER_YAW * self.camera_angle
        theta = math.radians(degrees)  # Convert to radians.
        self.update_position()
        # Convert the tile-space difference between our current location and desired
        # destination to a pixel-space difference on the minimap in a North-aligned
        # coordinate frame.
        x_reg = (dest.x - self.x) * self.PIXELS_PER_TILE
        y_reg = (self.y - dest.y) * self.PIXELS_PER_TILE
        # Now get the same pixel coordinate in the potentially-rotated minimap frame.
        x_mini = int(x_reg * math.cos(theta) + y_reg * math.sin(theta))
        y_mini = int(-x_reg * math.sin(theta) + y_reg * math.cos(theta))
        return Point(x_mini, y_mini)

    def change_position(self, dest: Point) -> None:
        """Click the minimap to change position.

        Args:
            dest (Point): The destination xy-coordinate in potentially rotated minimap
                pixel space.
        """
        self.update_position()
        dist_mini = self.get_pixel_distance(dest)
        if dist_mini:
            minimap_center = self.bot.win.minimap.get_center()
            x_new = int(round(minimap_center.x + dist_mini.x - 1))
            y_new = int(round(minimap_center.y + dist_mini.y - 1))
            self.bot.mouse.move_to(Point(x_new, y_new))
            self.bot.mouse.click()

    def get_target_posn(self, walk_path: WalkPath) -> Point:
        """Get the furthest-away coordinate to the destination within 12 tiles distance.

        Get the furthest-away `Point` within 12 tiles by searching from the destination
        `Point` backward to our current position.

        Args:
            walk_path (WalkPath): A list of `Point` tuples describing our character's
                travel path.

        Returns:
            Point: The next target point to walk to, measured in tile space.
        """
        self.update_position()
        # Using a generator for back-to-front search improves performance.
        idx = next(
            i
            for i in range(len(walk_path) - 1, -1, -1)
            if (abs(walk_path[i].x - self.x) <= self.MAX_TILE_DISTANCE and abs(walk_path[i].y - self.y) <= self.MAX_TILE_DISTANCE)  # Measured in tile space.
        )
        self.bot.log_msg(f"Walking progress: {idx}/{len(walk_path)}", overwrite=True)
        return walk_path[idx]

    def has_arrived(self, dest: Point) -> bool:
        """Return True if our position in tile-space is within a bounding area.

        Args:
            dest (Point): The destination `Point` to define an arrival area around.

        Returns:
            bool: True if we have arrived within the destination area, False otherwise.
        """
        self.update_position()
        p1 = Point(dest.x - self.AREA_PRECISION, dest.y - self.AREA_PRECISION)
        p2 = Point(dest.x + self.AREA_PRECISION, dest.y + self.AREA_PRECISION)
        within_x_range = self.x in range(p1.x, p2.x)
        within_y_range = self.y in range(p1.y, p2.y)
        return within_x_range and within_y_range

    def walk(self, walk_path: WalkPath, dest: Point = None) -> bool:
        """Walk along a `WalkPath` to a destination area.

        Note that each `Point` defining the `walk_path` and also `dest` is measured in
        tile space. Unlike `walk_to`, `walk` requires a previously-generated `WalkPath`
        instead of just a starting and destination `Point`.

        Args:
            walk_path (WalkPath): The series of `Point` objects to walk along.
            dest (Path, optional): The destination `Point` to define an arrival area
                around. Defaults to None, meaning the `walk_path` is simply walked until
                the last `Point` is reached.

        Returns:
            bool: True if the destination was reached, False if the `WalkPath` was
                simply traversed until its final `Point`.
        """
        dest = dest if dest else walk_path[-1]
        while True:
            new_pos = self.get_target_posn(walk_path)
            if self.has_arrived(dest):
                return True
            self.change_position(new_pos)  # Walk further along if we haven't arrived.
            if new_pos == walk_path[-1]:
                return False

    def walk_to(self, dest: NamedDest, host: Literal["dax", "osrspf"] = "dax") -> bool:
        """Call an API to generate the shortest `WalkPath` to a destination.

        Note! Dax is more reliable than osrspathfinder! Osrspathfinder periodically fails in certain locations. And why this occurs isn't immediately obvious.

        The API hosted by osrspathfinder or explv-map (i.e DAX) calculates the shortest
        path between our character's current position in the center of the game view
        and a desired location on the map (measured in tiles) via the A* pathfinding
        algorithm.

        Args:
            dest (NamedDest): Any `Point`, or perhaps instead a string name
                (i.e."VARROCK_SQUARE") associated with a destination listed in
                `utilities.locations`.
            host ("dax" or "osrspf"): Whether to use the DAX or OSRSpathfinder
                pathfinding API. Defaults to the more reliable "dax".

        Returns:
            bool: True if the destination was reached, False if the `WalkPath` was
                simply traversed until its final `Point`.
        """
        self.update_position()
        dest = (  # `dest` is a `Point` measured in tile space.
            getattr(loc, dest) if isinstance(dest, str) else dest  # Grab the coordinate from `utlities.api.locations`.
        )
        current_posn = Point(self.x, self.y)
        path = self.get_api_walk_path(p1=current_posn, p2=dest, host=host)
        return self.walk(path, dest)

    def get_api_walk_path(self, p1: Point, p2: Point, host: Literal["dax", "osrspf"]) -> WalkPath:
        """Retreive a `WalkPath` from either the DAX or OSRSpathfinder API endpoints.

        This method returns the results of the A* (pronounced "A-star") pathfinding
        algorithm. A* is a popular and efficient algorithm used to find the shortest
        path between two points in a graph or grid. It's commonly applied in video
        games, robotics, and other fields where pathfinding is essential.

        Args:
            p1 (Point): The start of the path to be calculated.
            p2 (Point): The destination point of the path to be calculated.
            host ("dax" or "osrspf"): Whether to use the DAX or OSRSpathfinder
                pathfinding API to obtain the desired path.

        Returns:
            WalkPath: The shortest valid path between the two provided points.
        """
        api = Pathfinder.get_path_dax if host == "dax" else Pathfinder.get_path_osrspf
        if path_raw := api(p1, p2):
            return self.add_waypoints(path_raw)
        self.bot.log_msg("API request for OSRSPF path failed.")
        return []

    def distance(self, p1: Point, p2: Point) -> float:
        """Return the Euclidean distance between two points.

        Args:
            p1 (Point): The reference point to use in the distance calculation.
            p2 (Point): Another point we'd like to measure distance to relative to the
                reference point.

        Returns:
            float: The absolute distance between the two provided `Point` objects.
        """
        return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)

    def add_waypoints(self, walk_path: WalkPath) -> WalkPath:
        """Smooth a `WalkPath` by computing intermediary `Point` objects between steps.

        Args:
            walk_path (WalkPath): The list of `Point` objects representing the
            traversal path we would like to smooth out.

        Returns:
            WalkPath: The original `WalkPath` provided, but with additional
                intermediary `Point` objects interspersed throughout. Note that the
                relative ordering of the points provided in `walk_path` is maintained.
        """
        walk_path_w_waypoints = [walk_path[0]]  # Start with the first coordinate.
        for step in range(len(walk_path) - 1):
            p1 = walk_path[step]
            p2 = walk_path[step + 1]
            dist = self.distance(p1, p2)
            # If the next point is far, add intermediary waypoints in between.
            if dist > self.NODE_DISTANCE:  # Measured in tile space.
                num_waypoints = math.ceil(dist / self.NODE_DISTANCE)
                dx = (p2.x - p1.x) / num_waypoints
                dy = (p2.y - p1.y) / num_waypoints
                for i in range(1, num_waypoints):
                    walk_path_w_waypoints.append(Point(round(p1.x + i * dx), round(p1.y + i * dy)))
            # Cap off the intermediary waypoints with the original point that was
            # further than 10 tiles away.
            walk_path_w_waypoints.append(p2)
        return walk_path_w_waypoints
