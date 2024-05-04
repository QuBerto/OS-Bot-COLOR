import threading
import time
from pathlib import Path

import pyautogui

import utilities.api.item_ids as ids
import utilities.api.locations as loc
import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.functions import QubotFeatures as Qubot
from utilities.walker import Walking

__BARROWS_PATH = Path(__file__).parent
BARROWS_IMAGES = __BARROWS_PATH.joinpath("images")


class OSRSBarrows(OSRSBot):
    def __init__(self):
        bot_title = "Qubot Barrows"
        description = ""
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.order = {
            "Dharoks": loc.BARROWS_DHAROKS,
            "Veracs": loc.BARROWS_VERACS,
            "Ahrims": loc.BARROWS_AHRIMS,
            "Torags": loc.BARROWS_TORAGS,
            "Kharyll": loc.BARROWS_KHARYLL,
            "Guthans": loc.BARROWS_GUTHANS,
        }

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            continue
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        self.api_m = MorgHTTPSocket()
        self.qubot = Qubot(self)
        self.start_threads()

        while not self.current_hp and not self.current_prayer and not self.position:
            self.log_msg("Waiting for threads to start")
            time.sleep(1 / 2)

        while time.time() - start_time < end_time:
            self.main()
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def main(self):
        # self.last_brother = 'Dharoks'
        # self.task = 'tomb'
        self.debug_threads()
        if self.task == "drink_fountain":
            self.drink_fountain()
        elif self.task == "teleport_to_barrows":
            self.teleport_to_barrows()
        elif self.task == "walk_to_brother":
            self.walk_to_brother()
        elif self.task == "dig":
            self.dig()
        elif self.task == "tomb":
            self.do_tomb()

        time.sleep(1)
        pass

    def drink_fountain(self):
        while not self.mouseover_text("Drink"):
            if fountain := self.get_nearest_tag(clr.GREEN):
                self.mouse.move_to(fountain.random_point())
        self.mouse.click()
        while self.task == "drink_fountain":
            time.sleep(1 / 10)
        self.log_msg("drank from fountain")

    def teleport_to_barrows(self):
        while not self.mouseover_text("Barrows"):
            if portal := self.get_nearest_tag(clr.BLUE):
                self.mouse.move_to(portal.random_point())
        self.mouse.click()
        while self.task == "teleport_to_barrows":
            time.sleep(1 / 10)
        self.log_msg("Teleported to barrows")

    def walk_to_brother(self):
        walker = Walking(self)
        walker.walk_to(self.order.get(self.next_brother))

    def dig(self):
        self.api_m = MorgHTTPSocket()
        spade = self.api_m.get_inv_item_indices(ids.SPADE)
        if spade:
            self.mouse.move_to(self.win.inventory_slots[spade[0]].random_point(), mouseSpeed="fastest")
            self.mouse.click()
            while self.task == "dig":
                time.sleep(1 / 10)

    def do_tomb(self):
        self.pre_fight()
        self.search_tomb()

    def search_tomb(self):
        if tomb := self.get_nearest_tag(clr.YELLOW):
            self.mouse.move_to(tomb.random_point(), mouseSpeed="fastest")
            if self.mouse.click(check_red_click=True):
                self.log_msg("Clicked tombe")
                while not self.is_in_combat():
                    message = ""
                    print(message)
                    if message and "nothing" in message:
                        self.did_fight = True

    def pre_fight(self):
        self.mouse.move_to(self.win.cp_tabs[5].random_point())
        self.mouse.click()
        time.sleep(2 / 10)
        if self.last_brother in ["Veracs", "Dharoks", "Torags", "Guthans"]:
            self.qubot.turn_on_prayer("melee")
        elif self.last_brother == "Ahrims":
            self.qubot.turn_on_prayer("magic")
        elif self.last_brother == "Kharyll":
            self.qubot.turn_on_prayer("missiles")

    def debug_threads(self):
        self.log_msg(f"Position: {self.position}")
        self.log_msg(f"HP: {self.current_hp}")
        self.log_msg(f"Prayer: {self.current_prayer}")
        self.log_msg(f"Location: {self.location}")
        self.log_msg(f"last_brother: {self.last_brother}")
        self.log_msg(f"next_brother: {self.next_brother}")
        self.log_msg(f"order: {self.order}")
        self.log_msg(f"brothers_to_do: {self.brothers_to_do}")
        self.log_msg(f"Task: {self.task}")

    def is_house(self):
        if self.get_nearest_tag(clr.BLUE):
            return True
        return False

    def start_threads(self):
        self.position = False
        self.current_hp = False
        self.current_prayer = False
        self.location = False
        self.last_brother = False
        self.next_brother = False
        self.brothers_to_do = self.order.copy()
        self.task = "init"
        self.last_brother = "Dharoks"
        self.did_fight = False
        last_brother_index = list(self.order.keys()).index(self.last_brother)
        next_index = (last_brother_index + 1) % len(self.order)
        self.next_brother = list(self.order.keys())[next_index]
        # Start threads for updating player location, current hitpoints, and current prayer
        location_thread = threading.Thread(target=self.update_location_thread)
        hp_thread = threading.Thread(target=self.update_hp_thread)
        prayer_thread = threading.Thread(target=self.update_prayer_thread)

        # Daemonize the threads so they will be terminated when the main program exits
        location_thread.daemon = True
        hp_thread.daemon = True
        prayer_thread.daemon = True

        # Start the threads
        location_thread.start()
        hp_thread.start()
        prayer_thread.start()

    def determine_task(self):
        if self.location == "POH":
            if self.current_hp:
                if self.current_hp[0] != self.current_hp[1]:
                    self.task = "drink_fountain"
                elif self.current_hp[0] == self.current_hp[1]:
                    self.brothers_to_do = self.order.keys()
                    self.task = "teleport_to_barrows"

        elif self.location == "Barrows" and self.last_brother is False:
            self.task = "walk_to_brother"

            if self.last_brother:
                # Assuming self.last_brother holds the name of the last visited brother
                last_brother_index = list(self.order.keys()).index(self.last_brother)
                next_index = (last_brother_index + 1) % len(self.order)
                self.next_brother = list(self.order.keys())[next_index]

            else:
                # If self.last_brother is not set, you can choose the first brother in the order
                self.next_brother = list(self.order.keys())[0]

        elif self.location in ["Veracs", "Guthans", "Dharoks", "Kharyll", "Torags", "Ahrims"] and not self.did_fight:
            self.did_fight = False
            self.task = "dig"

        elif self.location == "underground":
            print(self.api_m.get_is_in_combat())
            if self.api_m.get_is_in_combat():
                self.task = "figth_brother"
            elif self.did_fight:
                self.task = "leave_tomb"
            else:
                self.task = "tomb"
        elif self.did_fight:
            # Assuming self.last_brother holds the name of the last visited brother
            last_brother_index = list(self.order.keys()).index(self.last_brother)
            next_index = (last_brother_index + 1) % len(self.order)
            self.next_brother = list(self.order.keys())[next_index]
            self.did_fight = False
        elif self.location == "Barrows":
            self.task = "walk_to_brother"

    def update_location_thread(self):
        while self.status.value == 1:
            # Get player location and update it
            self.get_location()
            # Sleep for a certain interval before checking again
            time.sleep(1 / 10)  # Adjust the interval as needed
            self.determine_task()

    def update_hp_thread(self):
        while self.status.value == 1:
            # Get current hitpoints
            self.get_current_hp()
            # Sleep for a certain interval before checking again
            time.sleep(1)  # Adjust the interval as needed

    def update_prayer_thread(self):
        while self.status.value == 1:
            # Get current prayer
            self.get_current_prayer()
            # Sleep for a certain interval before checking again
            time.sleep(1)  # Adjust the interval as needed

    def get_location(self):
        self.position = self.api_m.get_player_position()
        self.last_brother
        if self.is_house():
            self.location = "POH"
        elif self.position and self.position[2] == 3:
            self.location = "underground"

        else:
            self.location = self.check_location(self.position)

    def check_location(self, position):
        current_location = False
        locations = {
            "Barrows_teleport": (3545, 3317, 3584, 3268),
            "Barrows": (3545, 3280, 3584, 3268),
            "Veracs": (3553, 3298, 3557, 3294),
            "Dharoks": (3570, 3299, 3575, 3295),
            "Ahrims": (3562, 3290, 3565, 3288),
            "Torags": (3557, 3286, 3553, 3283),
            "Kharyll": (3563, 3278, 3567, 3274),
            "Guthans": (3574, 3282, 3578, 3279),
        }
        for location, coords in locations.items():
            # Sorting the coordinates to get the minimum and maximum values
            min_x, max_x = sorted([coords[0], coords[2]])
            min_y, max_y = sorted([coords[1], coords[3]])
            # Check if the position falls within the boundaries of the location
            if position[0] >= min_x and position[0] <= max_x and position[1] >= min_y and position[1] <= max_y:
                current_location = location
        if current_location:
            if current_location in self.order:
                self.last_brother = current_location
            return current_location
        return None

    def get_current_hp(self):
        self.api_m = MorgHTTPSocket()
        self.current_hp = self.api_m.get_hitpoints()

    def get_current_prayer(self):
        self.api_m = MorgHTTPSocket()
        skills = self.api_m.get_skills()
        for skill in skills:
            if skill.get("stat") == "Prayer":
                self.current_prayer = (skill.get("boostedLevel"), skill.get("level"))
                break
