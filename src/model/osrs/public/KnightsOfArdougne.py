import time

import pyautogui

import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSKnight(OSRSBot):
    """
    QuBerto Ardy knight bot pickpocket ardy knights and open coinpouches.
    Health is totally ignored, make sure you can survive with normal regeneration.

    No RuneLite profile available.

    How to setup:
    1. Set left click to pickpocket.
    2. Mark the knight in the corner of the ardy south bank Cyan.
    3. Start script.
    """

    def __init__(self):
        bot_title = "Quberto Knights"
        description = "Knight of Ardougne bot"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 10
        self.take_breaks = True
        self.max_coins = 20

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup APIs
        api_m = MorgHTTPSocket()
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        # Get the path to the image
        coinpouch_img = imsearch.BOT_IMAGES.joinpath("items", "coin_pouch.png")

        if knight := self.get_nearest_tag(clr.CYAN):
            knight.distance_from_rect_center()
            self.mouse.move_to(knight.random_point(), mouseSpeed="fastest")
        while time.time() - start_time < end_time:
            # 5% of changing position
            coinpouch = imsearch.search_img_in_rect(coinpouch_img, self.win.control_panel)
            if api_m.get_inv_item_stack_amount(22531) > self.max_coins / 2 and rd.random_chance(probability=0.03) and coinpouch:
                self.mouse.move_to(coinpouch.random_point(), mouseSpeed="fastest")
                self.mouse.click()
                self.log_msg("[Process] Clicking coinpouch")

            if knight := self.get_nearest_tag(clr.CYAN):
                x, y = pyautogui.position()

                if x < knight.center()[0] - 15 or x > knight.center()[0] + 15:
                    self.mouse.move_to(knight.random_point(), mouseSpeed="fastest")
                    self.log_msg("[Proccess] Moving closer to the middle")
                if y < knight.center()[1] - 15 or y > knight.center()[1] + 15:
                    self.mouse.move_to(knight.random_point(), mouseSpeed="fastest")
                    self.log_msg("[Proccess] Moving closer to the middle")

                self.mouse.click()
                time.sleep(3 / 10)

            x = api_m.get_player_position()[0]
            y = api_m.get_player_position()[1]
            if api_m.get_inv_item_stack_amount(22531) > self.max_coins and rd.random_chance(probability=0.5):
                if coinpouch := imsearch.search_img_in_rect(coinpouch_img, self.win.control_panel):
                    self.mouse.move_to(coinpouch.random_point(), mouseSpeed="fastest")
                    self.log_msg("[Process] Clicking coinpouch")
                self.mouse.click()

            if x > 2655 or x < 2653:
                self.log_msg("[Stopping] Knight moved out of position")
                break
            if y > 3287 or y < 3287:
                # break
                self.log_msg("[Stopping] Knight moved out of position")
                break

            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.log_msg("Finished.")
