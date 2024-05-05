# SocketError Documentation

## __init__()

None

## get_error()

None

# MorgHTTPSocket Documentation

## __init__()

None

## __do_get()

Args:
        endpoint: One of either "inv", "stats", "equip", "events"
Returns:
        All JSON data from the endpoint as a dict.
Raises:
        SocketError: If the endpoint is not valid or the server is not running.

## test_endpoints()

Ensures all endpoints are working correctly to avoid errors happening when any method is called.
Returns:
        True if successful, False otherwise.

## get_hitpoints()

Fetches the current and maximum hitpoints of the player.
Returns:
        A Tuple(current_hitpoints, maximum_hitpoints).

## get_run_energy()

Fetches the current run energy of the player.
Returns:
        An int representing the current run energy.

## get_animation()

Fetches the current animation the actor is performing.
Returns:
        An int representing the current animation.

## get_animation_id()

Fetches the current animation frame ID the actor is using. Useful for checking if the player is doing
a particular action.
Returns:
        An int representing the current animation ID.

## get_is_player_idle()

Checks if the player is doing an idle animation.
Args:
        poll_seconds: The number of seconds to poll for an idle animation.
Returns:
        True if the player is idle, False otherwise..

## get_skill_level()

Gets level of inputted skill.
Args:
        skill: the name of the skill (not case sensitive)
Returns:
        The level of the skill as an int, or -1 if an error occurred.

## get_skill_xp()

Gets the total xp of a skill.
Args:
        skill: the name of the skill.
Returns:
        The total xp of the skill as an int, or -1 if an error occurred.

## get_skill_xp_gained()

Gets the xp gained of a skill. The tracker begins at 0 on client startup.
Args:
        skill: the name of the skill.
Returns:
        The xp gained of the skill as an int, or -1 if an error occurred.

## wait_til_gained_xp()

Waits until the player has gained xp in the inputted skill.
Args:
        skill: the name of the skill (not case sensitive).
        timeout: the maximum amount of time to wait for xp gain (seconds).
Returns:
        The xp gained of the skill as an int, or -1 if no XP was gained or an error occurred during the timeout.

## get_game_tick()

Fetches game tick number.
Returns:
        An int representing the current game tick.

## get_latest_chat_message()

Fetches the most recent chat message in the chat box.
Returns:
        A string representing the latest chat message.

## get_player_position()

Fetches the world point of a player.
Returns:
        A tuple of ints representing the player's world point (x, y, z), or (-1, -1, -1) if data is not present or invalid.

## get_player_region_data()

Fetches region data of a player's position.
Returns:
        A tuple of ints representing the player's region data (region_x, region_y, region_ID).

## get_camera_position()

Fetches the position of a player's camera.
Returns:
        A dict containing the player's camera position {yaw, pitch, x, y, z, x2, y2, z2},
        or None if data is not present or invalid.

## get_mouse_position()

Fetches the position of a player's mouse.
Returns:
        A tuple of ints representing the player's mouse position (x, y).

## get_interaction_code()

Fetches the interacting code of the current interaction. (Use case unknown)

## get_is_in_combat()

Determines if the player is in combat.
Returns:
        True if the player is in combat, False if not.
        Returns None if an error occurred.

## get_npc_hitpoints()

Fetches the HP of the NPC currently targetted.
TODO: Result seems to be multiplied by 6...?
Returns:
        An int representing the NPC's HP, or None if an error occurred.
        If no NPC is in combat, returns 0.

## get_inv()

Gets a list of dicts representing the player inventory.
Returns:
    List of dictionaries, each containing index, ID, and quantity of an item.

## get_if_item_in_inv()

Checks if an item is in the inventory or not.
Args:
        item_id: the id of the item to check for (an single ID, or list of IDs).
Returns:
        True if the item is in the inventory, False if not.

## get_is_inv_full()

Checks if player's inventory is full.
Returns:
        True if the player's inventory is full, False otherwise.

## get_is_inv_empty()

Checks if player's inventory is empty.
Returns:
        True if the player's inventory is empty, False otherwise.

## get_inv_item_indices()

For the given item ID(s), returns a list of inventory slot indexes that the item exists in.
Useful for locating items you do not want to drop. If you want to locate an item in your
inventory, consider using :meth:`MorgHTTPSocket.get_first_occurrence()` instead.
Args:
        item_id: The item ID to search for (an single ID, or list of IDs).
Returns:
        A list of inventory slot indexes that the item(s) exists in.

## get_first_occurrence()

For the given item ID(s), returns the first inventory slot index that the item exists in.
e.g. [1, 1, 2, 3, 3, 3, 4, 4, 4, 4] -> [0, 2, 3, 6]
Args:
    item_id: The item ID to search for (an single ID, or list of IDs).
Returns:
    The first inventory slot index that the item exists in for each unique item ID.
    If a single item ID is provided, returns an integer (or -1).
    If a list of item IDs is provided, returns a list of integers (or empty list).

## get_inv_item_stack_amount()

For the given item ID, returns the total amount of that item in your inventory.
This is only useful for items that stack (e.g. coins, runes, etc).
Args:
    id: The item ID to search for. If a list is passed, the first matching item will be used.
        This is useful for items that have multiple IDs (e.g. coins, coin pouches, etc.).
Returns:
    The total amount of that item in your inventory.

## get_is_item_equipped()

Checks if the player has given item(s) equipped. Given a list of IDs, returns True on first ID found.
Args:
        item_id: the id of the item to check for (a single ID, or list of IDs).
Returns:
        True if an item is equipped, False if not.

## get_equipped_item_quantity()

Checks for the quantity of an equipped item.
Args:
        item_id: The ID of the item to check for.
Returns:
        The quantity of the item equipped, or 0 if not equipped.

## convert_player_position_to_pixels()

Convert a world point into coordinate where to click with the mouse to make it possible to move via the socket.
TODO: Implement.
