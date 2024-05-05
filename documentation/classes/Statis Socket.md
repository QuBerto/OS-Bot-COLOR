# RLSTATUS Documentation

## _set_headers()

None

## do_POST()

None

## log_message()

Suppress logging.

# StatusSocket Documentation

## __init__()

None

## __RSERVER()

None

## get_player_data()

Fetches the entire blob of player_Data

## get_game_tick()

Fetches the game tick from the API.

## get_real_level()

Fetches the real level of a skill.
Args:
    skill_name: The name of the skill to check (must be all caps).
Example:
    >>> print(api_status.get_real_level("ATTACK"))

## get_boosted_level()

Fetches boosted level of a skill.
Args:
    skill_name: The name of the skill to check (must be all caps).
Example:
    >>> print(api_status.get_boosted_level("ATTACK"))

## get_is_boosted()

Compares real level to boosted level of a skill.
Args:
    skill_name: The name of the skill to check (must be all caps).
Returns:
    True if boosted level is greater than real level
Example:
    >>> print(api_status.get_is_boosted("ATTACK"))

## get_run_energy()

Gets the player's current run energy.
Returns:
        The player's current run energy as an int.

## get_is_inv_full()

Checks if player's inventory is full.
Returns:
        True if the player's inventory is full, False otherwise.

## get_is_inv_empty()

Checks if player's inventory is empty.
Returns:
        True if the player's inventory is empty, False otherwise.

## get_inv()

Gets a list of dicts representing the player inventory.
Returns:
        A list of dicts with the following keys:
                - index: The position of the item in the inventory.
                - id: The item ID.
                - quantity: The quantity of the item.
Example:
        for item in inv:
                print(f"Slot: {item['index']}, Item ID: {item['id']}, Amount: {item['amount']}")

## get_inv_item_indices()

For the given item ID, returns a list of inventory slot indexes that the item exists in.
Useful for locating items you do not want to drop.
Args:
        item_id: The item ID to search for (an single ID, or list of IDs).
Returns:
        A list of inventory slot indexes that the item exists in.

## get_inv_item_stack_amount()

For the given item ID, returns the total amount of that item in your inventory.
This is only useful for items that stack (e.g. coins, runes, etc).
Args:
        item_id: The item ID to search for. If a list is passed, the first matching item will be used.
                 This is useful for items that have multiple IDs (e.g. coins, coin pouches, etc.).
Returns:
        The total amount of that item in your inventory.

## get_is_player_idle()

Checks if the player is idle. Note, this does not check if the player is moving - it only
checks if they are performing an action animation (skilling, combat, etc).
Returns:
        True if the player is idle, False otherwise.
Notes:
        If you have the option, use MorgHTTPClient's idle check function instead. This one
        does not consider movement animations.

## get_is_player_praying()

Checks if the player is currently praying. Useful for knowing when you've run out of prayer points.
Returns:
        True if the player is praying, False otherwise.

## get_player_equipment()

None

## get_equipment_stats()

Checks your current equipment stats. Includes aStab, aSlash, aCrush, aMagic, aRange,
dStab, dSlash, dCrush, dMagic, dRange, str, rStr, mDmg.
Returns:
        A list of your current equipment stats.

## get_animation_data()

None

## get_animation_id()

None
