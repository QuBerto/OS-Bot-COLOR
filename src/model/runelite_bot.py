"""
The RuneLiteBot class contains properties and functions that are common across all RuneLite-based clients. This class
can be inherited by additional abstract classes representing all bots for a specific game (E.g., OSNRBot, AloraBot, etc.).

To determine Thresholds for finding contours: https://pinetools.com/threshold-image

For converting RGB to HSV:
    https://stackoverflow.com/questions/10948589/choosing-the-correct-upper-and-lower-hsv-boundaries-for-color-detection-withcv/48367205#48367205

Item ID Database:
    https://www.runelocus.com/tools/osrs-item-id-list/
"""

import string
import time
from abc import ABCMeta
from typing import List, Union

import cv2
import keyboard
import numpy as np
import pyautogui
import pyautogui as pag
import requests
from deprecated import deprecated

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.debug as debug
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import utilities.runelite_cv as rcv
from model.bot import Bot, BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.geometry import Point, Rectangle, RuneLiteObject
from utilities.window import Window


class RuneLiteWindow(Window):
    current_action: Rectangle = None  # https://i.imgur.com/fKXuIyO.png
    hp_bar: Rectangle = None  # https://i.imgur.com/2lCovGV.png
    prayer_bar: Rectangle = None

    def __init__(self, window_title: str) -> None:
        """
        RuneLiteWindow is an extensions of the Window class, which allows for locating and interacting with key
        UI elements on screen.
        """
        super().__init__(window_title, padding_top=26, padding_left=0)

    # Override
    def initialize(self) -> bool:
        """
        Overrirde of Window.initialize(). This function is called when the bot is started.
        """
        if not super().initialize():
            return False
        self.__locate_hp_prayer_bars()
        self.current_action = Rectangle(
            left=10 + self.game_view.left,
            top=25 + self.game_view.top,
            width=128,
            height=20,
        )
        return True

    def __locate_hp_prayer_bars(self) -> None:
        """
        Creates Rectangles for the HP and Prayer bars on either side of the control panel, storing it in the
        class property.
        """
        bar_w, bar_h = 18, 250  # dimensions of the bars
        self.hp_bar = Rectangle(
            left=self.control_panel.left + 7,
            top=self.control_panel.top + 42,
            width=bar_w,
            height=bar_h,
        )
        self.prayer_bar = Rectangle(
            left=self.control_panel.left + 217,
            top=self.control_panel.top + 42,
            width=bar_w,
            height=bar_h,
        )

    # Override
    def resize(self, width: int = 773, height: int = 534) -> None:
        """
        Resizes the client window. Default size is 773x534 (minsize of fixed layout).
        Args:
            width: The width to resize the window to.
            height: The height to resize the window to.
        """
        if client := self.window:
            client.size = (width, height)


class RuneLiteBot(Bot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, game_title, bot_title, description, window: Window = RuneLiteWindow("RuneLite")) -> None:
        super().__init__(game_title, bot_title, description, window)
        self.bank_slots = []
        self.deposit_button = False
        self.imgtabs = False

    # --- OCR Functions ---
    @deprecated(reason="This is a slow way of checking if you are in combat. Consider using an API function instead.")
    def is_in_combat(self) -> bool:
        """
        Returns whether the player is in combat. This is achieved by checking if text exists in the RuneLite opponent info
        section in the game view, and if that text indicates an NPC is out of HP.
        """
        if ocr.extract_text(self.win.current_action, ocr.PLAIN_12, clr.WHITE):
            return True

    def is_player_doing_action(self, action: str):
        """
        Returns whether the player character is doing a given action. This works by checking the text in the current action
        region of the game view.
        Args:
            action: The action to check for (E.g., "Woodcutting" - case sensitive).
        Returns:
            True if the player is doing the given action, False otherwise.
        """
        return ocr.find_text(action, self.win.current_action, ocr.PLAIN_12, clr.GREEN)

    def pick_up_loot(self, items: Union[str, List[str]], supress_warning=True) -> bool:
        """
        Attempts to pick up a single purple loot item off the ground. It is your responsibility to ensure you have
        enough inventory space to pick up the item. The item closest to the game view center is picked up first.
        Args:
            item: The name(s) of the item(s) to pick up (E.g. -> "Coins", or "coins, bones", or ["Coins", "Dragon bones"]).
        Returns:
            True if the item was clicked, False otherwise.
        """
        # Capitalize each item name
        if isinstance(items, list):
            for i, item in enumerate(items):
                item = item.capitalize()
                items[i] = item
        else:
            items = self.capitalize_loot_list(items, to_list=True)
        # Locate Ground Items text
        if item_text := ocr.find_text(items, self.win.game_view, ocr.PLAIN_11, clr.PURPLE):
            for item in item_text:
                item.set_rectangle_reference(self.win.game_view)
            sorted_by_closest = sorted(item_text, key=Rectangle.distance_from_center)
            self.mouse.move_to(sorted_by_closest[0].get_center())
            for _ in range(5):
                if self.mouseover_text(contains=["Take"] + items, color=[clr.OFF_WHITE, clr.OFF_ORANGE]):
                    break
                self.mouse.move_rel(0, 3, 1, mouseSpeed="fastest")
            self.mouse.right_click()
            # search the right-click menu
            if take_text := ocr.find_text(
                items,
                self.win.game_view,
                ocr.BOLD_12,
                [clr.WHITE, clr.PURPLE, clr.ORANGE],
            ):
                self.mouse.move_to(take_text[0].random_point(), mouseSpeed="medium")
                self.mouse.click()
                return True
            else:
                self.log_msg(f"Could not find 'Take {items}' in right-click menu.")
                return False
        elif not supress_warning:
            self.log_msg(f"Could not find {items} on the ground.")
            return False

    def capitalize_loot_list(self, loot: str, to_list: bool):
        """
        Takes a comma-separated string of loot items and capitalizes each item.
        Args:
            loot_list: A comma-separated string of loot items.
            to_list: Whether to return a list of capitalized loot items (or keep it as a string).
        Returns:
            A list of capitalized loot items.
        """
        if not loot:
            return ""
        phrases = loot.split(",")
        capitalized_phrases = []
        for phrase in phrases:
            stripped_phrase = phrase.strip()
            capitalized_phrase = stripped_phrase.capitalize()
            capitalized_phrases.append(capitalized_phrase)
        return capitalized_phrases if to_list else ", ".join(capitalized_phrases)

    # --- NPC/Object Detection ---
    def get_nearest_tagged_NPC(self, include_in_combat: bool = False) -> RuneLiteObject:
        # sourcery skip: use-next
        """
        Locates the nearest tagged NPC, optionally including those in combat.
        Args:
            include_in_combat: Whether to include NPCs that are already in combat.
        Returns:
            A RuneLiteObject object or None if no tagged NPCs are found.
        """
        game_view = self.win.game_view
        img_game_view = game_view.screenshot()
        # Isolate colors in image
        img_npcs = clr.isolate_colors(img_game_view, clr.CYAN)
        img_fighting_entities = clr.isolate_colors(img_game_view, [clr.GREEN, clr.RED])
        # Locate potential NPCs in image by determining contours
        objs = rcv.extract_objects(img_npcs)
        if not objs:
            print("No tagged NPCs found.")
            return None
        for obj in objs:
            obj.set_rectangle_reference(self.win.game_view)
        # Sort shapes by distance from player
        objs = sorted(objs, key=RuneLiteObject.distance_from_rect_center)
        if include_in_combat:
            return objs[0]
        for obj in objs:
            if not rcv.is_point_obstructed(obj._center, img_fighting_entities):
                return obj
        return None

    def get_all_tagged_in_rect(self, rect: Rectangle, color: clr.Color) -> List[RuneLiteObject]:
        """
        Finds all contours on screen of a particular color and returns a list of Shapes.
        Args:
            rect: A reference to the Rectangle that this shape belongs in (E.g., Bot.win.control_panel).
            color: The clr.Color to search for.
        Returns:
            A list of RuneLiteObjects or empty list if none found.
        """
        img_rect = rect.screenshot()
        isolated_colors = clr.isolate_colors(img_rect, color)
        objs = rcv.extract_objects(isolated_colors)
        for obj in objs:
            obj.set_rectangle_reference(rect)
        return objs

    def get_nearest_tag(self, color: clr.Color) -> RuneLiteObject:
        """
        Finds the nearest outlined object of a particular color within the game view and returns it as a RuneLiteObject.
        Args:
            color: The clr.Color to search for.
        Returns:
            The nearest outline to the character as a RuneLiteObject, or None if none found.
        """
        if shapes := self.get_all_tagged_in_rect(self.win.game_view, color):
            shapes_sorted = sorted(shapes, key=RuneLiteObject.distance_from_rect_center)
            return shapes_sorted[0]
        else:
            return None

    def right_click_select(self, text: str, color: clr):
        """Right clicks on the screen and selects the option with the given text"""
        self.mouse.right_click()

        # Get the current mouse position and create a Point from it
        mouse_pos = Point(*pag.position())

        # Get monitor dimensions
        max_x, max_y = pag.size()

        # Define the dimensions of the rectangle as percentages of the screen size
        rect_width = int(max_x * 0.2)  # 20% of the screen width
        rect_height = int(max_y * 0.3)  # 30% of the screen height

        # Create points for the rectangle
        p1 = Point(max(mouse_pos.x - rect_width // 2, 0), mouse_pos.y)  # top-left point
        p2 = Point(min(mouse_pos.x + rect_width // 2, max_x), min(mouse_pos.y + rect_height, max_y))  # bottom-right point

        # Create the rectangle
        rect = Rectangle.from_points(p1, p2)

        found = ocr.find_text(text, rect, ocr.BOLD_12, color)
        if found:
            self.mouse.move_to(found[0].random_point())
            self.mouse.click()
            return True
        return False

    def zoom(
        self,
        out: bool = True,
        percent_zoom: float = 1.0,
        minimap: bool = False,
        max_steps: int = 50,
        step_duration: float = 0.01,
        verbose: bool = True,
        overwrite: bool = True,
    ) -> None:
        """Zoom in or out on the game window or minimap.

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
        """
        # We can only zoom via scroll if the cursor is on the game window or minimap.
        win_obj = self.win.minimap if minimap else self.win.game_view
        win_str = "minimap" if minimap else "game window"
        zstyle = "out" if out else "in"
        if verbose:
            self.log_msg(f"Moving mouse to {win_str}...")
        self.mouse.move_to(win_obj.random_point())
        if verbose:
            self.log_msg(f"Mouse moved to {win_str}.", overwrite=overwrite)
        # self.sleep()
        perc_str = int(percent_zoom * 100)
        if verbose:
            self.log_msg(f"Zooming {win_str} {zstyle} ({perc_str: d}%)...", overwrite=overwrite)
        max_zoom_units = 3600
        sign = -1 if out else 1
        scroll_amount = int(np.ceil(max_zoom_units * percent_zoom))
        num_steps = int(np.ceil(max_steps * percent_zoom))
        scroll_per_step = int(np.ceil(scroll_amount / num_steps)) * sign
        sleep_per_step = abs(step_duration / max_zoom_units)
        for _ in range(num_steps):
            pag.scroll(scroll_per_step)
            time.sleep(sleep_per_step)
        if verbose:
            self.log_msg(f"Zoomed {zstyle} {win_str} ({perc_str: d}%).", overwrite=overwrite)

    def get_player_position(self):
        """
        Finds player position on screen
        Returns:
            A tuple of current player position
        """
        if not self.win.world_location:
            object = ocr.find_text("Tile", self.win.game_view, ocr.PLAIN_12, [clr.OFF_WHITE])
            if object and len(object) == 1:
                self.win.world_location = Rectangle(left=object[0].get_top_left()[0], top=object[0].get_top_right()[1], width=130, height=20)
            else:
                return (-1, -1, -1)
        all_ascii = string.ascii_letters + string.punctuation + "".join(ocr.problematic_chars)
        filtered_ascii = "".join([char for char in all_ascii if char not in "0123456789 ,"])
        extracted = ocr.extract_text(self.win.world_location, ocr.PLAIN_12, [clr.OFF_WHITE], exclude_chars=filtered_ascii)
        result = (-1, -1, -1)
        if extracted:
            result = tuple(int(item) for item in extracted.split(","))
        return result

    def get_price(self, itemID: int) -> int:
        """
        Fetches the latest price of an item from the RuneScape Wiki API.

        Args:
            itemID (int): The ID of the item to fetch the price for.

        Returns:
            int: The average price of the item, or 0 if the request fails.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        }
        # Construct the URL to fetch the item's price
        url = "https://prices.runescape.wiki/api/v1/osrs/latest?id=" + str(itemID)
        # Send a GET request to the API
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract the high and low prices of the item
            high_price = data["data"][str(itemID)]["high"]
            low_price = data["data"][str(itemID)]["low"]
            # Calculate the average price
            average_price = int((high_price + low_price) / 2)
            return average_price
        else:
            # Return 0 if the request fails
            return 0

    def extract_number_inventory(self, inv_slot: int):
        """
        This will extract the number inside an inventory slot
        """
        all_characters_except_digits = list(string.ascii_letters + string.punctuation + string.whitespace)
        if not self.open_tab(3):
            return False
        quantity = ocr.extract_text(
            rect=self.win.inventory_slots[inv_slot],
            font=ocr.PLAIN_11,
            color=[clr.OFF_YELLOW, clr.WHITE, clr.RED],
            exclude_chars=all_characters_except_digits,
        )
        try:
            return int(quantity)
        except ValueError:
            return False

    def do_interface_action(self, key="space"):
        """
        This will run the inteface action
        """
        if not self.wait_till_interface():
            return False
        if self.press_key_interface(key):
            return False
        return True

    def wait_till_interface(self):
        """
        This will stop further execution until interface is opened
        """
        error = 0
        while not self.get_all():
            if error > 20:
                return False
            error += 1
            time.sleep(1 / 10)
        return True

    def press_key_interface(self, key):
        """
        This function will press i key on the inteface action
        """
        error = 0
        while self.get_all():
            if error > 20:
                return False
            error += 1
            keyboard.press(key)
            time.sleep(6 / 10)

    def wait_till_inv_out_of(self, items) -> bool:
        """
        This will stop further execution until inventory is out of item id(s).
        """
        error = 0
        api_m = MorgHTTPSocket()
        while api_m.get_inv_item_indices(items):
            if error > 200:
                return False
            error += 1
            time.sleep(2 / 10)
        return True

    def get_all(self) -> bool:
        """
        Will check if a certain action menu is open.
        """
        if ocr.find_text(["many", "make"], rect=self.win.chat, font=ocr.BOLD_12, color=clr.Color([64, 48, 32])):
            return True
        return False

    @deprecated(reason="Click item can do the same but better.")
    def get_item(self, id, last=False, move_first=False):
        """Find an item in inventory and click on it.
        :param int item_id: An id representing the item to click on.
        :param str text: The mouseover text to check for. (Default: Use)
        """
        api_m = MorgHTTPSocket()
        item = api_m.get_inv_item_indices(id)
        if item:
            if move_first:
                self.mouse.move_to(self.win.inventory_slots[item[0]].random_point(), mouseSpeed="fastest")
            while not self.mouseover_text("Use", color=clr.OFF_WHITE):
                if last:
                    self.mouse.move_to(self.win.inventory_slots[item[-1]].random_point(), mouseSpeed="fastest")
                else:
                    self.mouse.move_to(self.win.inventory_slots[item[0]].random_point(), mouseSpeed="fastest")
            self.mouse.click()

    def click_item(self, item_id: int, text: str = "Use", move_first: bool = False) -> bool:
        """Find an item in inventory and click on it.
        :param int item_id: An id representing the item to click on.
        :param str text: The mouseover text to check for. (Default: Use)
        """
        api_m = MorgHTTPSocket()
        items = api_m.get_inv_item_indices(item_id)
        if items:
            item = items[0]
        else:
            return False
        self.mouse.move_to(self.win.inventory_slots[item].random_point(), mouseSpeed="fastest")
        while not self.mouseover_text(text, color=clr.OFF_WHITE):
            self.mouse.move_to(self.win.inventory_slots[item].random_point(), mouseSpeed="fastest")
            if self.mouseover_text(text, color=clr.OFF_WHITE):
                break
            self.open_tab(3)
            self.mouse.move_to(self.win.inventory_slots[item].random_point(), mouseSpeed="fastest")
        self.mouse.click()
        self.log_msg("Clicked item #" + str(item))
        return True

    def click_rectangle(self, rectangle: Rectangle, text: str = "Use") -> bool:
        """
        Find an item in inventory and click on it.
            :param int item_id: An id representing the item to click on.
            :param str text: The mouseover text to check for. (Default: Use)
        """
        self.mouse.move_to(rectangle.random_point(), mouseSpeed="fastest")
        if not self.mouseover_text(text, color=clr.OFF_WHITE):
            return False
        self.mouse.click()
        self.log_msg(f"Clicked  {rectangle}")
        return True

    def click_tag_if_exists(self, color: clr.Color, text: str, check_for_red=False) -> bool:
        """
        Clicks on tag if it exists
        Args:
            color: a Color of the tag
            text: Mouse over text
            check_for_red: if check for red must be activated
        """
        if not (tag := self.get_nearest_tag(color)):
            return False
        self.mouse.move_to(tag.random_point(), mouseSpeed="fastest")
        if not self.mouseover_text(text, color=clr.OFF_WHITE):
            return False
        if check_for_red is True:
            return self.mouse.click(check_for_red=check_for_red)
        self.mouse.click()
        return True

    def find_open_tab(self):
        """
        Finds the opened tag by color
        """
        for index, tab in enumerate(self.win.cp_tabs):
            # Define the region of the screen to search (left, top, width, height)
            tab_color = clr.Color([90, 30, 15], [120, 40, 30])

            if self.color_in_object2(tab, tab_color):
                self.current_tab = index
                return index

            self.current_tab = False

    def open_tab(self, number: int, force_reset=False) -> bool:
        """
        Open tab on controlpanel
            :param int number: A number representing which tab to open
            :param bool force_reset: find open tab again, this proces can be slow
        """
        if not hasattr(self, "current_tab") or force_reset:
            self.find_open_tab()
            if self.current_tab is False:
                return False

        if number == self.current_tab:
            return True
        self.current_tab = number
        self.mouse.move_to(self.win.cp_tabs[number].random_point())
        self.mouse.click()
        self.log_msg(f"Opening tab {number}")
        return True

    def is_chat(self, text: str, colr=clr.BLACK) -> bool:
        """
        Check if text is in chat window
        Args:
            :param str text: A string to search inside the chat window
            :param clr color: A clr object representing the font color
        """
        if ocr.find_text(text, rect=self.win.chat, font=ocr.QUILL_8, color=colr):
            self.log_msg(f"{text} is found in chat")
            return True
        return False

    def toggle_prayer(self, prayer: str, toggle=False) -> bool:
        """
        Toggle prayer on or off
        Args:
            :param str prayer: A string containing the prayer to toggle
            :para toggle: Either False, on or off
        """
        images = {
            "magic": imsearch.BOT_IMAGES.joinpath("prayers", "magic.png"),
            "melee": imsearch.BOT_IMAGES.joinpath("prayers", "melee.png"),
            "missiles": imsearch.BOT_IMAGES.joinpath("prayers", "missiles.png"),
        }
        if image := images.get(prayer):
            self.open_tab(5)
            if img := imsearch.search_img_in_rect(image, self.win.control_panel):
                if self.color_in_object2(img, clr.Color([194, 171, 109], [195, 176, 123])):
                    self.log_msg("Prayer is currently on")
                    if not toggle:
                        self.mouse.move_to(img.random_point(), mouseSpeed="fastest")
                        self.mouse.click()
                        self.open_tab(3)
                    if toggle == "off":
                        self.mouse.move_to(img.random_point(), mouseSpeed="fastest")
                        self.mouse.click()
                        self.open_tab(3)
                    return True
                else:
                    self.log_msg("Prayer is currently off")
                    if not toggle:
                        self.mouse.move_to(img.random_point(), mouseSpeed="fastest")
                        self.mouse.click()
                        self.open_tab(3)
                    if toggle == "on":
                        self.mouse.move_to(img.random_point(), mouseSpeed="fastest")
                        self.mouse.click()
                        self.open_tab(3)
                    return True

    def open_bank(self):
        """
        Open the bank, a bank must always be marked cyan
        """
        self.click_bank()
        self.wait_till_bank_open()

    def withdraw_items(self, items, close=False, mouse_speed="fastest", check=True):
        """
        Withdraw items from the bank
        """
        result = True
        for item in items:
            if not self.withdraw_item(item, mouse_speed, check):
                result = False
        if close and not self.bank_close():
            result = False
        return result

    def bank_close(self, full_inv=False):
        """
        Close the bank
        """
        api_m = MorgHTTPSocket()
        error = 0
        if full_inv:
            while len(api_m.get_inv()) != 28:
                if error > 20:
                    return False
                error += 1
                time.sleep(2 / 10)
        while self.is_bank_open():
            pyautogui.press("esc")
            time.sleep(2 / 10)
        return True

    def withdraw_item(self, item, mouse_speed="fastest", check=True):
        """
        Withdraws an item from a slot in the inventory.

        Args:
            item: A dictionary representing the item to withdraw.
                It should contain information such as the slot number and the number of clicks needed to withdraw the item.
            mouse_speed: The speed of the mouse movement (default is "fastest").
            check: Whether to check if the item was successfully withdrawn (default is True).

        Returns:
            bool: True if the item withdrawal was attempted, False otherwise.
        """
        current_inventory = self.get_inventory_length()
        clicks = item.get("clicks")
        self.mouse.move_to(self.get_item_in_slot(item["slot"]).random_point(), mouseSpeed=mouse_speed)
        for _i in range(0, clicks):
            self.mouse.click()
            if check:
                time.sleep(4 / 10)
        while check and current_inventory == self.get_inventory_length():
            time.sleep(1 / 10)
        return True

    def get_inventory_length(self):
        """
        Gets the length of the player's inventory.

        This function utilizes an API call to retrieve the player's inventory items and returns the length of the inventory.

        Returns:
            int: The length of the player's inventory.
        """
        # Initialize an instance of MorgHTTPSocket for API communication
        api_m = MorgHTTPSocket()
        # Retrieve the player's inventory items using the API and return the length of the inventory
        return len(api_m.get_inv())

    def wait_till_bank_open(self):
        """
        Waits until the bank interface is open.

        This function continuously checks if the bank interface is open by calling the is_bank_open method until it returns True.

        """
        # Continuously loop until the bank interface is open
        while not self.is_bank_open():
            pass

    def click_bank(self):
        """
        Clicks on the bank icon in the game interface.

        This function moves the mouse cursor to the nearest cyan-colored tag (indicating the bank icon) and clicks on it.
        If the cursor is not over the "Use" or "Bank" text with an off-white color, it continuously moves the cursor to the nearest cyan-colored tag until it is.

        """
        # Continuously loop until the cursor is over the "Use" or "Bank" text with an off-white color
        while not self.mouseover_text(["Use", "Bank"], color=clr.OFF_WHITE):
            # Get the nearest cyan-colored tag (indicating the bank icon)
            if bank := self.get_nearest_tag(color=clr.CYAN):
                # Move the mouse cursor to the tag's position
                self.mouse.move_to(bank.random_point())
        # Once the cursor is over the "Use" or "Bank" text with an off-white color, click on it
        self.mouse.click()

    def is_bank_open(self):
        """
        Checks if the bank interface is currently open.

        This function searches for the bank tabs image within the game view or within a specific region if the bank tabs
        image has been previously located. If the bank tabs image is found with a confidence level of at least 0.05,
        it is considered that the bank interface is open.

        Returns:
            bool: True if the bank interface is open, False otherwise.
        """
        tabs_img = imsearch.BOT_IMAGES.joinpath("bank", "banktabs.png")
        self.performance_start()
        if self.imgtabs:
            if imsearch.search_img_in_rect(tabs_img, self.imgtabs, confidence=0.05):
                self.performance_end()
                return True
        else:
            if imsearch.search_img_in_rect(tabs_img, self.win.game_view, confidence=0.05):
                self.performance_end()
                return True
        self.performance_end()
        return False

    def get_item_in_slot(self, slot: int):
        """
        Retrieves the item located in the specified slot of the bank interface.

        This function first obtains the positions of the bank tabs.
        Then, it calculates the index of the bank slot corresponding to the specified slot.
        If the calculated index is valid (within the range of available bank slots),
        it returns the bank slot object located at that index.

        Args:
            slot (int): The slot number of the item to retrieve.

        Returns:
            The bank slot object located in the specified slot, or None if the slot is invalid.
        """
        self.get_banktabs_position()
        new_slot = slot - 1
        if len(self.bank_slots) > new_slot:
            return self.bank_slots[new_slot]

    def get_banktabs_position(self):
        """
        Gets the positions of the bank tabs in the bank interface.

        This function first checks if the number of bank slots is not equal to 8.
        If the number of bank slots is not 8, it searches for the image representing the bank tabs within the game view.
        Then, it retrieves the positions of the bank slots based on the found bank tabs image.

        """
        if len(self.bank_slots) != 8:
            tabs_img = imsearch.BOT_IMAGES.joinpath("bank", "banktabs.png")
            self.imgtabs = imsearch.search_img_in_rect(tabs_img, self.win.game_view)
            self.get_pixels_by_object(self.imgtabs, bankslots=True, offset_y=38, extra_margin_left=8, extra_margin_right=10)

    def click_deposit_all(self):
        """
        Clicks the "Deposit All" button in the bank interface.

        This function first checks if the bank interface is open. If not, it logs a message instructing to open the bank first.
        Then, it checks if the location of the deposit button is known. If not, it attempts to locate the deposit button.
        It continuously moves the mouse cursor to the deposit button until the mouseover text "Deposit" with an off-white color is detected.
        Once the mouseover text is detected, indicating that the cursor is over the "Deposit All" button, a click action is performed.

        """
        if not self.is_bank_open():
            self.log_msg("Open bank first")
        if not self.deposit_button:
            self.locate_deposit()
        while not self.mouseover_text("Deposit", color=clr.OFF_WHITE):
            self.mouse.move_to(self.deposit_button.random_point())
        self.mouse.click()

    def locate_deposit(self):
        """
        Locates the deposit button within the game view.

        This function searches for the deposit button within the game view by looking for an arrow_down image.
        If the deposit button is found, its location is stored in the 'deposit_button' attribute of the class instance.

        Returns:
            bool: True if the deposit button is found and its location is stored, False otherwise.
        """
        tabs_img = imsearch.BOT_IMAGES.joinpath("bank", "arrow_down.png")
        deposit_button = self.get_RLobject_by_object(
            imsearch.search_img_in_rect(tabs_img, self.win.game_view),
            offset_x=-45,
            offset_y=30,
            extra_margin_left=-5,
            extra_margin_right=-5,
            columns=1,
            margin=-5,
        )
        if deposit_button:
            self.deposit_button = deposit_button[0]
            return True
        return False

    def color_in_object(self, object: Rectangle, color: clr) -> bool:
        """
        Checks if a certain color is present in an object
        Args:
            object: A Rectangle to search in
            color: A color to search for
        Returns:
            bool True or False
        """

        region = object.to_dict().values()
        screenshot = pyautogui.screenshot(region=region)
        color_to_search = color  # Example: Red color
        for x in range(screenshot.width):
            for y in range(screenshot.height):
                pixel_color = screenshot.getpixel((x, y))
                if pixel_color == color_to_search:
                    return True
        return False

    from typing import Any, Dict, List

    def color_in_object2(self, object: Rectangle, color_range: clr.Color) -> bool:
        """
        Checks if the pixel color at any point in the object is within the specified color range.
        Args:
            object: A Rectangle to search in.
            color_range: A dictionary containing the lower and upper bounds for each color channel (R, G, B).
        Returns:
            bool: True if the color at any point in the object is within the specified color range, False otherwise.
        """
        region = object.to_dict().values()
        screenshot = pyautogui.screenshot(region=region)
        lower_bound = color_range.lower
        upper_bound = color_range.upper
        for x in range(screenshot.width):
            for y in range(screenshot.height):
                pixel_color = screenshot.getpixel((x, y))

                # Check if the pixel color falls within the specified color range
                if (
                    lower_bound[0] <= pixel_color[2] <= upper_bound[0]
                    and lower_bound[1] <= pixel_color[1] <= upper_bound[1]
                    and lower_bound[2] <= pixel_color[0] <= upper_bound[2]
                ):
                    return True
        return False

    def test(self, object, offset_x=0, offset_y=0, extra_margin_left=0, extra_margin_right=0, columns=8, margin=5):
        """
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
        """
        result = self.get_pixels_by_object(object, False, offset_x, offset_y, extra_margin_left, extra_margin_right, columns, margin)
        print(object)
        self.create_screenshot(result)

    def get_RLobject_by_object(self, object, bankslots=False, offset_x=0, offset_y=0, extra_margin_left=0, extra_margin_right=0, columns=8, margin=5):
        """
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
        """
        coords = object.to_dict()
        rect_x, rect_y, rect_w, rect_h = coords["left"], coords["top"], coords["width"], coords["height"]
        # Apply the offset and extra margins
        rect_y += offset_y
        rect_x += offset_x
        rect_x += extra_margin_left
        rect_w -= extra_margin_left + extra_margin_right

        num_columns = columns
        column_width = rect_w // num_columns

        pixel_coordinates = []

        for i in range(num_columns):
            start_x = rect_x + i * column_width + margin
            end_x = start_x + column_width - 2 * margin

            start_x = min(max(start_x, rect_x), rect_x + rect_w)
            end_x = min(max(end_x, rect_x), rect_x + rect_w)

            start_y = rect_y + margin
            end_y = rect_y + rect_h - margin

            pixel_coordinates.append(Rectangle(left=start_x, top=start_y, width=end_x - start_x, height=end_y - start_y))

        return pixel_coordinates

    def get_pixels_by_object(self, object, bankslots=False, offset_x=0, offset_y=0, extra_margin_left=0, extra_margin_right=0, columns=8, margin=5):
        """
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
        """
        coords = object.to_dict()
        rect_x, rect_y, rect_w, rect_h = coords["left"], coords["top"], coords["width"], coords["height"]
        # Apply the offset and extra margins
        rect_y += offset_y
        rect_x += offset_x
        rect_x += extra_margin_left
        rect_w -= extra_margin_left + extra_margin_right

        num_columns = columns
        column_width = rect_w // num_columns

        pixel_coordinates = []

        for i in range(num_columns):
            start_x = rect_x + i * column_width + margin
            end_x = start_x + column_width - 2 * margin

            start_x = min(max(start_x, rect_x), rect_x + rect_w)
            end_x = min(max(end_x, rect_x), rect_x + rect_w)

            start_y = rect_y + margin
            end_y = rect_y + rect_h - margin
            if bankslots:
                self.bank_slots.append(Rectangle(left=start_x, top=start_y, width=end_x - start_x, height=end_y - start_y))
            pixel_coordinates.append(((start_x, start_y), (end_x, end_y)))
        print(pixel_coordinates)
        return pixel_coordinates

    def create_screenshot(self, pixel_coordinates):
        """
        Creates screenshot from marked coordinated
        Args:
            pixel_coordinates: A list of pixel coordinates
        Returns:
            A Screenshot of set list
        """
        # Step 1: Take a screenshot
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Step 2: Highlight the pixels in each column
        for (start_x, start_y), (end_x, end_y) in pixel_coordinates:
            screenshot[start_y:end_y, start_x:end_x] = [0, 0, 255]  # Set the pixels to red (in BGR format)

        # Step 3: Display the image
        cv2.imshow("Highlighted Pixels", screenshot)

        # Step 4: Wait for a key press and then close the image window
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def performance_start(self):
        """
        Measure performance of an action. Call performance_end to end measuring
        """
        self.start_time = time.perf_counter()

    def performance_end(self):
        """
        Measure performance of an action. Prints time taken since performance_start
        """
        self.end_time = time.perf_counter()
        elapsed_time_ms = (self.end_time - self.start_time) * 1000  # Convert to milliseconds
        self.log_msg(f"Time taken full: {elapsed_time_ms: .2f} ms")

    def debug_runelite(self):
        """
        Debug some functions of RuneLiteBot
        """

        functions_to_debug = [
            ("is_player_doing_action(woodcutting)", lambda: self.is_player_doing_action("woodcutting")),
            ("pick_up_loot(ids.BONES)", lambda: self.pick_up_loot(["bones"])),
            ("get_nearest_tagged_NPC()", self.get_nearest_tagged_NPC),
            ("get_all_tagged_in_rect(game_view, GREEN)", lambda: self.get_all_tagged_in_rect(self.win.game_view, color=clr.GREEN)),
            ("get_nearest_tagged_NPC()", lambda: self.get_nearest_tag(clr.BLUE)),
            ("right_click_select()", lambda: self.right_click_select(text="Cancel", color=clr.OFF_WHITE)),
            ("zoom()", self.zoom),
            ("get_player_position()", self.get_player_position),
            ("extract_number_inventory(1)", lambda: self.extract_number_inventory(1)),
            ("get_all()", self.get_all),
            ("click_item()", lambda: self.click_item(ids.BONES)),
            ("click_tag_if_exists()", lambda: self.click_tag_if_exists(clr.BLUE, "Attack")),
            ("find_open_tab()", self.find_open_tab),
            ("open_tab(0)", lambda: self.open_tab(0)),
            ("open_tab(3)", lambda: self.open_tab(3)),
            ("is_chat(test)", lambda: self.is_chat("Test")),
            ("toggle_prayer(magic)", lambda: self.toggle_prayer("magic", "on")),
            ("toggle_prayer(magic)", lambda: self.toggle_prayer("magic", "off")),
            ("is_bank_open()", self.is_bank_open),
            ("get_price(id)", lambda: self.get_price(ids.RUNE_2H_AXE)),
            ("get_price(str)", lambda: self.get_price(4151)),
        ]

        for description, function in functions_to_debug:
            self.performance_start()
            result = function()
            self.performance_end()
            self.log_msg(f"{description}: {result}")
        time.sleep(2)

    # --- Client Settings ---
    @deprecated(reason="This method is no longer needed for RuneLite games that can launch with arguments through the OSBC client.")
    def logout_runelite(self):
        """
        Identifies the RuneLite logout button and clicks it.
        """
        self.log_msg("Logging out of RuneLite...")
        rl_login_icon = imsearch.search_img_in_rect(
            imsearch.BOT_IMAGES.joinpath("settings", "runelite_logout.png"),
            self.win.rectangle(),
            confidence=0.9,
        )
        if rl_login_icon is not None:
            self.mouse.move_to(rl_login_icon.random_point())
            self.mouse.click()
            time.sleep(0.2)
            pag.press("enter")
            time.sleep(1)
