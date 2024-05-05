import time

import utilities.api.item_ids as ids
import utilities.color as clr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSTTT(OSRSBot):
    def __init__(self):
        """
        Initializes the Two Tick Teaks bot.
        """
        bot_title = "QuBerto Teaks"
        description = "Two Tick Teaks"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1

    def create_options(self):
        """
        Creates options for the bot, such as running time.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        """
        Saves the options set by the user.

        Args:
            options (dict): Dictionary containing user options.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]

        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        """
        The main loop of the bot that runs until the specified running time is reached.
        """
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        start_time = time.time()
        end_time = self.running_time * 60
        self.current_game_tick = 0
        self.failed_times = 0
        time.sleep(self.api_s.gameTick)
        while time.time() - start_time < end_time:
            if len(self.api_m.get_inv()) == 28:
                self.clear_logs()
            self.start_sequence()
            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def start_sequence(self):
        """
        Performs the sequence of actions required for the bot.
        """
        inv_count = len(self.api_m.get_inv())
        if ground := self.get_nearest_tag(clr.YELLOW):
            self.mouse.move_to(ground.random_point(), mouseSpeed="fastest")

        if self.api_s.get_game_tick() - self.current_game_tick > 1:
            while self.api_m.get_is_in_combat():
                time.sleep(1 / 6)
            self.log_msg(f"{self.api_s.get_game_tick()} | Start sequence ")
            self.log_msg("-----------------------------")
            self.failed_times = 0
            self.mouse.click()
        else:
            while self.current_game_tick == self.api_s.get_game_tick():
                time.sleep(1 / 6)
            self.log_msg(f"{self.api_s.get_game_tick()} | Tree tick", overwrite=True)
            self.mouse.click()
        self.current_game_tick = self.api_s.get_game_tick()
        if tree := self.get_nearest_tag(clr.BLUE) or self.get_nearest_tag(clr.GREEN):
            self.mouse.move_to(tree.random_point(), mouseSpeed="fastest")
        else:
            return False
        while self.current_game_tick == self.api_s.get_game_tick():
            time.sleep(1 / 20)
        self.mouse.click()
        self.current_game_tick = self.api_s.get_game_tick()
        self.log_msg(f"{self.current_game_tick} | Ground tick", overwrite=True)
        new_inv_count = len(self.api_m.get_inv())
        if new_inv_count == inv_count:
            self.failed_times = self.failed_times + 1
        else:
            self.failed_times = 0
        if self.failed_times >= 5:
            self.log_msg(f"{self.current_game_tick} | Failed too many times, resetting")
            time.sleep(2)
            self.current_game_tick = 0

    def clear_logs(self):
        """
        Clears logs from the inventory.
        """
        self.log_msg(f"{self.api_s.get_game_tick()} | Dropping logs", overwrite=True)
        if logs := self.api_m.get_inv_item_indices(ids.TEAK_LOGS):
            for log in logs:
                self.mouse.move_to(self.win.inventory_slots[log].random_point(), mouseSpeed="insane")
                self.mouse.click()
