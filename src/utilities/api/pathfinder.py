import json
from typing import Any, Dict

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from utilities.geometry import List, Point


class Pathfinder:
    def __init__(self) -> None:
        """Initialize a `Pathfinder` and don't do anything else."""
        pass

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
    def make_api_call(
        url: str,
        headers: Dict[str, str],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make an API POST request to a pathfinding service.

        Args:
            url (str): URL of the API endpoint we are hitting.
            headers (Dict[str, str]): Additional HTTP metadata for the API call.
            data (Dict[str, Any]): The JSON payload to ship with the API call.

        Returns:
            Dict[str, Any]: JSON response dictionary.
        """
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_path_osrspf(p1: Point, p2: Point) -> List[Point]:
        """Retrieve a shortest `WalkPath` between `p1` and `p2` from OSRSpathfinder.

        Args:
            p1 (Point): The start of the path to be calculated.
            p2 (Point): The destination point of the path to be calculated.

        Returns:
            List[Point]: `WalkPath` object scraped from the JSON response from the
                OSRSpathfinder service.
        """
        url = "https://osrspathfinder.com/find-path"
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "algo": "A_STAR",
            "start": {"plane": 0, "x": p1.x, "y": p1.y},
            "end": {"plane": 0, "x": p2.x, "y": p2.y},
        }
        try:
            response = Pathfinder.make_api_call(url, headers, payload)
            if path_raw := response["result"]["steps"][0]["path"]:
                return [Point(step["x"], step["y"]) for step in path_raw]
        except requests.exceptions.HTTPError as exc:  # Handle non-200 statuses.
            print(f"HTTP error: {exc}")
        except Exception as exc:
            print(f"An unexpected error occurred: {exc}")
        return []

    @staticmethod
    def get_path_dax(p1: Point, p2: Point) -> List[Point]:
        """Retrieve a `WalkPath` object representing the shortest path to a destination.

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
        """
        url = "https://explv-map.siisiqf.workers.dev/"
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://explv.github.io",
        }
        payload = {
            "start": {"x": p1.x, "y": p1.y, "z": 0},
            "end": {"x": p2.x, "y": p2.y, "z": 0},
            "player": {"members": True},
        }
        try:
            if path_raw := Pathfinder.make_api_call(url, headers, payload)["path"]:
                return [Point(step["x"], step["y"]) for step in path_raw]
        except requests.exceptions.HTTPError as exc:  # Handle non-200 statuses.
            print(f"HTTP error: {exc}")
        except Exception as exc:
            print(f"An unexpected error occurred: {exc}")
        return []
