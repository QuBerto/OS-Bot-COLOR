# RuneLiteWindow Documentation

## __init__

RuneLiteWindow is an extensions of the Window class, which allows for locating and interacting with key
UI elements on screen.

## initialize

Overrirde of Window.initialize(). This function is called when the bot is started.

## __locate_hp_prayer_bars

Creates Rectangles for the HP and Prayer bars on either side of the control panel, storing it in the
class property.

## resize

Resizes the client window. Default size is 773x534 (minsize of fixed layout).
Args:
    width: The width to resize the window to.
    height: The height to resize the window to.

# RuneLiteBot Documentation

## __init__

None

## is_in_combat

Returns whether the player is in combat. This is achieved by checking if text exists in the RuneLite opponent info
section in the game view, and if that text indicates an NPC is out of HP.

## is_player_doing_action

Returns whether the player character is doing a given action. This works by checking the text in the current action
region of the game view.
Args:
    action: The action to check for (E.g., "Woodcutting" - case sensitive).
Returns:
    True if the player is doing the given action, False otherwise.

## pick_up_loot

Attempts to pick up a single purple loot item off the ground. It is your responsibility to ensure you have
enough inventory space to pick up the item. The item closest to the game view center is picked up first.
Args:
    item: The name(s) of the item(s) to pick up (E.g. -> "Coins", or "coins, bones", or ["Coins", "Dragon bones"]).
Returns:
    True if the item was clicked, False otherwise.

## capitalize_loot_list

Takes a comma-separated string of loot items and capitalizes each item.
Args:
    loot_list: A comma-separated string of loot items.
    to_list: Whether to return a list of capitalized loot items (or keep it as a string).
Returns:
    A list of capitalized loot items.

## get_nearest_tagged_NPC

Locates the nearest tagged NPC, optionally including those in combat.
Args:
    include_in_combat: Whether to include NPCs that are already in combat.
Returns:
    A RuneLiteObject object or None if no tagged NPCs are found.

## get_all_tagged_in_rect

Finds all contours on screen of a particular color and returns a list of Shapes.
Args:
    rect: A reference to the Rectangle that this shape belongs in (E.g., Bot.win.control_panel).
    color: The clr.Color to search for.
Returns:
    A list of RuneLiteObjects or empty list if none found.

## get_nearest_tag

Finds the nearest outlined object of a particular color within the game view and returns it as a RuneLiteObject.
Args:
    color: The clr.Color to search for.
Returns:
    The nearest outline to the character as a RuneLiteObject, or None if none found.

## right_click_select

Right clicks on the screen and selects the option with the given text

## zoom

Zoom in or out on the game window or minimap.

Note that 3600 is the amount of backward scrolling necessary to zoom all the
way out from a fully zoomed in game window.

Args:
    out (bool, optional): Zoom out if True, zoom in if False. Defaults to True.
    percent_zoom (float, optional): How much to zoom. Defaults to 1.0 (100%).
    minimap (bool, optional): Zoom the minimap if True, otherwise zoom the game
        window. Defaults to False.
    max_steps (int, optional): The maximum number of scroll steps to use. Use
        this to calibrate overall scroll animation speed. Defaults to 50.
    step_duration (float, optional): Seconds to wait between scroll steps. Use
        this to calibrate overall scroll animation speed. Defaults to 0.01.
    verbose (bool, optional): Whether to print log messages. Defaults to True.
    overwrite (bool, optional): Whether to reduce log message spam. Defaults to
        True.

## get_player_position

Finds player position on screen
Returns:
    A tuple of current player position

## get_price

Fetches the latest price of an item from the RuneScape Wiki API.

Args:
    itemID (int): The ID of the item to fetch the price for.

Returns:
    int: The average price of the item, or 0 if the request fails.

## extract_number_inventory

This will extract the number inside an inventory slot

## do_interface_action

This will run the inteface action

## wait_till_interface

This will stop further execution until interface is opened

## press_key_interface

This function will press i key on the inteface action

## wait_till_inv_out_of

This will stop further execution until inventory is out of item id(s).

## get_all

Will check if a certain action menu is open.

## get_item

Find an item in inventory and click on it.
:param int item_id: An id representing the item to click on.
:param str text: The mouseover text to check for. (Default: Use)

## click_item

Find an item in inventory and click on it.
:param int item_id: An id representing the item to click on.
:param str text: The mouseover text to check for. (Default: Use)

## click_rectangle

Find an item in inventory and click on it.
    :param int item_id: An id representing the item to click on.
    :param str text: The mouseover text to check for. (Default: Use)

## click_tag_if_exists

Clicks on tag if it exists
Args:
    color: a Color of the tag
    text: Mouse over text
    check_for_red: if check for red must be activated

## find_open_tab

Finds the opened tag by color

## open_tab

Open tab on controlpanel
    :param int number: A number representing which tab to open
    :param bool force_reset: find open tab again, this proces can be slow

## is_chat

Check if text is in chat window
Args:
    :param str text: A string to search inside the chat window
    :param clr color: A clr object representing the font color

## toggle_prayer

Toggle prayer on or off
Args:
    :param str prayer: A string containing the prayer to toggle
    :para toggle: Either False, on or off

## open_bank

Open the bank, a bank must always be marked cyan

## withdraw_items

Withdraw items from the bank

## bank_close

Close the bank

## withdraw_item

Withdraws an item from a slot in the inventory.

Args:
    item: A dictionary representing the item to withdraw.
        It should contain information such as the slot number and the number of clicks needed to withdraw the item.
    mouse_speed: The speed of the mouse movement (default is "fastest").
    check: Whether to check if the item was successfully withdrawn (default is True).

Returns:
    bool: True if the item withdrawal was attempted, False otherwise.

## get_inventory_length

Gets the length of the player's inventory.

This function utilizes an API call to retrieve the player's inventory items and returns the length of the inventory.

Returns:
    int: The length of the player's inventory.

## wait_till_bank_open

Waits until the bank interface is open.

This function continuously checks if the bank interface is open by calling the is_bank_open method until it returns True.

## click_bank

Clicks on the bank icon in the game interface.

This function moves the mouse cursor to the nearest cyan-colored tag (indicating the bank icon) and clicks on it.
If the cursor is not over the "Use" or "Bank" text with an off-white color, it continuously moves the cursor to the nearest cyan-colored tag until it is.

## is_bank_open

Checks if the bank interface is currently open.

This function searches for the bank tabs image within the game view or within a specific region if the bank tabs
image has been previously located. If the bank tabs image is found with a confidence level of at least 0.05,
it is considered that the bank interface is open.

Returns:
    bool: True if the bank interface is open, False otherwise.

## get_item_in_slot

Retrieves the item located in the specified slot of the bank interface.

This function first obtains the positions of the bank tabs.
Then, it calculates the index of the bank slot corresponding to the specified slot.
If the calculated index is valid (within the range of available bank slots),
it returns the bank slot object located at that index.

Args:
    slot (int): The slot number of the item to retrieve.

Returns:
    The bank slot object located in the specified slot, or None if the slot is invalid.

## get_banktabs_position

Gets the positions of the bank tabs in the bank interface.

This function first checks if the number of bank slots is not equal to 8.
If the number of bank slots is not 8, it searches for the image representing the bank tabs within the game view.
Then, it retrieves the positions of the bank slots based on the found bank tabs image.

## click_deposit_all

Clicks the "Deposit All" button in the bank interface.

This function first checks if the bank interface is open. If not, it logs a message instructing to open the bank first.
Then, it checks if the location of the deposit button is known. If not, it attempts to locate the deposit button.
It continuously moves the mouse cursor to the deposit button until the mouseover text "Deposit" with an off-white color is detected.
Once the mouseover text is detected, indicating that the cursor is over the "Deposit All" button, a click action is performed.

## locate_deposit

Locates the deposit button within the game view.

This function searches for the deposit button within the game view by looking for an arrow_down image.
If the deposit button is found, its location is stored in the 'deposit_button' attribute of the class instance.

Returns:
    bool: True if the deposit button is found and its location is stored, False otherwise.

## color_in_object

Checks if a certain color is present in an object
Args:
    object: A Rectangle to search in
    color: A color to search for
Returns:
    bool True or False

## color_in_object2

Checks if the pixel color at any point in the object is within the specified color range.
Args:
    object: A Rectangle to search in.
    color_range: A dictionary containing the lower and upper bounds for each color channel (R, G, B).
Returns:
    bool: True if the color at any point in the object is within the specified color range, False otherwise.

## test

Takes an object, turn it into multiple objects take a screenshot and mork those objects
Args:
    object: A Runelite object
    offset_x: Move pixels to x
    offset_y: Move pixels to y
    extra_margin_left: add margin to each objext on the left, can also be negative
    extra_margin_right: add margin to each objext on the left, can also be negative
    columns: How many colums
    margin: add margin around each column
Returns:
    Screenshot with marked objects

## get_RLobject_by_object

Takes an object, turn it into multiple objects take a screenshot and mork those objects
Args:
    object: A Runelite object
    offset_x: Move pixels to x
    offset_y: Move pixels to y
    extra_margin_left: add margin to each objext on the left, can also be negative
    extra_margin_right: add margin to each objext on the left, can also be negative
    columns: How many colums
    margin: add margin around each column
Returns:
    Runelite objects

## get_pixels_by_object

Takes an object, turn it into multiple objects take a screenshot and mork those objects
Args:
    object: A Runelite object
    offset_x: Move pixels to x
    offset_y: Move pixels to y
    extra_margin_left: add margin to each objext on the left, can also be negative
    extra_margin_right: add margin to each objext on the left, can also be negative
    columns: How many colums
    margin: add margin around each column
Returns:
    pixel_coordinates

## create_screenshot

Creates screenshot from marked coordinated
Args:
    pixel_coordinates: A list of pixel coordinates
Returns:
    A Screenshot of set list

## performance_start

Measure performance of an action. Call performance_end to end measuring

## performance_end

Measure performance of an action. Prints time taken since performance_start

## debug_runelite

Debug some functions of RuneLiteBot

## logout_runelite

Identifies the RuneLite logout button and clicks it.
