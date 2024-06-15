import utilities.api.locations as loc
from model.osrs.osrs_bot import OSRSBot
from utilities.walker import Walker


class OSRSWalkingExample(OSRSBot):
    def __init__(self):
        """
        Walker Tester.

        In option, set destination. Destination should be a valid location without interaction in the way (ie. doors, ditches etc.)
        """
        super().__init__(bot_title="QuBerto Wanderer", description="Walk almost anywhere.")
        self.dest = loc.VARROCK_SQUARE

    def create_options(self):
        locations = [name for name in vars(loc) if not name.startswith("__")]
        self.options_builder.add_dropdown_option("dest", "Destination:", locations)

    def save_options(self, options: dict):
        for option in options:
            if option == "dest":
                self.log_msg(f"dest: {options[option]}")
                self.dest = options[option]
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        while True:
            print("mouse")
            self.mouse.move_to(self.win.game_view.random_point())
            print("Wind")
            self.mouse.wind_move_to(self.win.inventory_slots[2].random_point())
            # print(self.test(self.win.minimap,margin=0,columns=1))
            # walker = Walker(self)
            # dest = self.dest  # loc.TEST_PATH[-1]
            # if walker.walk_to(dest, host="dax"):
            #     self.log_msg("Arrived at destination.")
            #     self.stop()
            # self.stop()
