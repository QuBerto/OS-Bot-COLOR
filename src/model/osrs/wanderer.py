import utilities.api.locations as loc
from model.osrs.osrs_bot import OSRSBot
from utilities.walker import Walker


class OSRSWalkingExample(OSRSBot):
    def __init__(self):
        super().__init__(bot_title="Wanderer", description="Walk almost anywhere.")

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
            walker = Walker(self)
            dest = self.dest  # loc.TEST_PATH[-1]
            if walker.walk_to(dest):
                self.log_msg("Arrived at destination")
                self.stop()
            self.stop()
