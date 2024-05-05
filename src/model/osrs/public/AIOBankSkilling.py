import time

import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class AIOBankSkilling(OSRSBot):
    """
    QuBerto AIOBankSkilling
    Do almost any bankstanding skill with this script.

    Required plugins:
    Morg HTTP client.

    How to setup:
    1. Make sure your ingredients are placed in the first spots in your bank.
    2. Take 1 of each ingredient out of the bank, for example 1 herb, and 1 potion.
    3. Start script.
    """

    def __init__(self):
        bot_title = "AIO Bank Skilling"
        description = "Start with one of all your ingredients."

        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 100
        self.action = "space"

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("interface_action", "Action in the interface", "space")

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]

            elif option == "interface_action":
                self.action = "space"
                if options[option]:
                    self.action = options[option]
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def pre_loop(self):
        excluded = [ids.KNIFE, ids.GLASSBLOWING_PIPE]
        inv = self.api_m.get_inv()
        self.excluded = [i for i, inventory_slot in enumerate(inv) if inventory_slot["id"] in excluded]
        self.num_ingredients = len(inv)

        self.item_1 = inv[0]["id"]
        if self.num_ingredients > 1:
            self.item_2 = inv[1]["id"]

        if len(self.excluded) > 0:
            self.num_ingredients -= 1

    def main_loop(self):
        self.api_m = MorgHTTPSocket()
        self.failed_before = False
        start_time = time.time()
        self.pre_loop()
        while time.time() - start_time < self.running_time * 60:
            if not self.main():
                if self.failed_before:
                    self.log_msg("Failed last time, stopping.")
                    break
                self.failed_before = True
            else:
                self.failed_before = False
            self.update_progress((time.time() - start_time) / self.running_time * 60)
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def main(self):
        self.open_bank()
        self.click_deposit_all()
        withdraw = []

        for i in range(1, self.num_ingredients + 1):
            withdraw.append({"slot": i, "clicks": 1})
        print(withdraw)
        self.withdraw_items(withdraw, check=False)

        if not self.bank_close(full_inv=True):
            return False
        self.get_item(self.item_1)
        self.get_item(self.item_2, last=True, move_first=True)

        if not self.do_interface_action(self.action):
            return False
        self.mouse.move_to(self.win.game_view.random_point())

        if self.excluded:
            if not self.wait_till_inv_out_of([self.item_2]):
                return False

            return True
        else:
            if not self.wait_till_inv_out_of([self.item_1, self.item_2]):
                return False
            return True
