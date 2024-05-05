# Pathfinder Documentation

## __init__()

Initialize a `Pathfinder` and don't do anything else.

## make_api_call()

Make an API POST request to a pathfinding service.

Args:
    url (str): URL of the API endpoint we are hitting.
    headers (Dict[str, str]): Additional HTTP metadata for the API call.
    data (Dict[str, Any]): The JSON payload to ship with the API call.

Returns:
    Dict[str, Any]: JSON response dictionary.

## get_path_osrspf()

Retrieve a shortest `WalkPath` between `p1` and `p2` from OSRSpathfinder.

Args:
    p1 (Point): The start of the path to be calculated.
    p2 (Point): The destination point of the path to be calculated.

Returns:
    List[Point]: `WalkPath` object scraped from the JSON response from the
        OSRSpathfinder service.

## get_path_dax()

Retrieve a `WalkPath` object representing the shortest path to a destination.

Note that the DAX service provides human-readable error snippets. They are
listed here for reference:
    ERROR_MESSAGE_MAPPING = {
        "UNMAPPED_REGION": "Unmapped region.",
        "BLOCKED": "Tile is blocked.",
        "EXCEEDED_SEARCH_LIMIT": "Exceeded search limit.",
        "UNREACHABLE": "Unreachable tile.",
        "NO_WEB_PATH": "No web path.",
        "INVALID_CREDENTIALS": "Invalid credentials.",
        "RATE_LIMIT_EXCEEDED": "Rate limit exceeded.",
        "NO_RESPONSE_FROM_SERVER": "No response from server.",
        "UNKNOWN": "Unknown error occurred.",
    }

Args:
    p1 (Point): The start of the path to be calculated.
    p2 (Point): The destination point of the path to be calculated.

Returns:
    List[Point]: `WalkPath` object scraped from the JSON response from the
        DAX pathfinding service.
