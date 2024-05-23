import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.ocr as ocr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject
from utilities.walker import Walker


class OSRSMLM(OSRSBot):
    def __init__(self):
        bot_title = "MLM"
        description = (
            "This bot power-chops wood. Position your character near some trees, tag them, and press Play.\nTHIS SCRIPT IS AN EXAMPLE, DO NOT USE LONGTERM."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 100
        self.take_breaks = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup API
        self.api_m = MorgHTTPSocket()
        self.mouse.click()
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.main()
            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.__logout("Finished.")

    def main(self):
        if int(self.read_space()) <= 28 + 28:
            self.bank()
        if len(self.api_m.get_inv()) >= 28:
            self.deposit()
        else:
            self.mine()

    def mine(self):
        while len(self.api_m.get_inv()) < 28:
            if self.get_nearest_tag(clr.GREEN):
                self.click_tag_if_exists(clr.GREEN, "Mine", check_for_red=True)
                while not self.api_m.get_is_player_idle():
                    time.sleep(4 / 10)
            else:
                walker = Walker(self)
                walker.walk_to((3747, 5649))

    def deposit(self):
        walker = Walker(self)
        walker.walk_to((3749, 5671))
        while not self.click_tag_if_exists(clr.BLUE, "Deposit", check_for_red=True):
            pass
        while self.api_m.get_inv_item_indices(ids.PAYDIRT):
            time.sleep(0.1)
        if int(self.read_space()) <= 28 + 28:
            self.bank()

    def read_space(self):
        return ocr.extract_text(self.win.game_view, ocr.PLAIN_11, clr.OFF_WHITE, exclude_chars=self.all_characters_except_digits)

    def bank(self):
        while int(self.read_space()) < 100:
            while not self.click_tag_if_exists(clr.YELLOW, "Search", check_for_red=True):
                pass
            while not self.api_m.get_inv_item_indices([ids.COAL, ids.GOLD_ORE, ids.MITHRIL_ORE, ids.ADAMANTITE_ORE, ids.RUNITE_ORE]):
                time.sleep(1 / 10)
            self.open_bank()
            self.click_deposit_all()
            self.bank_close()
