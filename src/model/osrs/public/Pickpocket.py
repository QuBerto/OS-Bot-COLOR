import time

import utilities.api.item_ids as ids
import utilities.color as clr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSPickpocket(OSRSBot):
    """
    Two Tick Trees

    Setup same as in this guide:
    https://www.youtube.com/watch?v=LnJJ0RuUPws

    1. Import RUneLite Profile
    2. Stand on yellow marked tile
    3. Start script.
    """

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
        time.sleep(self.api_s.gameTick)
        while time.time() - start_time < end_time:
            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
