import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSKnight(OSRSBot):
    """
    QuBerto Ardy knight bot pickpocket ardy knights and open coinpouches.
    Health is totally ignored, make sure you can survive with normal regeneration.

    No RuneLite profile available.

    How to setup:
    1. Set left click to pickpocket.
    2. Mark the knight in the corner of the ardy south bank Green.
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
        self.coins = 0
        self.success = 0
        self.failed = 0
        self.food = [ids.CAKE, ids.SLICE_OF_CAKE, ids._23_CAKE]

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_number_option("open_at", "When to open pouches max?", 28)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "open_at":
                self.max_coins = int(options[option])
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.start_time = time.time()
        self.end_time = self.running_time * 60
        self.action = ""
        self.update()
        while time.time() - self.start_time < self.end_time:
            self.update("Start")
            if self.get_hp() < 10:
                self.eat()
                continue
            if self.api_m.get_inv_item_stack_amount(ids.COIN_POUCH_22531) > self.max_coins / 2 or (
                self.api_m.get_inv_item_stack_amount(ids.COIN_POUCH_22531) > self.max_coins and rd.random_chance(probability=0.5)
            ):
                self.update("Click pouch")
                self.click_item([ids.COIN_POUCH_22531], "Open")
            self.update("Find knigth")
            knights = self.find_color(self.win.game_view, "custom_green")
            if knights:
                self.update("Found knigth")
                knight = knights[0]
                self.update("Mouse move to")

                if not self.mouseover_text("Pick", clr.OFF_WHITE):
                    self.mouse.move_to(knight.random_point())
                    if not self.mouseover_text("Pick", clr.OFF_WHITE):
                        self.update("Pickpocket not found")
                        continue
                self.update("Mouse Click")
                start_health = self.get_hp()
                if not self.mouse.click(check_red_click=True):
                    self.update("Red click failed")
                    continue

                start_tick = self.api_s.get_game_tick()
                while start_tick + 1 > self.api_s.get_game_tick():
                    ani = self.api_m.get_animation()
                    if ani == 881:
                        time.sleep(0.5)
                        self.update("Pickpocket Successfull")
                        self.success += 1
                        while ani == 881:
                            ani = self.api_m.get_animation()
                            pass
                        break

                    elif start_health > self.get_hp():
                        time.sleep(0.5)
                        self.failed += 1
                        self.update("Pickpocket Failed")
                        if self.get_hp() < 10:
                            continue
                        self.wait_game_ticks(5)
                        break

            position = self.api_m.get_player_position()
            if (position[0] > 2655 or position[0] < 2653) or (position[1] > 3287 or position[1] < 3283):
                self.log_msg("[Stopping] Knight moved out of position")
                break
            self.update("End")
        self.update_progress(1)
        self.log_msg("Finished.")

    def update(self, action: str = "None"):
        self.action = action
        self.log_msg(
            (
                f"Success: {self.success} | Fails: {self.failed} | Coins: {self.coins + self.api_m.get_inv_item_stack_amount(ids.coins)} |"
                f" Last action: {self.action}"
            ),
            overwrite=True,
        )
        self.update_progress((time.time() - self.start_time) / self.end_time)

    def eat(self):
        food = self.api_m.get_inv_item_indices(self.food)
        while food and self.get_hp() < self.api_m.get_skill_level("Hitpoints") - 6:
            self.update("Eating")
            food = self.api_m.get_inv_item_indices(self.food)
            self.click_item(self.food, "Eat", max_tries=1)
            self.wait_game_ticks(3)
        if self.get_hp() < self.api_m.get_skill_level("Hitpoints") - 6:
            self.update("Banking")
            self.bank()
            self.update("Finished Banking")

    def bank(self):
        while not self.open_bank():
            pass
        self.update("Bank opened")
        self.coins += self.api_m.get_inv_item_stack_amount(ids.coins)
        self.update("Click deposit")
        self.click_deposit_all()
        self.update("Withdraw first")
        self.withdraw_first()
        self.update("Bank close")
        self.bank_close()
        if not self.api_m.get_inv_item_indices(self.food):
            self.update("Could not withdraw food")
            self.stop()
