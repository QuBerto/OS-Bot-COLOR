import time

import requests

import utilities.api.highscores as hs
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot


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
        self.running_time = 300
        self.take_breaks = True
        self.max_coins = 20
        self.coins = 0
        self.success = 0
        self.current_success = 0
        self.current_coin_pouch = 0
        self.failed = 0
        self.max_hp = hs.HighScores("erva hc").get_skill_level(hs.HighScores.SKILLS[4])
        self.current_coins = 0
        self.food = [ids.CAKE, ids.SLICE_OF_CAKE, ids._23_CAKE]
        self.coin_pouch_img = imsearch.BOT_IMAGES.joinpath("items", "coin_pouch.png")
        self.food_imgs = [
            imsearch.BOT_IMAGES.joinpath("items", "Salmon.png"),
            # imsearch.BOT_IMAGES.joinpath("items", "slice_of_cake.png"),
            # imsearch.BOT_IMAGES.joinpath("items", "23cake.png"),
            # imsearch.BOT_IMAGES.joinpath("items", "cake.png")
        ]
        self.coins_imgs = [
            imsearch.BOT_IMAGES.joinpath("items", "coins_25.png"),
            imsearch.BOT_IMAGES.joinpath("items", "coins_250.png"),
            imsearch.BOT_IMAGES.joinpath("items", "coins_1000.png"),
            imsearch.BOT_IMAGES.joinpath("items", "coins_10000.png"),
        ]

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

    def update_totals(self):
        self.performance_start()
        self.current_coins = self.coins + self.get_coins_count()
        self.current_success = self.get_coin_pouch_count() + self.success
        self.current_coin_pouch = self.get_coin_pouch_count()
        self.performance_end()

    def main_loop(self):
        self.start_time = time.time()
        self.end_time = self.running_time * 60
        self.action = ""
        self.update()
        while time.time() - self.start_time < self.end_time:
            self.update_totals()
            self.update("Start")
            if self.get_hp() > self.max_hp:
                self.max_hp = self.get_hp()
            if self.get_hp() < 10:
                self.eat()
                continue
            if self.current_coin_pouch > self.max_coins / 2 or (self.current_coin_pouch > self.max_coins and rd.random_chance(probability=0.5)):
                self.update("Click pouch")
                self.success += self.current_coin_pouch
                self.click_item_image(self.coin_pouch_img, "Open")
            self.update("Find knigth")
            knights = self.find_color(self.win.game_view, "new_green")
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
                if not self.mouse.click(check_red_click=True):
                    self.update("Red click failed")
                    continue

                start_tick = self.get_tick()
                start_cash = self.current_coin_pouch
                start_health = self.get_hp()
                while start_tick + 1 > self.get_tick():
                    if start_cash != self.get_coins_count():
                        self.update("Pickpocket Successfull")

                        time.sleep(rd.random.randint(800, 1200) / 1000)

                    elif start_health > self.get_hp():
                        time.sleep(0.5)
                        self.failed += 1
                        self.update("Pickpocket Failed")
                        if self.get_hp() < 10:
                            continue
                        self.wait_game_ticks(5)
                        break

            position = self.get_player_position()
            if (position[0] > 2655 or position[0] < 2653) or (position[1] > 3287 or position[1] < 3283):
                self.log_msg("[Stopping] Knight moved out of position")
                break
            self.update("End")
        self.update_progress(1)
        self.log_msg("Finished.")

    def update(self, action: str = "None"):
        self.action = action
        self.log_msg(
            f"Success: {self.current_success} | Coins: {self.current_coins} | Last action: {self.action}",
            overwrite=True,
        )
        self.update_progress((time.time() - self.start_time) / self.end_time)

    def eat(self):
        food = self.get_food()
        while food and self.get_hp() < self.max_hp - 6:
            self.update("Eating")
            food = self.get_food()
            if food:
                self.click_inv_item(food[0], "Eat", max_tries=1)
            self.wait_game_ticks(3)
        if self.get_hp() < self.max_hp - 6:
            self.update("Banking")
            self.bank()
            self.update("Finished Banking")

    def bank(self):
        while not self.open_bank():
            pass
        self.update("Bank opened")
        self.coins += self.get_coins_count()
        self.update("Click deposit")
        self.click_deposit_all()
        self.update("Withdraw first")
        self.withdraw_first()
        self.update("Bank close")
        self.bank_close()
        time.sleep(1)
        if not self.get_food():
            self.update("Could not withdraw food")
            self.stop()

    def get_food(self):
        for food_img in self.food_imgs:
            slots = self.find_inventory_slots(food_img)
            if slots:
                return slots
        return []

    def get_coin_pouch_count(self):
        item = self.find_coin_pouch()
        if item:
            return self.extract_number_inventory(item[0])
        return 0

    def get_coins_count(self):
        item = self.find_coins()
        if item:
            return self.extract_number_inventory(item[0])
        return 0

    def find_coin_pouch(self):
        return self.find_inventory_slots(self.coin_pouch_img)

    def find_coins(self):
        for coin_img in self.coins_imgs:
            slots = self.find_inventory_slots(coin_img)
            if slots:
                return slots
        return []

    def get_player_hitpoints(self, player_name: str) -> int:
        url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" + player_name

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data for player {player_name}")

        data = response.text.split("\n")

        # The hitpoints data is on the 10th line (index 9) for OSRS hiscore (rank, level, XP)
        hitpoints_data = data[4].split(",")

        if len(hitpoints_data) < 2:
            raise Exception(f"Unexpected data format for player {player_name}")

        hitpoints_level = int(hitpoints_data[1])

        return hitpoints_level
