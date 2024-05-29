import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.walker import Walker


class OSRSMLM(OSRSBot):
    def __init__(self):
        bot_title = "MLM"
        description = ""
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 100
        self.take_breaks = False
        self.paydirt = 0

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        # self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])

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
            if int(self.read_space()) <= 28 + 28 and len(self.api_m.get_inv()) < 15:
                self.bank()
            if len(self.api_m.get_inv()) >= 28:
                self.deposit()
            else:
                self.mine()
        self.update_progress(1)
        self.log_msg("test")

    def mine(self):
        while len(self.api_m.get_inv()) < 28:
            if self.get_nearest_tag(clr.GREEN):
                if not self.click_tag_if_exists(clr.GREEN, "Mine", check_for_red=True):
                    try:
                        self.update("Walk to mine")
                        walker = Walker(self)
                        walker.walk_to((3747, 5648))
                    except StopIteration:
                        self.update("Walk to mine BACKUP")
                        walker = Walker(self)
                        path = walker.get_api_walk_path((3746, 5650), (3750, 5671), "dax")
                        walker.walk(path, (3750, 5671))
                self.update("Mining")
                while not self.api_m.get_is_player_idle():
                    time.sleep(4 / 10)
                # self.wait_game_ticks(1)
                time.sleep(6 / 10)
                while not self.api_m.get_is_player_idle():
                    time.sleep(4 / 10)
                self.update("Mining")
            else:
                self.update("Walk to mine")
                walker = Walker(self)
                walker.walk_to((3747, 5648))

    def deposit(self):
        paydirt_count = len(self.api_m.get_inv_item_indices(ids.PAYDIRT))
        try:
            self.update("Walk to deposit")
            walker = Walker(self)
            walker.walk_to((3750, 5671))
        except StopIteration:
            self.update("Walk to deposit BACKUP")
            walker = Walker(self)
            path = walker.get_api_walk_path((3746, 5650), (3750, 5671), "dax")
            walker.walk(path, (3750, 5671))
        while not self.click_tag_if_exists(clr.BLUE, "Deposit", check_for_red=True):
            pass
        self.update("Walk till paydirt is deposited")
        while self.api_m.get_inv_item_indices(ids.PAYDIRT):
            time.sleep(0.1)
        self.paydirt += paydirt_count
        if int(self.read_space()) <= 28 + 28:
            self.update("Start bank")
            self.bank()

    def read_space(self):
        return ocr.extract_text(self.win.game_view, ocr.PLAIN_11, clr.OFF_WHITE, exclude_chars=self.all_characters_except_digits)

    def bank(self):
        while int(self.read_space()) < 100:
            self.update("Walk to sack")
            walker = Walker(self)
            walker.walk_to((3749, 5659))
            self.update("Click sack")
            while not self.click_tag_if_exists(clr.YELLOW, "Search", check_for_red=True):
                pass
            self.update("Waiting on ores")
            while not self.api_m.get_inv_item_indices([ids.COAL, ids.GOLD_ORE, ids.MITHRIL_ORE, ids.ADAMANTITE_ORE, ids.RUNITE_ORE]):
                time.sleep(1 / 10)
            self.update("Walk to bank")
            walker = Walker(self)
            walker.walk_to((3760, 5666))
            self.update("Open bank")
            while not self.open_bank():
                pass
            self.update("click_deposit_all")
            self.click_deposit_all()
            self.update("bank_close")
            self.bank_close()

    def update(self, action: str = "None"):
        self.action = action
        self.log_msg(
            f"Action: {self.action} | Paydirt: {self.paydirt + len(self.api_m.get_inv_item_indices(ids.PAYDIRT))}",
            overwrite=True,
        )
