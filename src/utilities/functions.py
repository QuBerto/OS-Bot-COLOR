import string
import time
from pathlib import Path

import cv2
import keyboard
import numpy as np
import pyautogui

import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
from utilities.geometry import Point, Rectangle


class QubotFeatures:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.current_tab = 3
        self.cape_slot = False

    def extract_number_inventory(self, inv_slot: int):
        all_characters_except_digits = list(string.ascii_letters + string.punctuation + string.whitespace)
        if self.current_tab != 3 and not self.open_tab(3):
            return False
        quantity = ocr.extract_text(
            rect=self.bot.win.inventory_slots[inv_slot],
            font=ocr.PLAIN_11,
            color=[clr.OFF_YELLOW, clr.WHITE, clr.RED],
            exclude_chars=all_characters_except_digits,
        )
        try:
            return int(quantity)
        except ValueError:
            return False

    def do_interface_action(self, key="space"):
        if not self.wait_till_interface():
            return False
        if self.press_key_interface(key):
            return False
        return True

    def wait_till_interface(self):
        error = 0
        while not self.get_all():
            if error > 20:
                return False
            error += 1
            time.sleep(1 / 10)
        return True

    def press_key_interface(self, key):
        error = 0
        while self.get_all():
            if error > 20:
                return False
            error += 1
            keyboard.press(key)
            time.sleep(6 / 10)

    def wait_till_inv_out_of(self, items):
        error = 0
        while self.bot.api_m.get_inv_item_indices(items):
            if error > 200:
                return False
            error += 1
            time.sleep(2 / 10)
        return True

    def get_all(self):
        if ocr.find_text(["many", "make"], rect=self.bot.win.chat, font=ocr.BOLD_12, color=clr.Color([64, 48, 32])):
            return True
        return False

    def get_item(self, id, last=False, move_first=False):
        item = self.bot.api_m.get_inv_item_indices(id)
        if item:
            if move_first:
                self.bot.mouse.move_to(self.bot.win.inventory_slots[item[0]].random_point(), mouseSpeed="fastest")
            while not self.bot.mouseover_text("Use", color=clr.OFF_WHITE):
                if last:
                    self.bot.mouse.move_to(self.bot.win.inventory_slots[item[-1]].random_point(), mouseSpeed="fastest")
                else:
                    self.bot.mouse.move_to(self.bot.win.inventory_slots[item[0]].random_point(), mouseSpeed="fastest")
            self.bot.mouse.click()

    def click_item(self, item_id: int, text: str = "Use"):
        """Find an item in inventory and click on it.
        :param int item_id: An id representing the item to click on.
        :param str text: The mouseover text to check for. (Default: Use)
        """
        items = self.bot.api_m.get_inv_item_indices(item_id)
        if items:
            item = items[0]
        else:
            return False
        self.bot.mouse.move_to(self.bot.win.inventory_slots[item].random_point(), mouseSpeed="fastest")
        while not self.bot.mouseover_text(text, color=clr.OFF_WHITE):
            self.bot.mouse.move_to(self.bot.win.inventory_slots[item].random_point(), mouseSpeed="fastest")
            if self.bot.mouseover_text(text, color=clr.OFF_WHITE):
                break
            self.open_tab(3)
            self.bot.mouse.move_to(self.win.inventory_slots[item].random_point(), mouseSpeed="fastest")
        self.bot.mouse.click()
        self.bot.log_msg("Clicked item #" + str(item))
        return True

    def click_rectangle(self, rectangle: Rectangle, text: str = "Use"):
        """Find an item in inventory and click on it.
        :param int item_id: An id representing the item to click on.
        :param str text: The mouseover text to check for. (Default: Use)
        """

        self.bot.mouse.move_to(rectangle.random_point(), mouseSpeed="fastest")
        if not self.bot.mouseover_text(text, color=clr.OFF_WHITE):
            return False
        self.bot.mouse.click()
        self.bot.log_msg(f"Clicked  {rectangle}")
        return True

    def click_tag_if_exists(self, color, text, check_for_red=False):
        if not (tag := self.bot.get_nearest_tag(color)):
            return False
        self.bot.mouse.move_to(tag.random_point(), mouseSpeed="fastest")
        if not self.bot.mouseover_text(text, color=clr.OFF_WHITE):
            return False
        if check_for_red is True:
            return self.bot.mouse.click(check_for_red=check_for_red)
        self.bot.mouse.click()
        return True

    def turn_on_prayer(self, type):
        images = {
            "magic": imsearch.BOT_IMAGES.joinpath("prayers", "magic.png"),
            "melee": imsearch.BOT_IMAGES.joinpath("prayers", "melee.png"),
            "missiles": imsearch.BOT_IMAGES.joinpath("prayers", "missiles.png"),
        }
        image = images.get(type)
        if image:
            self.open_tab(5)
            img = imsearch.search_img_in_rect(image, self.bot.win.control_panel)
            if img:
                # Define the region of the screen to search (left, top, width, height)
                region = self.bot.win.control_panel.to_dict().values()

                # Take a screenshot of the defined region
                screenshot = pyautogui.screenshot(region=region)

                # Define the color to search for (RGB tuple)
                color_to_search = (194, 171, 109)  # Example: Red color

                # Iterate over each pixel in the screenshot to search for the color
                for x in range(screenshot.width):
                    for y in range(screenshot.height):
                        pixel_color = screenshot.getpixel((x, y))
                        if pixel_color == color_to_search:
                            # Color found at coordinates (x, y) relative to the defined region
                            self.open_tab(3)
                            return True
                self.bot.mouse.move_to(img.random_point(), mouseSpeed="fastest")
                self.bot.mouse.click()
                # Iterate over each pixel in the screenshot to search for the color
                for x in range(screenshot.width):
                    for y in range(screenshot.height):
                        pixel_color = screenshot.getpixel((x, y))
                        if pixel_color == color_to_search:
                            # Color found at coordinates (x, y) relative to the defined region
                            self.open_tab(3)
                            return True

    def turn_off_prayer(self, type):
        images = {
            "magic": imsearch.BOT_IMAGES.joinpath("prayers", "magic.png"),
            "melee": imsearch.BOT_IMAGES.joinpath("prayers", "melee.png"),
            "missiles": imsearch.BOT_IMAGES.joinpath("prayers", "missiles.png"),
        }
        image = images.get(type)
        if image:
            self.open_tab(5)
            img = imsearch.search_img_in_rect(image, self.bot.win.control_panel)
            if img:
                # Define the region of the screen to search (left, top, width, height)
                region = self.bot.win.control_panel.to_dict().values()

                # Take a screenshot of the defined region
                screenshot = pyautogui.screenshot(region=region)

                # Define the color to search for (RGB tuple)
                color_to_search = (194, 171, 109)  # Example: Red color

                # Iterate over each pixel in the screenshot to search for the color
                for x in range(screenshot.width):
                    for y in range(screenshot.height):
                        pixel_color = screenshot.getpixel((x, y))
                        if pixel_color == color_to_search:
                            # Color found at coordinates (x, y) relative to the defined region
                            self.bot.mouse.move_to(img.random_point(), mouseSpeed="fastest")
                            self.bot.mouse.click()
                            self.open_tab(3)
                            return True
                return True

    def open_tab(self, number: int):
        """Open tab on controlpanel
        :param int number: A number representing which tab to open
        """
        if number == self.current_tab:
            return False
        self.current_tab = number
        self.bot.mouse.move_to(self.bot.win.cp_tabs[number].random_point())
        self.bot.mouse.click()
        self.bot.log_msg(f"Opening tab {number}")
        return True

    def is_chat(self, text: str, colr=clr.BLACK):
        """Check if text is in chat window
        :param str text: A string to search inside the chat window
        :param clr color: A clr object representing the font color
        """
        if ocr.find_text(text, rect=self.bot.win.chat, font=ocr.QUILL_8, color=colr):
            self.bot.log_msg(f"{text} is found in chat")
            return True
        return False

    def teleport_to_bank(self):
        """Teleports to crafting bank"""
        self.open_tab(4)
        current_location = self.bot.api_m.get_player_position()
        self.click_cape()
        while current_location == self.bot.api_m.get_player_position():
            time.sleep(2 / 10)
        self.open_tab(3)
        return True

    def click_cape(self):
        if self.current_tab == 4 and self.locate_cape():
            while not self.bot.mouseover_text("Teleport", color=clr.OFF_WHITE):
                self.bot.mouse.move_to(self.cape_slot.random_point())
            self.bot.mouse.click()

    def locate_cape(self):
        if not self.cape_slot:
            result = self.get_RLobject_by_object(
                self.bot.win.cp_tabs[0], offset_x=55, offset_y=81, columns=1, margin=1, extra_margin_left=5, extra_margin_right=5
            )
            if result != []:
                self.cape_slot = result[0]
                return True
            return False
        return True

    def test(self, object, offset_x=0, offset_y=0, extra_margin_left=0, extra_margin_right=0, columns=8, margin=5):
        result = self.get_pixels_by_object(object, False, offset_x, offset_y, extra_margin_left, extra_margin_right, columns, margin)
        print(object)
        self.create_screenshot(result)

    def find_highest(self, current_highest, high, color):
        numbers = list(range(current_highest, high))
        numbers.reverse()
        for number in numbers:
            # if number != 5:
            #     continue
            self.bot.log_msg(f"Finding number: {number}")
            rects = self.bot.get_all_tagged_in_rect(self.bot.win.game_view, color=color)

            for rect in rects:
                rectangle = Rectangle(int(rect._x_min) - 30, int(rect._y_max) - 30, int(rect._width) + 60, int(rect._height) + 60)

                try:
                    glade = ocr.find_text(str(number), rect=rectangle, font=ocr.PLAIN_11, color=color)
                except ValueError:
                    print("Failed")
                    continue

                if glade and current_highest <= number:
                    self.bot.log_msg(f"Found number: {number}")
                    return number, glade
        return False, False

    def get_RLobject_by_object(self, object, bankslots=False, offset_x=0, offset_y=0, extra_margin_left=0, extra_margin_right=0, columns=8, margin=5):
        coords = object.to_dict()
        print(columns)
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
        coords = object.to_dict()
        print(columns)
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

    def get_RLobject_by_object(self, object, bankslots=False, offset_x=0, offset_y=0, extra_margin_left=0, extra_margin_right=0, columns=8, margin=5):
        coords = object.to_dict()
        print(columns)
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

    def create_screenshot(self, pixel_coordinates):
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
        self.start_time = time.perf_counter()

    def performance_end(self):
        self.end_time = time.perf_counter()
        elapsed_time_ms = (self.end_time - self.start_time) * 1000  # Convert to milliseconds
        print(f"Time taken full: {elapsed_time_ms: .2f} ms")
