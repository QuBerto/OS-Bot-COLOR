import math
import string
import time

import pyautogui

import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Point, Rectangle


class OSRSAgilitycourses(OSRSBot):
    """
    Most courses are broken currently. Canifis, Falador and Ardougne do work.
    """

    def __init__(self):
        bot_title = "QuBerto Agility courses"
        description = "QuBerto agility courses"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 200
        all_ascii = string.ascii_letters + string.punctuation + "".join(ocr.problematic_chars)
        self.filtered_ascii = "".join([char for char in all_ascii if char not in "0123456789 ,"])
        self.set_ardougne_course()

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("course", "Which course", ["Ardougne", "Ape atoll", "Fremennik", "Seers", "Falador", "Canifis"])
        self.options_builder.add_checkbox_option("seers_tele", "Use teleport in seers", ["Yes"])

    def save_options(self, options: dict):
        self.do_seers_tele = False
        self.running_time = options["running_time"]
        if options["course"] == "Ape atoll":
            self.set_ape_atoll_course()
        elif options["course"] == "Fremennik":
            self.set_fremennik_course()
        elif options["course"] == "Seers":
            self.set_seers_course()
        elif options["course"] == "Falador":
            self.set_falador_course()
        elif options["course"] == "Canifis":
            self.set_canifis_course()
        elif options["course"] == "Ardougne":
            self.set_ardougne_course()

        if "Yes" in options["seers_tele"]:
            self.do_seers_tele = True
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Course: {self.get_current_name()}")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def pre_main(self):
        self.log_msg(f"Set course to {self.get_current_name()}")

        self.current_step = 0
        self.find_coord_index()
        self.failed = False
        self.last_energy = 100
        self.set_run_orb_color()

    def main_loop(self):
        start_time = time.time()
        end_time = self.running_time * 60
        self.pre_main()
        while time.time() - start_time < end_time:
            self.main()
            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def main(self):
        self.log_msg("Begin Loop")
        if not self.is_coursestep():
            self.start_course()
        self.do_step()

    def start_course(self):
        self.teleport()
        self.turn_on_run_energy()
        self.current_step = 0

    def teleport(self):
        if self.do_seers_tele and (teleport := self.get_current_teleport()):
            self.do_teleport(teleport)

    def do_teleport(self, teleport):
        if teleport == "Camelot_Teleport":
            self.camelot_telly()

        elif teleport == "Camelot_Tabs":
            pass

    def camelot_telly(self):
        tabs_img = imsearch.BOT_IMAGES.joinpath("spell_book", "Camelot_Teleport.png")
        img = imsearch.search_img_in_rect(tabs_img, self.win.control_panel)
        while img and not self.mouseover_text("Seers"):
            self.mouse.move_to(img.random_point())
            self.mouse.click()

    def do_step(self):
        self.current_highest = 0
        self.log_msg(f"Current step {self.get_current_step()}")
        self.log_msg(f"Current step {self.get_current_color()}")
        if self.find_numbers():
            while not self.get_current_tags():
                self.find_highest()

        self.pre_wait()
        self.pick_up_mark()
        while self.is_coursestep():
            if self.search_object():
                break
        self.log_msg("Clicked object")
        start_time = time.time()
        while not self.is_step_completed():
            if self.is_step_failed():
                return False

            time.sleep(3 / 10)
            if start_time < time.time() - self.get_current_timeout() / 1000:
                self.log_msg("Ran out of time")
                self.mouse.move_to(self.win.game_view.random_point())
                return False
        self.log_msg("Step completed")
        self.add_step()
        self.pick_up_mark()

    def search_object(self):
        if self.get_current_tags():
            self.log_msg("Found object")
            if self.try_click():
                return True
            return False

    def try_click(self):
        while True:
            if obj := self.get_current_tags():
                self.mouse.move_to(obj.random_point(), mouseSpeed="fastest")
            else:
                self.mouse.move_to(self.win.game_view.random_point())

            if self.mouse.click(check_red_click=True):
                break
        return True

    def find_highest(self):
        for number in self.create_range():
            found_number = self.find_number(number)
            if found_number and self.current_highest <= number and rd.random_chance(0.8):
                self.log_msg(f"Walking to number {number} of {self.get_current_max_tiles()}")
                center = found_number[0].get_center()
                rect = Rectangle.from_points(Point(center[0], center[1]), Point(center[0], center[1]))
                self.mouse.move_to(rect.random_point(), mouseSpeed="fastest")
                if self.mouseover_text("Walk", color=clr.OFF_WHITE):
                    self.mouse.click()
                    self.current_highest = number
                    time.sleep(1)
                    while not self.get_current_tags() and self.check_if_walking():
                        pass
                    return

    def check_if_walking(self, polling_ms=600):
        old_player_position = self.get_player_position()
        time.sleep(polling_ms / 1000)
        if self.get_player_position() != old_player_position:
            return True
        return False

    def find_coord_index(self):
        coord = self.get_player_position()
        for index, step in enumerate(self.get_all_steps()):
            print(step.get("coord", []))
            print(index)
            if coord == step.get("coord", []):
                self.current_step = index + 1
                return index + 1  # Adding 1 to make the index start from 1 instead of 0
        return 0

    def set_ape_atoll_course(self):
        self.set_course(self.ape_course())

    def set_fremennik_course(self):
        self.set_course(self.fremennik_course())

    def set_seers_course(self):
        self.set_course(self.seers_course())

    def set_falador_course(self):
        self.set_course(self.falador_course())

    def set_canifis_course(self):
        self.set_course(self.canifis_course())

    def set_ardougne_course(self):
        self.set_course(self.ardougne_course())

    def set_course(self, course):
        self.course = course
        if self.get_current_name() != "seers":
            self.do_seers_tele = False

    def pre_wait(self):
        time.sleep(self.get_current_wait() / 1000)

    def add_step(self):
        self.current_step += 1

    def get_current_step(self):
        return self.course["steps"][self.current_step]

    def get_current_color(self) -> clr.Color:
        return self.get_current_step().get("color")

    def get_current_coord(self):
        return self.get_current_step().get("coord")

    def get_current_failed_coord(self):
        return self.get_current_step().get("failed_coord")

    def get_current_text(self):
        return self.get_current_step().get("text")

    def get_current_wait(self):
        return self.get_current_step().get("wait", 0)

    def get_current_timeout(self):
        return self.get_current_step().get("timeout", 10000)

    def get_current_max_tiles(self):
        return self.course.get("max_tile", 0)

    def get_current_teleport(self):
        return self.course.get("teleport", 0)

    def get_current_name(self):
        return self.course.get("name")

    def get_current_marks(self):
        return self.course.get("marks", False)

    def get_all_steps(self):
        return self.course["steps"]

    def get_course(self):
        return self.course

    def get_course_steps(self):
        return len(self.course["steps"])

    def get_current_tags(self):
        return self.get_nearest_tag(self.get_current_color())

    def is_current_mouseover(self, color=clr.OFF_WHITE):
        return self.mouseover_text(self.get_current_text(), color)

    def is_coursestep(self):
        if self.current_step < self.get_course_steps():
            return True
        return False

    def set_last_run_energy(self):
        self.last_energy = self.get_run_energy()
        self.log_msg(f"Last run energy set to {self.last_energy}")

    def get_last_run_energy(self):
        if self.last_energy:
            return self.last_energy
        return 100

    def turn_on_run_energy(self):
        if self.get_last_run_energy() and self.get_last_run_energy() < self.get_run_energy() and self.get_run_energy() > 80:
            self.click_run()
        self.set_last_run_energy()

    def is_step_completed(self):
        if self.get_player_position() == self.get_current_coord():
            return True
        return False

    def get_player_position(self):
        box = Rectangle(left=self.win.game_view.get_top_left()[0], top=self.win.game_view.get_top_left()[1], width=150, height=50)
        extracted = ocr.extract_text(box, ocr.PLAIN_12, [clr.OFF_WHITE], exclude_chars=self.filtered_ascii)
        result = (-1, -1, -1)
        if extracted:
            result = tuple(int(item) for item in extracted.split(","))
        return result

    def get_pixel_color(self, x: int, y: int):
        pixel_color = pyautogui.screenshot().getpixel((x, y))
        return pixel_color

    def get_pixel_run_orb(self):
        x, y = self.win.run_orb.get_center()
        self.get_pixel_color(x, y)
        return x, y

    def set_run_orb_color(self):
        self.run_orb_color = self.win.run_orb.random_point()

    def get_run_orb_color(self):
        return self.run_orb_color

    def is_step_failed(self):
        if self.get_player_position()[2] == 0 and (self.current_step <= self.get_course_steps() and self.current_step != 0):
            self.failed = True
            self.current_step = 0
            return True
        return False

    def is_failed(self):
        if self.failed:
            return True
        return False

    def is_first(self):
        if self.current_step == 0:
            return True
        return False

    def find_numbers(self):
        if self.is_first() or self.is_failed():
            return True
        return False

    def create_range(self):
        numbers = list(range(self.current_highest, self.get_current_max_tiles() + 1))
        numbers.reverse()
        return numbers

    def find_number(self, number: int):
        return ocr.find_text(str(number), rect=self.win.game_view, font=ocr.PLAIN_11, color=clr.ORANGE)

    def find_mark_of_grace(self):
        self.performance_start()
        result = ocr.find_text(str("gr"), rect=self.win.game_view, font=ocr.PLAIN_11, color=clr.PURPLE)
        self.performance_end()
        return result

    def get_center(self):
        return self.win.game_view.get_center()

    def open_control_panel(self, number):
        self.mouse.move_to(self.win.cp_tabs[number])
        self.mouse.click()

    def pick_up_mark(self):
        if self.get_current_marks() and (grace := self.find_mark_of_grace()):
            try:
                if self.is_grace_closer_to_center(grace[0].get_center()):
                    while self.find_mark_of_grace():
                        time.sleep(6 / 10)
                        if self.pick_up_loot("Mark of grace"):
                            while self.check_if_walking():
                                time.sleep(1 / 10)
                            return True
            except ValueError:
                self.mouse.move_to(self.win.game_view.random_point())
        return False

    def distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def is_grace_closer_to_center(self, grace):
        center_to_grace = self.distance(self.get_center(), grace)
        center_to_current_tag = self.distance(self.get_center(), self.get_current_tags().center())
        return center_to_grace < center_to_current_tag

    def is_run_toggled(self):
        if self.get_pixel_run_orb() != self.get_run_orb_color():
            return False
        return True

    def click_run(self):
        if not self.is_run_toggled():
            while not self.mouseover_text("Toggle"):
                self.mouse.move_to(self.win.run_orb.random_point())
            self.mouse.click()

    def performance_start(self):
        self.start_time = time.perf_counter()

    def performance_end(self):
        self.end_time = time.perf_counter()
        elapsed_time_ms = (self.end_time - self.start_time) * 1000  # Convert to milliseconds
        print(f"Time taken full: {elapsed_time_ms: .2f} ms")

    def ape_course(self):
        return {
            "name": "Ape atoll agility course",
            "max_tile": 0,
            "marks": False,
            "steps": [
                {
                    "color": clr.CYAN,
                    "coord": (2753, 2742, 0),
                    "text": "Jump-to",
                    "timeout": 10000,
                },
                {
                    "color": clr.BLUE,
                    "coord": (2753, 2742, 2),
                    "text": "Climb",
                    "wait": 2000,
                },
                {
                    "color": clr.RED,
                    "coord": (2747, 2741, 0),
                    "text": "Swing Across",
                    "timeout": 10000,
                },
                {
                    "color": clr.GREEN,
                    "coord": (2742, 2741, 0),
                    "text": "Climb-up",
                    "timeout": 10000,
                },
                {
                    "color": clr.RED,
                    "coord": (2756, 2731, 0),
                    "text": "Swing",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.YELLOW,
                    "coord": (2770, 2747, 0),
                    "text": "Climb-down",
                    "timeout": 14000,
                    "wait": 1000,
                },
            ],
        }

    def seers_course(self):
        return {
            "name": "Seers Rooftop agility course",
            "max_tile": 10,
            "marks": True,
            "teleport": "Camelot_Teleport",
            "steps": [
                {
                    "color": clr.CYAN,
                    "coord": (2729, 3491, 3),
                    "text": "Climb",
                    "timeout": 10000,
                    "wait": 1800,
                },
                {
                    "color": clr.CYAN,
                    "coord": (2713, 3494, 2),
                    "text": "Jump",
                    "timeout": 10000,
                    "wait": 1800,
                },
                {
                    "color": clr.RED,
                    "coord": (2710, 3480, 2),
                    "text": "Cross",
                    "timeout": 10000,
                    "wait": 1800,
                },
                {
                    "color": clr.BLUE,
                    "coord": (2710, 3472, 3),
                    "text": "Jump",
                    "timeout": 10000,
                    "wait": 1800,
                },
                {
                    "color": clr.BLUE,
                    "coord": (2702, 3465, 2),
                    "text": "Jump",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.GREEN,
                    "coord": (2704, 3464, 0),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
            ],
        }

    def fremennik_course(self):
        return {
            "name": "Fremennik rooftop course",
            "max_tile": 10,
            "marks": True,
            "steps": [
                {
                    "color": clr.CYAN,
                    "coord": (2625, 3676, 3),
                    "text": "Climb",
                    "timeout": 10000,
                },
                {
                    "color": clr.CYAN,
                    "coord": (2622, 3668, 3),
                    "text": "Leap",
                    "timeout": 6000,
                    "wait": 1800,
                },
                {
                    "color": clr.BLUE,
                    "coord": (2627, 3654, 3),
                    "text": "Cross",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.GREEN,
                    "coord": (2639, 3653, 3),
                    "text": "Leap",
                    "timeout": 10000,
                },
                {
                    "color": clr.RED,
                    "coord": (2643, 3657, 3),
                    "text": "Hurdle",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.YELLOW,
                    "coord": (2655, 3670, 3),
                    "text": "Cross",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.WHITE,
                    "coord": (2652, 3676, 0),
                    "text": "Jump-in",
                    "timeout": 14000,
                    "wait": 1000,
                },
            ],
        }

    def falador_course(self):
        return {
            "name": "Falador rooftop course",
            "max_tile": 10,
            "marks": True,
            "steps": [
                {
                    "color": clr.CYAN,
                    "coord": (3036, 3342, 3),
                    "text": "Climb",
                    "timeout": 10000,
                },
                {
                    "color": clr.RED,
                    "coord": (3047, 3344, 3),
                    "text": "Cross",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.BLUE,
                    "coord": (3050, 3357, 3),
                    "text": "Cross",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.GREEN,
                    "coord": (3048, 3361, 3),
                    "text": "Jump",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.YELLOW,
                    "coord": (3041, 3361, 3),
                    "text": "Jump",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.CYAN,
                    "coord": (3028, 3354, 3),
                    "text": "Cross",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.WHITE,
                    "coord": (3020, 3353, 3),
                    "text": "Cross",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.ORANGE,
                    "coord": (3018, 3349, 3),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.GREEN,
                    "coord": (3014, 3346, 3),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.BLUE,
                    "coord": (3013, 3342, 3),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.CYAN,
                    "coord": (3013, 3333, 3),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.RED,
                    "coord": (3019, 3333, 3),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.YELLOW,
                    "coord": (3029, 3333, 0),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
            ],
        }

    def ardougne_course(self):
        return {
            "name": "Ardougne rooftop course",
            "max_tile": 10,
            "marks": True,
            "steps": [
                {
                    "color": clr.BLUE,
                    "coord": (2671, 3299, 3),
                    "text": "Cli",
                    "timeout": 10000,
                },
                {
                    "color": clr.RED,
                    "coord": (2665, 3318, 3),
                    "text": "Jump",
                    "timeout": 10000,
                },
                {
                    "color": clr.BLUE,
                    "coord": (2656, 3318, 3),
                    "text": "-on",
                    "timeout": 10000,
                },
                {
                    "color": clr.GREEN,
                    "coord": (2653, 3314, 3),
                    "text": "Jump",
                    "timeout": 10000,
                    "failed_coord": (2653, 3316, 0),
                },
                {
                    "color": clr.CYAN,
                    "coord": (2651, 3309, 3),
                    "text": "Jump",
                    "timeout": 10000,
                },
                {
                    "color": clr.YELLOW,
                    "coord": (2656, 3297, 3),
                    "text": "Bal",
                    "timeout": 10000,
                },
                {
                    "color": clr.BLUE,
                    "coord": (2668, 3297, 0),
                    "text": "Jump",
                    "wait": 2000,
                    "timeout": 12000,
                },
            ],
        }

    def canifis_course(self):
        return {
            "name": "Canafis rooftop course",
            "max_tile": 10,
            "marks": True,
            "steps": [
                {
                    "color": clr.CYAN,
                    "coord": (3506, 3492, 2),
                    "text": "Climb",
                    "timeout": 10000,
                },
                {
                    "color": clr.CYAN,
                    "coord": (3502, 3504, 2),
                    "text": "Jump",
                    "timeout": 4000,
                    "wait": 1000,
                },
                {
                    "color": clr.GREEN,
                    "coord": (3492, 3504, 2),
                    "text": "Jump",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.RED,
                    "coord": (3479, 3499, 3),
                    "text": "Jump",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.RED,
                    "coord": (3478, 3486, 2),
                    "text": "Jump",
                    "timeout": 10000,
                    "wait": 1000,
                },
                {
                    "color": clr.YELLOW,
                    "coord": (3489, 3476, 3),
                    "text": "Vault",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.WHITE,
                    "coord": (3510, 3476, 2),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
                {
                    "color": clr.WHITE,
                    "coord": (3510, 3485, 0),
                    "text": "Jump",
                    "timeout": 14000,
                    "wait": 1000,
                },
            ],
        }
