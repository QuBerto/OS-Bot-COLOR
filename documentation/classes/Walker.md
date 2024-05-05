# Walker Documentation

## __init__

Initialize a walking `RuneLiteBot`.

Args:
    runeLiteBot (RuneLiteBot): The `RuneLiteBot` to walk with.

## update_position

Update the `position`, `x`, and `y` attributes via the Morg API.

Note that the returned position is measured in game tiles (rather than pixels).

## update_camera_angle

Update the `camera_angle` attribute via the Morg API.

The camera angle consists of both "pitch" and "yaw", but since we are
navigating via the flat minimap, "yaw" is the only relevant value.

## get_pixel_distance

Find the distance from minimap center to a destination point in pixels.

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

## change_position

Click the minimap to change position.

Args:
    dest (Point): The destination xy-coordinate in potentially rotated minimap
        pixel space.

## get_target_posn

Get the furthest-away coordinate to the destination within 12 tiles distance.

Get the furthest-away `Point` within 12 tiles by searching from the destination
`Point` backward to our current position.

Args:
    walk_path (WalkPath): A list of `Point` tuples describing our character's
        travel path.

Returns:
    Point: The next target point to walk to, measured in tile space.

## has_arrived

Return True if our position in tile-space is within a bounding area.

Args:
    dest (Point): The destination `Point` to define an arrival area around.

Returns:
    bool: True if we have arrived within the destination area, False otherwise.

## walk

Walk along a `WalkPath` to a destination area.

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

## walk_to

Call an API to generate the shortest `WalkPath` to a destination.

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

## get_api_walk_path

Retreive a `WalkPath` from either the DAX or OSRSpathfinder API endpoints.

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

## distance

Return the Euclidean distance between two points.

Args:
    p1 (Point): The reference point to use in the distance calculation.
    p2 (Point): Another point we'd like to measure distance to relative to the
        reference point.

Returns:
    float: The absolute distance between the two provided `Point` objects.

## add_waypoints

Smooth a `WalkPath` by computing intermediary `Point` objects between steps.

Args:
    walk_path (WalkPath): The list of `Point` objects representing the
    traversal path we would like to smooth out.

Returns:
    WalkPath: The original `WalkPath` provided, but with additional
        intermediary `Point` objects interspersed throughout. Note that the
        relative ordering of the points provided in `walk_path` is maintained.
