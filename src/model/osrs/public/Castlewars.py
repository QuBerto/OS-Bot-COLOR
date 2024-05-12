import time

import utilities.api.item_ids as ids
import utilities.color as clr
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSCastlewars(OSRSBot):
    """
    QuBerto Castle Wars
    "Plays" Castle Wars for you A.K.A stands afk at the top.

    Runelite Profile: Castlewars.properties

    1. Import Runelite Profile
    2. Start in the lobby.
    """

    def __init__(self):
        """
        Initializes the Castle Wars AFK bot.
        """
        bot_title = "QuBerto CW AFK"
        description = "Castle wars AFK bot"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1000

    def create_options(self):
        """
        Creates options for the bot, such as running time.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        """
        Saves the options set by the user.

        Args:
            options (dict): Dictionary containing user options.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
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
        The main loop of the bot that runs until the specified running time is reached.
        """
        self.api_m = MorgHTTPSocket()
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.main()
            time.sleep(1 / 10)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def main(self):
        """
        The main logic of the bot's actions.
        """
        if self.is_waitingroom() or self.is_destination():
            time.sleep(6 / 10)
            return True
        time.sleep(1 / 10)
        if self.is_lobby():
            if self.has_ticket():
                self.bank()
                return True
            else:
                self.click_portal()
        time.sleep(1 / 10)
        if self.is_castlewars():
            if self.get_nearest_tag(color=clr.YELLOW):
                self.click_ladder()

            if self.get_nearest_tag(color=clr.BLUE):
                self.click_tile()
        time.sleep(1 / 10)

    def bank(self):
        """
        Performs banking actions for the bot.
        """
        if self.has_ticket():
            self.open_bank()
            self.click_item(ids.CASTLE_WARS_TICKET, text="Deposit", deposit_all=True)
            self.bank_close()
            self.wait_till_idle()
            return True

    def click_portal(self):
        """
        Clicks the portal if it exists.
        """
        if self.click_tag_if_exists(clr.GREEN, text="Enter"):
            self.wait_till_idle()
            return True
        return False

    def click_ladder(self):
        """
        Clicks the ladder if it exists.
        """
        if self.click_tag_if_exists(clr.YELLOW, text="Climb"):
            self.log_msg("waiting")
            self.wait_till_idle()
            return True
        return False

    def click_tile(self):
        """
        Clicks the tile if it exists.
        """
        if self.click_tag_if_exists(clr.BLUE, text="Walk"):
            self.wait_till_idle()
            return True
        return False

    def region_checker(self):
        """
        Checks the player's current region.
        """
        self.get_region()

    def get_region(self):
        """
        Retrieves the player's current region.
        """
        data = self.api_m.get_player_region_data()
        if data:
            return data[2]
        return False

    def get_coords(self):
        """
        Retrieves the player's current coordinates.
        """
        data = self.api_m.get_player_position()
        if data:
            return data

    def is_lobby(self):
        """
        Checks if the player is in the lobby.
        """
        if self.get_region() == 9776:
            self.log_msg("We are in the lobby")
            return True
        return False

    def is_castlewars(self):
        """
        Checks if the player is in Castle Wars.
        """
        if self.get_region() == 9520:
            self.log_msg("We are in the castle")
            return True
        return False

    def is_waitingroom(self):
        """
        Checks if the player is in the waiting room.
        """
        if self.get_region() == 9620:
            self.log_msg("We are in the waiting room")
            return True
        return False

    def is_destination(self):
        """
        Checks if the player is at the destination.
        """
        coords = self.get_coords()
        if (coords == (2430, 3072, 2) or coords == (2429, 3072, 2)) or (coords == (2370, 3135, 2) or coords == (2369, 3135, 2)):
            self.log_msg("We are at our destination", overwrite=True)
            return True
        return False

    def has_ticket(self):
        """
        Checks if the player has a ticket.
        """
        if self.api_m.get_inv_item_indices(item_id=ids.CASTLE_WARS_TICKET):
            return True
        return False

    def get_inv_slot_ticket(self):
        """
        Retrieves the inventory slot of the ticket item.
        """
        if ticket := self.api_m.get_inv_item_indices(item_id=ids.CASTLE_WARS_TICKET):
            return ticket[0]
