# BotThread Documentation

## __init__()

None

## run()

None

## __get_id()

Returns id of the respective thread

## stop()

Raises SystemExit exception in the thread. This can be called from the main thread followed by join().

# BotStatus Documentation

# Bot Documentation

## __init__()

Instantiates a Bot object. This must be called by subclasses.
Args:
    game_title: title of the game the bot will interact with
    bot_title: title of the bot to display in the UI
    description: description of the bot to display in the UI
    window: window object the bot will use to interact with the game client
    launchable: whether the game client can be launched with custom arguments from the bot's UI

## main_loop()

Main logic of the bot. This function is called in a separate thread.

## create_options()

Defines the options for the bot using the OptionsBuilder.

## save_options()

Saves a dictionary of options as properties of the bot.
Args:
    options: dict - dictionary of options to save

## get_options_view()

Builds the options view for the bot based on the options defined in the OptionsBuilder.

## play()

Fired when the user starts the bot manually. This function performs necessary set up on the UI
and locates/initializes the game client window. Then, it launches the bot's main loop in a separate thread.

## __initialize_window()

Attempts to focus and initialize the game window by identifying core UI elements.

## stop()

Fired when the user stops the bot manually.

## set_controller()

None

## reset_progress()

Resets the current progress property to 0 and notifies the controller to update UI.

## update_progress()

Updates the progress property and notifies the controller to update UI.
Args:
    progress: float - number between 0 and 1 indicating percentage of progress.

## set_status()

Sets the status property of the bot and notifies the controller to update UI accordingly.
Args:
    status: BotStatus - status to set the bot to

## log_msg()

Sends a message to the controller to be displayed in the log for the user.
Args:
    msg: str - message to log
    overwrite: bool - if True, overwrites the current log message. If False, appends to the log.

## clear_log()

Requests the controller to tell the UI to clear the log.

## drop_all()

Shift-clicks all items in the inventory to drop them.
Args:
    skip_rows: The number of rows to skip before dropping.
    skip_slots: The indices of slots to avoid dropping.

## drop()

Shift-clicks inventory slots to drop items.
Args:
    slots: The indices of slots to drop.

## friends_nearby()

Checks the minimap for green dots to indicate friends nearby.
Returns:
    True if friends are nearby, False otherwise.

## logout()

Logs player out.

## take_break()

Takes a break for a random amount of time.
Args:
    min_seconds: minimum amount of time the bot could rest
    max_seconds: maximum amount of time the bot could rest
    fancy: if True, the randomly generated value will be from a truncated normal distribution
           with randomly selected means. This may produce more human results.

## sleep()

Don't do anything for a number of seconds.

Note that there is a built-in skew to use times closer to the lower bound due
to the definition of `fancy_normal_sample`.

Args:
    lo (float, optional): Defaults to 0.1.
    hi (float, optional): Defaults to 0.3.

## has_hp_bar()

Returns whether the player has an HP bar above their head. Useful alternative to using OCR to check if the
player is in combat. This function only works when the game camera is all the way up.

## get_hp()

Gets the HP value of the player. Returns -1 if the value couldn't be read.

## get_prayer()

Gets the Prayer points of the player. Returns -1 if the value couldn't be read.

## get_run_energy()

Gets the run energy of the player. Returns -1 if the value couldn't be read.

## get_special_energy()

Gets the special attack energy of the player. Returns -1 if the value couldn't be read.

## get_total_xp()

Gets the total XP of the player using OCR. Returns -1 if the value couldn't be read.

## mouseover_text()

Examines the mouseover text area.
Args:
    contains: The text to search for (single word, phrase, or list of words). Case sensitive. If left blank,
              returns all text in the mouseover area.
    color: The color(s) to isolate. If left blank, isolates all expected colors. Consider using
           clr.OFF_* colors for best results.
Returns:
    True if exact string is found, False otherwise.
    If args are left blank, returns the text in the mouseover area.

## chatbox_text()

Examines the chatbox for text. Currently only captures player chat text.
Args:
    contains: The text to search for (single word or phrase). Case sensitive. If left blank,
              returns all text in the chatbox.
Returns:
    True if exact string is found, False otherwise.
    If args are left blank, returns the text in the chatbox.

## set_compass_north()

None

## set_compass_west()

None

## set_compass_east()

None

## set_compass_south()

None

## __compass_right_click()

None

## move_camera()

Rotates the camera by specified degrees in any direction.
Agrs:
    horizontal: The degree to rotate the camera (-360 to 360).
    vertical: The degree to rotate the camera up (-90 to 90).
Note:
    A negative degree will rotate the camera left or down.

## toggle_auto_retaliate()

Toggles auto retaliate. Assumes client window is configured.
Args:
    toggle_on: Whether to turn on or off.

## select_combat_style()

Selects a combat style from the combat tab.
Args:
    combat_style: the attack type ("accurate", "aggressive", "defensive", "controlled", "rapid", "longrange").

## toggle_run()

Toggles run. Assumes client window is configured. Images not included.
Args:
    toggle_on: True to turn on, False to turn off.
