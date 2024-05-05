import time

import pyautogui
from plyer import notification

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSAerialFishing(OSRSBot):
    def __init__(self):
        bot_title = "QuBerto Aereal Fishing"
        description = "Fishes at molch island for you"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 120
        self.mouse.register_mouse_speed("custom", 2, 2)
        self.mouse.register_mouse_speed("custom_2", 8, 12)
        self.fish_ids = [ids.BLUEGILL, ids.GREATER_SIREN, ids.MOTTLED_EEL, ids.COMMON_TENCH]
        self.map = True
        self.last_notification_time = 0
        self.inventory_setup = [
            ids.KNIFE,
            ids.FISH_CHUNKS,
            ids.MOLCH_PEARL,
            ids.GOLDEN_TENCH,
            ids.PEARL_FISHING_ROD,
            ids.PEARL_BARBARIAN_ROD,
            ids.PEARL_FLY_FISHING_ROD,
            ids.CLUE_BOTTLE_BEGINNER,
            ids.CLUE_BOTTLE_EASY,
            ids.CLUE_BOTTLE_MEDIUM,
            ids.CLUE_BOTTLE_HARD,
            ids.CLUE_BOTTLE_ELITE,
            ids.FISH_SACK,
            ids.CLUE_SCROLL_BEGINNER,
            ids.CLUE_SCROLL_MEDIUM,
            ids.CLUE_SCROLL,
            ids.CLUE_SCROLL_HARD,
            ids.CLUE_SCROLL_EASY,
            ids.CLUE_SCROLL_ELITE,
        ]
        self.other_player = ""

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        self.running_time = options["running_time"]
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.options_set = True

    def main_loop(self):
        self.api_m = MorgHTTPSocket()
        start_time = time.time()
        end_time = self.running_time * 60
        self.pre_loop()
        while time.time() - start_time < end_time:
            self.main()
            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.logout()
        self.stop()

    def pre_loop(self):
        if not self.api_m.get_is_item_equipped(ids.CORMORANTS_GLOVE_22817):
            self.stop_msg("Gloves not equiped")
        if self.api_m.get_player_position() != (1376, 3629, 0):
            self.stop_msg("Not at starting tile")
        if not self.api_m.get_inv_item_indices(ids.KNIFE):
            self.stop_msg("Missing knife")
        if self.api_m.get_inv_item_stack_amount(ids.FISH_CHUNKS) < 1:
            self.stop_msg("No fishchunks")
        if not self.api_m.test_endpoints():
            self.stop_msg("Something is wrong with the API")
        if not self.get_nearest_tag(color=clr.GREEN):
            self.stop_msg("No green tilemarker set")
        if not self.get_nearest_tag(color=clr.CYAN):
            self.stop_msg("Tag all fishingspots CYAN")
        self.check_map()
        self.log_msg("Pre checks complete")

    def stop_msg(self, msg: str):
        self.log_msg(msg)
        self.stop()

    def main(self):
        self.check_inv()
        self.fish()
        self.check_coords()
        self.check_map()

    def fish(self):
        while not self.mouseover_text("Catch", color=clr.OFF_WHITE):
            self.move_fish()
            if self.mouseover_text("Use", color=clr.OFF_WHITE):
                self.move_tile()
        self.mouse.click()
        empty_spots = 28 - len(self.api_m.get_inv())
        self.log_msg(f"{self.other_player}Catch fish, {empty_spots} empty inv slots", True)
        time.sleep(6 / 10)
        while self.api_m.get_is_item_equipped(ids.CORMORANTS_GLOVE):
            time.sleep(2 / 10)
            if not self.mouseover_text("Catch", color=clr.OFF_WHITE) and len(self.api_m.get_inv()) < 27:
                self.move_fish()

    def move_fish(self):
        if fish := self.get_nearest_tag(color=clr.CYAN):
            self.mouse.move_to(fish.random_point(), mouseSpeed="custom_2")

    def check_inv(self):
        if len(self.api_m.get_inv()) == 28:
            self.log_msg(f"{self.other_player}Inventory full, stop Fishing", True)
            quantity = self.api_m.get_inv_item_stack_amount(ids.FISH_CHUNKS)
            if quantity < rd.random.randint(120, 310):
                self.log_msg(f"{self.other_player}Cut fish")
                self.cut_fish()
            else:
                self.log_msg(f"{self.other_player}Dropping fish")
                self.drop_all_fish()
            self.reorder()
            self.log_msg(f"{self.other_player}Continue fishing")

    def cut_fish(self):
        if (knife := self.api_m.get_inv_item_indices(ids.KNIFE)) and (fishes := self.api_m.get_inv_item_indices(self.fish_ids)):
            for fish in fishes:
                self.log_msg(f"{self.other_player}Cutting fish in position " + str(fish), True)
                self.check_map()
                self.click_item(knife[0])
                self.click_item(fish)
            self.log_msg(f"{self.other_player}Cutting fish finished", True)
        else:
            self.log_msg(f"{self.other_player}Something went horribly wrong")

    def drop_all_fish(self):
        pyautogui.keyDown("shift")
        for fish in self.api_m.get_inv_item_indices(self.fish_ids):
            self.log_msg(f"{self.other_player}Dropping fish in position " + str(fish), True)
            self.check_map()
            self.click_item(fish, "Drop")
        pyautogui.keyUp("shift")
        self.log_msg(f"{self.other_player}Dropping fish finished", True)

    def check_coords(self):
        if self.api_m.get_player_position() != (1376, 3629, 0):
            self.move_tile()
            time.sleep(2)

    def move_tile(self):
        if tile := self.get_nearest_tag(clr.GREEN):
            self.mouse.move_to(tile.random_point(), mouseSpeed="custom_2")
            if (
                self.mouseover_text("Walk", color=clr.OFF_WHITE)
                or self.mouseover_text("Take", color=clr.OFF_WHITE)
                or self.mouseover_text("Use", color=clr.OFF_WHITE)
            ):
                self.log_msg(f"{self.other_player}Clicking green tile")
                self.mouse.click()

    def click_item(self, item: int, text: str = "Use"):
        self.mouse.move_to(self.win.inventory_slots[item].random_point(), mouseSpeed="custom")
        while not self.mouseover_text(text, color=clr.OFF_WHITE):
            self.mouse.move_to(self.win.inventory_slots[item].random_point(), mouseSpeed="custom")
            if self.mouseover_text(text, color=clr.OFF_WHITE):
                break
            self.mouse.move_to(self.win.cp_tabs[3].random_point(), mouseSpeed="custom")
            self.mouse.click()
            self.mouse.move_to(self.win.inventory_slots[item].random_point(), mouseSpeed="custom")
        self.mouse.click()

    def check_map(self):
        if self.map:
            color = (255, 0, 255)
            region = (self.win.minimap.get_top_left()[0], self.win.minimap.get_top_left()[1], self.win.minimap.height, self.win.minimap.width)
            if self.find_color_in_region(color, region):
                self.other_player = "[Player Detected] "
                current_time = time.time()
                if current_time - self.last_notification_time >= 60:  # 60 seconds = 1 minute
                    notification.notify(
                        title="Python Bot",
                        message="PLAYER DETECTED PLAYER DETECTED",
                        app_icon=None,
                        timeout=10,
                    )
                    self.last_notification_time = current_time
            else:
                self.other_player = ""

    def find_color_in_region(self, color: tuple, region: tuple):
        screenshot = pyautogui.screenshot(region=region)
        img = screenshot.convert("RGB")
        for y in range(img.height):
            for x in range(img.width):
                color_tuple = tuple(color)

                if img.getpixel((x, y)) == color_tuple:
                    print(img.getpixel((x, y)))
                    return (x + region[0], y + region[1])
        return None

    def reorder(self):
        for item in self.inventory_setup:
            item_inv = self.api_m.get_inv_item_indices(item)
            swaps = False
            if item_inv:
                swaps = self.assign_indexes(item_inv, self.api_m.get_inv())
            if swaps:
                self.run_swaps(swaps)

    def run_swaps(self, swaps):
        for swap in swaps:
            self.log_msg("Swapping item #" + str(swap["source_index"]) + " to postion #" + str(swap["target_index"]))
            self.mouse.move_to(self.win.inventory_slots[swap["source_index"]].random_point(), mouseSpeed="fastest")
            pyautogui.mouseDown()
            time.sleep(1 / 10)
            self.mouse.move_to(self.win.inventory_slots[swap["target_index"]].random_point(), mouseSpeed="fast")
            pyautogui.mouseUp()
            time.sleep(6 / 10)

    def assign_indexes(self, list_of_indexes, inventory_data):
        inventory_indexes = [item["index"] for item in inventory_data]
        empty_indexes = [index for index in range(0, 28) if index not in inventory_indexes]
        move_indexes = []
        for source_index in list_of_indexes:
            target_index = empty_indexes.pop(0)
            if target_index < source_index:
                move_indexes.append({"source_index": source_index, "target_index": target_index})
        return move_indexes
