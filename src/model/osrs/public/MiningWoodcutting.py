import pprint
import time

import pyautogui as pag
import pytweening

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.ocr as ocr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSForester(OSRSBot):
    def __init__(self):
        bot_title = "Quberto Auto Woodcutter"
        description = "Woodcutting aio"
        super().__init__(bot_title=bot_title, description=description)
        self.combination = 3
        self.take_breaks = 1
        self.running_time = 360
        self.name_clues = []
        self.timeout = 30
        self.type_log = ids.WILLOW_LOGS
        self.clues = ["beginner", "easy", "medium", "hard", "elite"]
        self.ores = ["COPPER", "TIN", "IRON", "SILVER", "GOLD", "MITHRIL", "ADMANT", "RUNE"]
        self.logs = ["LOGS", "OAK", "WILLOW", "MAPLE", "YEW", "MAGIC", "REDWOOD"]
        self.how_many = ["3 (Y/B/R)", "2 (Y/B)", "1 (Y)"]
        self.items_to_click = [ids.BIRD_NEST_5074, ids.BIRD_NEST_22798]
        self.items_to_drop = [
            ids.GOLD_AMULET,
            ids.ACORN,
            ids.APPLE_TREE_SEED,
            ids.WILLOW_SEED,
            ids.BANANA_TREE_SEED,
            ids.ORANGE_TREE_SEED,
            ids.CURRY_TREE_SEED,
            ids.MAPLE_SEED,
            ids.PINEAPPLE_SEED,
            ids.CALQUAT_TREE_SEED,
            ids.TEAK_SEED,
            ids.MAHOGANY_SEED,
            ids.GOLD_RING,
            ids.SAPPHIRE_RING,
            ids.EMERALD_RING,
            ids.RUBY_RING,
        ]
        self.reorder_items = [
            ids.BIRD_NEST_5075,
            ids.BIRD_NEST_22798,
            ids.CLUE_NEST_BEGINNER,
            ids.CLUE_NEST_HARD,
            ids.CLUE_NEST_MEDIUM,
            ids.CLUE_BOTTLE_EASY,
            ids.CLUE_NEST_ELITE,
        ]
        self.logs = ids.MAPLE_LOGS

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("type_log", "What logs?", self.logs + self.ores)
        self.options_builder.add_dropdown_option("combination", "How many trees?", self.how_many)
        self.options_builder.add_checkbox_option("pick_up_birdnests", "Pick up bird nests?", ["Yes"])
        self.options_builder.add_checkbox_option("pick_up_cluenests", "What Clues nest?", self.clues)
        self.options_builder.add_slider_option("max_timeout", "How long till despawn?", 1, 300)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", ["Yes"])

    def save_options(self, options: dict):
        self.pick_up_birdnests = False
        self.pick_up_clues = []
        self.name_clues = []

        for option in options:
            if option == "running_time":
                self.running_time = options[option]

            elif option == "pick_up_birdnests" and "Yes" in options[option]:
                self.pick_up_birdnests = True

            elif option == "pick_up_cluenests":
                for clue in options[option]:
                    id_clue = getattr(ids, "CLUE_NEST_" + clue.upper())
                    name_clue = "Clue nest (" + clue + ")"
                    self.pick_up_clues.append(id_clue)
                    self.name_clues.append(name_clue)

            elif option == "combination":
                if options[option] == "3 (Y/B/R)":
                    self.combination = 3
                elif options[option] == "2 (Y/B)":
                    self.combination = 2
                elif options[option] == "1 (Y)":
                    self.combination = 1
                self.log_msg(f"How many ores: {self.combination}")

            elif option == "type_log":
                self.ore_name = options[option]
                if options[option] == "IRON":
                    self.type_log = getattr(ids, options[option] + "_ORE")
                elif "LOGS" != options[option]:
                    self.type_log = getattr(ids, options[option] + "_LOGS")
                else:
                    self.type_log = getattr(ids, options[option])
                self.log_msg(f"drop_clues: {self.type_log}")
                self.items_to_drop.append(self.type_log)

            elif option == "take_breaks":
                self.take_breaks = False
                if "Yes" in options[option]:
                    self.take_breaks = True

                self.log_msg(f"take_breaks: {self.take_breaks}")

            elif option == "max_timeout":
                self.timeout = options[option]

            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        if self.pick_up_birdnests:
            self.name_clues.append("Bird nest")
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def remove_dropped(self, copy, droplist):
        list_copy = copy  # self.gems.copy()  # Create a copy of self.gems

        # Remove gems present in self.drop_gems from the copy
        for drop in droplist:
            if drop in list_copy:
                list_copy.remove(drop)

        return list_copy

    def main_loop(self):
        self.api_m = MorgHTTPSocket()

        self.latest_blue = False
        self.latest_red = False
        self.latest_yellow = False
        self.did_pre_move = False

        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            found_tree = False
            if self.handle_tree(color=clr.YELLOW, nice_name="Yellow"):
                found_tree = True
            if not found_tree and (self.combination == 3 or self.combination == 2) and self.handle_tree(color=clr.BLUE, nice_name="Blue"):
                found_tree = True
            if not found_tree and self.combination == 3 and self.handle_tree(color=clr.RED, nice_name="Red"):
                found_tree = True

            if not found_tree and rd.random_chance(probability=0.1):
                self.empty_item(self.type_log, 20)
                pink = self.get_nearest_tag(color=clr.PINK)
                print(pink)
                if not pink:
                    self.get_all_tagged_in_rect(rect=self.win.minimap, color=clr.PINK)

            if self.name_clues:
                self.log_msg(self.name_clues)
                if self.pick_up_loot(self.name_clues):
                    time.sleep(2)

    def handle_tree(self, color, nice_name):
        self.nice_name = nice_name
        self.handle_drop_logs()
        return self.click_tree(color)

    def empty_item(self, item_list, length=0):
        item = self.api_m.get_inv_item_indices(item_list)
        if len(item) > length:
            self.log_msg(f"Dropping items id: {item_list}")
            self.drop(item)
            return True
        return False

    def handle_drop_logs(self):
        emptied_inv = False
        if self.api_m.get_is_inv_full():
            self.empty_item(self.items_to_drop)
            time.sleep(1 / 2)
            self.reorder()
            emptied_inv = True
        self.check_inv()
        return emptied_inv

    def check_inv(self):
        items = self.api_m.get_inv_item_indices(self.items_to_click)
        if items:
            self.click_inventory_item(items[0])
            time.sleep(2)

    def click_inventory_item(self, item_location):
        self.mouse.move_to(self.win.inventory_slots[item_location].random_point(), mouseSpeed="insane")
        self.mouse.click()

    def click_tree(self, color):
        roots = self.get_nearest_tag(color=clr.GREEN)
        if roots:
            self.handle_roots(roots)

        else:
            tree = self.get_nearest_tag(color=color)
            if tree:
                self.log_msg("Clicking " + self.nice_name + " tag")

                # Set maximum number of attempts
                max_attempts = 5
                # Initialize variables
                attempts = 0

                mouseover = self.mouseover_text(["Chop", "Mine"], color=clr.OFF_WHITE)
                self.mouse.move_to(tree.random_point())
                while not mouseover and attempts < max_attempts:
                    self.mouse.move_to(tree.random_point())
                    mouseover = self.mouseover_text(["Chop", "Mine"], color=clr.OFF_WHITE)
                    attempts += 1

                if mouseover:
                    self.mouse.click()
                else:
                    # Handle case when mouseover fails
                    self.log_msg("Mouseover failed after " + str(max_attempts) + " attempts.")

                # Set maximum number of attempts

                start_time = time.time()

                tree = self.get_nearest_tag(color=color)
                while tree and time.time() - start_time < self.timeout:
                    tree = self.get_nearest_tag(color=color)
                    if self.handle_drop_logs():
                        return True

                    roots = self.get_nearest_tag(color=clr.GREEN)
                    if roots:
                        self.handle_roots(roots)
                    tree = self.get_nearest_tag(color=color)

                if self.take_breaks and rd.random_chance(0.004):
                    self.take_break(1, 25)
                return True
            return False

    def handle_roots(self, roots):
        while roots:
            self.log_msg("Clicking Roots tag")

            max_attempts = 5
            # Initialize variables
            attempts = 0
            self.mouse.move_to(roots.random_point())
            mouseover = self.mouseover_text("Chop", color=clr.OFF_WHITE)

            while not mouseover and attempts < max_attempts:
                self.mouse.move_to(roots.random_point())
                mouseover = self.mouseover_text("Chop", color=clr.OFF_WHITE)
                attempts += 1
            if mouseover:
                self.mouse.click()
            else:
                # Handle case when mouseover fails
                self.log_msg("Mouseover failed after " + str(max_attempts) + " attempts.")
            start_time = time.time()
            mouseover = self.mouseover_text("Chop", color=clr.OFF_WHITE)
            found = True
            attempts = 0
            while found and time.time() - start_time < 60:
                roots = self.get_nearest_tag(color=clr.GREEN)
                if not roots:
                    attempts += 1
                    if attempts < 5:
                        continue
                    break

                mouseover = self.mouseover_text("Chop", color=clr.OFF_WHITE)
                if self.api_m.get_is_player_idle(1):
                    roots = self.get_nearest_tag(color=clr.GREEN)
                    if roots:
                        self.mouse.move_to(roots.random_point(), mouseSpeed="insane")
                        self.mouse.click()
                        time.sleep(2)

            roots = self.get_nearest_tag(color=clr.GREEN)

    def reorder(self):
        for clue in self.reorder_items:
            clue_inv = self.api_m.get_inv_item_indices(clue)
            swaps = False
            if clue_inv:
                swaps = self.assign_indexes(clue_inv, self.api_m.get_inv())
            if swaps:
                self.run_swaps(swaps)

    def run_swaps(self, swaps):
        for swap in swaps:
            self.log_msg("Swapping item #" + str(swap["source_index"]) + " to postion #" + str(swap["target_index"]))
            self.mouse.move_to(self.win.inventory_slots[swap["source_index"]].random_point(), mouseSpeed="insane")
            pag.mouseDown()
            self.mouse.move_to(self.win.inventory_slots[swap["target_index"]].random_point(), mouseSpeed="insane")
            pag.mouseUp()
            time.sleep(3 / 10)

    def assign_indexes(self, list_of_indexes, inventory_data):
        inventory_indexes = [item["index"] for item in inventory_data]
        empty_indexes = [index for index in range(0, 28) if index not in inventory_indexes]
        move_indexes = []

        for source_index in list_of_indexes:
            target_index = empty_indexes.pop()
            if target_index > source_index:
                move_indexes.append({"source_index": source_index, "target_index": target_index})

        return move_indexes
