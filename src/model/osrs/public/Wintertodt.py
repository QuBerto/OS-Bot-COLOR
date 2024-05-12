import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.ocr as ocr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Point, Rectangle


class OSRSWintertodt(OSRSBot):
    def __init__(self):
        bot_title = "QuBerto Wintertodt"
        description = "QuBerto Wintertodt"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 100

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            elif option == "multi_select_example":
                self.log_msg(f"Multi-select example: {options[option]}")
            elif option == "menu_example":
                self.log_msg(f"Menu example: {options[option]}")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.`
          operator to access their functions.
        """
        # Setup APIs
        self.api_m = MorgHTTPSocket()
        # api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.
            # print(self.test(self.win.cp_tabs[0],margin=0, columns=1))
            self.find_game_status()
            self.debug_wintertodt()
            time.sleep(1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def find_game_status(self):
        text = (ocr.find_text("Wintertodt", self.win.game_view, font=ocr.PLAIN_11, color=clr.BLACK))[0]
        new_rectangle = Rectangle(text.left, text.top, 150, text.height)

        extract = ocr.extract_text(new_rectangle, ocr.PLAIN_11, color=clr.BLACK, exclude_chars=(self.filter_only_numbers().replace("%", "")))

        if "%" in extract:
            self.game_status = "running"
            self.wintertodt_energy = extract.replace("%", "")
            self.waiting_time = 0
        else:
            self.game_status = "waiting"
            self.waiting_time = extract
            self.wintertodt_energy = 0

        if roots := self.api_m.get_inv_item_indices(ids.BRUMA_ROOT):
            self.has_roots = True
            self.roots = roots
        else:
            self.has_roots = False
            self.roots = []

        if kindling := self.api_m.get_inv_item_indices(ids.BRUMA_KINDLING):
            self.has_kindling = True
            self.kindling = kindling
        else:
            self.has_kindling = False
            self.kindling = []
        self.get_inv_status()

    def get_inv_status(self):
        inv = self.api_m.get_inv()
        self.inv_length = len(inv)
        self.roots = []
        self.kindling = []
        self.food = []
        self.hammer = []
        self.knife = []
        self.tinderbox = []
        self.food = []
        for item in inv:
            if item["id"] == ids.BRUMA_KINDLING:
                self.kindling.append(item["index"])
            elif item["id"] == ids.BRUMA_ROOT:
                self.roots.append(item["index"])
            elif item["id"] == ids.TINDERBOX:
                self.tinderbox.append(item["index"])
            elif item["id"] == ids.HAMMER:
                self.hammer.append(item["index"])
            elif item["id"] == ids.KNIFE:
                self.knife.append(item["index"])
            elif item["id"] in [ids.CAKE, ids.SLICE_OF_CAKE]:
                self.food.append(item["index"])

    def decide_task(self):
        while self.game_status == "waiting":
            time.sleep(0.5)
        if self.game_status == "running":
            pass

    def debug_wintertodt(self):
        print(self.game_status)
        print(self.wintertodt_energy)
        print(self.waiting_time)
        print(self.has_kindling)
        print(self.kindling)
        print(self.has_roots)
        print(self.roots)
