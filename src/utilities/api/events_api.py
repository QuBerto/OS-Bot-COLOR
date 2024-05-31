import inspect
import threading
import time
from types import ModuleType
from typing import Dict, List, Tuple, Union

import item_ids as iid
from flask import Flask, request


class EventsAPI:
    """Interface between Python and the EventsAPI RuneLite plug-in.

    Note that this object listens for POST requests emitted by the EventsAPI plug-in at:
        http://localhost:8081/api/
    It's important to ensure that port 8081 is open and that no other processes are
    using the port.

    The EventsAPI has 8 main event types, and all but 1 of them only update when a
    relevant event occurs. The player_status endpoint is the only event type that is
    constantly emitted (and therefore reliably updated). The inventory_items endpoint,
    for example, will not update unless something changes the state of the inventory
    (for example, an item moving positions, being deposited or traded, or a new item
    being received).
    """

    def __init__(self):
        """Instantiate an `EventsAPI` object to begin receiving OSRS event data."""
        self.app = Flask(__name__)
        self.player_status = {}
        self.inventory_items = {}
        self.bank = {}
        self.npc_kill = {}
        self.level_change = {}
        self.login_state = ""  # "LOGGED_IN" or "LOGGED_OUT".
        self.quest_change = {}
        self.equipped_items = {}
        self.reverse_item_mapping = self._create_reverse_mapping(iid)
        # self.reverse_npc_mapping = self._create_reverse_mapping(nid)
        # These timestamps track the recency of their associated attributes.
        self._player_status_timestamp = None
        self._inventory_items_timestamp = None
        self._bank_timestamp = None
        self._npc_kill_timestamp = None
        self._level_change_timestamp = None
        self._login_state_timestamp = None
        self._quest_change_timestamp = None
        self._equipped_items_timestamp = None

        @self.app.route("/api/player_status/", methods=["POST"])
        def handle_player_status() -> Tuple[str, int]:
            """Handle POST requests to update and timestamp our status.

            Returns:
                Tuple[str, int]: Informational message and HTTP status code.
            """
            if request.method == "POST":
                data = request.json
                self.player_status = data.get("data")
                self._player_status_timestamp = time.time()
                return "Player status data received.", 200
            else:
                return "Only POST requests are supported", 405

        @self.app.route("/api/login_state/", methods=["POST"])
        def handle_login_state() -> Tuple[str, int]:
            """Handle POST requests to update and timestamp our login state.

            Returns:
                Tuple[str, int]: Informational message and HTTP status code.
            """
            if request.method == "POST":
                data = request.json
                self.login_state = data.get("data").get("state")
                self._login_state_timestamp = time.time()
                return "Login state data received.", 200
            else:
                return "Only POST requests are supported", 405

        @self.app.route("/api/level_change/", methods=["POST"])
        def handle_level_change() -> Tuple[str, int]:
            """Handle POST requests to update and timestamp our leveling state.

            Returns:
                Tuple[str, int]: Informational message and HTTP status code.
            """
            if request.method == "POST":
                data = request.json
                self.level_change = data.get("data")
                self._level_change_timestamp = time.time()
                return "Level change data received.", 200
            else:
                return "Only POST requests are supported", 405

        @self.app.route("/api/quest_change/", methods=["POST"])
        def handle_quest_change() -> Tuple[str, int]:
            """Handle POST requests to update and timestamp our quest progress.

            Returns:
                Tuple[str, int]: Informational message and HTTP status code.
            """
            if request.method == "POST":
                data = request.json
                self.quest_change = data.get("data")
                self._quest_change_timestamp = time.time()
                return "Quest change data received.", 200
            else:
                return "Only POST requests are supported", 405

        @self.app.route("/api/equipped_items/", methods=["POST"])
        def handle_equipped_items() -> Tuple[str, int]:
            """Handle POST requests to update and timestamp our equipment info.

            Returns:
                Tuple[str, int]: Informational message and HTTP status code.
            """
            if request.method == "POST":
                data = request.json
                self.equipped_items = data.get("data").get("equippedItems")
                self._equipped_items_timestamp = time.time()
                return "Equipped items data received.", 200
            else:
                return "Only POST requests are supported", 405

        @self.app.route("/api/npc_kill/", methods=["POST"])
        def handle_npc_kill() -> Tuple[str, int]:
            """Handle POST requests to update and timestamp info about recent NPC kills.

            Returns:
                Tuple[str, int]: Informational message and HTTP status code.
            """
            if request.method == "POST":
                data = request.json
                self.npc_kill = data.get("data")
                self._npc_kill_timestamp = time.time()
                return "NPC kill data received.", 200
            else:
                return "Only POST requests are supported", 405

        @self.app.route("/api/inventory_items/", methods=["POST"])
        def handle_inventory_items() -> Tuple[str, int]:
            """Handle POST requests to update and timestamp inventory item details.

            Returns:
                Tuple[str, int]: Informational message and HTTP status code.
            """
            if request.method == "POST":
                data = request.json
                self.inventory_items = data.get("data")
                self._inventory_items_timestamp = time.time()
                return "Iventory items data received.", 200
            else:
                return "Only POST requests are supported", 405

        @self.app.route("/api/bank/", methods=["POST"])
        def handle_bank() -> Tuple[str, int]:
            """Handle POST requests to update and timestamp bank item details.

            Returns:
                Tuple[str, int]: Informational message and HTTP status code.
            """
            if request.method == "POST":
                data = request.json
                self.bank = data.get("data")
                self._bank_timestamp = time.time()
                return "Bank data received.", 200
            else:
                return "Only POST requests are supported", 405

        # Start the Flask server as a daemon thread.
        self.server_thread = threading.Thread(
            target=self.app.run,
            kwargs={"host": "localhost", "port": 8081, "threaded": True},
        )
        self.server_thread.daemon = True
        self.server_thread.start()

    def _create_reverse_mapping(self, module: ModuleType) -> Dict[int, str]:
        """Given a file defining global constants, create a constant:varname mapping.

        This method is intended to help decode JSON payloads, making them more
        human-readable.

        Args:
            module (ModuleType): The reference module containing the global constants.

        Returns:
            Dict[int, str]: A dictionary which maps constants to their corresponding
                variable names.
        """
        reverse_mapping = {}
        for name, value in inspect.getmembers(module):
            if not name.startswith("__") and isinstance(value, int):
                reverse_mapping[value] = name
        return reverse_mapping

    def get_username(self) -> str:
        """Get the username of the account currently logged in.

        Returns:
            str: The up-to-12-character username associated with the logged-in account.
        """
        return self.player_status.get("userName")

    def get_account_type(self) -> str:
        """Get the type of account currently logged in.

        [TO DEV] A member's account shows up as NORMAL. What about a free one? A
            restricted one? A banned one? A mod?

        Returns:
            str: The type of account.
        """
        return self.player_status.get("accountType")

    def get_combat_level(self) -> int:
        """Get our character's combat level.

        Returns:
            int: Our character's integer combat level (i.e. power level).
        """
        return self.player_status.get("combatLevel")

    def get_current_world_point(self) -> Dict[str, int]:
        """Get coordinates describing our characters position, measured in world tiles.

        [TO DEV] Understand more about what the "plane" key is measuring.

        Returns:
            Dict[str, int]: An xy coordinate pair as well as a plane.
        """
        return self.player_status.get("worldPoint")

    def get_current_world(self) -> Union[int, None]:
        """Get the integer ID of the current world (i.e. server) we are logged into.

        Returns:
            int: The integer ID of the game server our character resides in, or None if
                a world is not well-defined (e.g. we are logged out).
        """
        return self.player_status.get("world")

    def get_max_health(self) -> int:
        """Get the maximum number of hit points our character can hold at once.

        Returns:
            int: Our character's maximum number of hit points.
        """
        return self.player_status.get("maxHealth")

    def get_current_health(self) -> int:
        """Return our character's current health.

        Returns:
            int: The current health as of the last relevant POST update.
        """
        return self.player_status.get("currentHealth")

    def get_max_prayer(self) -> int:
        """Get the maximum number of prayer points our character can hold at once.

        Returns:
            int: Our character's maximum number of prayer points.
        """
        return self.player_status.get("maxPrayer")

    def get_current_prayer(self) -> int:
        """Return our character's current prayer level.

        Returns:
            int: The current prayer level as of the last relevant POST update.
        """
        return self.player_status.get("currentPrayer")

    def get_current_run_energy(self) -> int:
        """Get the current run energy on a scale from 0 (0%) to 10,000 (100%).

        Note that run energy in-game is presented as a float between 0 and 100. This means, for example, that 90 run energy corresponds to an output of 9000 from this method.

        Returns:
            int: The current run energy on a scale of 0 to 10,000.
        """
        return self.player_status.get("currentRun")

    def get_current_weight(self) -> int:
        """Get the current weight our character is carrying.

        Returns:
            int: The weight our character is currently carrying (in OSRS weight units).
        """
        return self.player_status.get("currentWeight")

    def is_item_in_inv(self, item_id: Union[List[int], int]) -> bool:
        """Check whether an item is in our character's inventory.

        Args:
            item_id (Union[List[int], int]): The item(s) to check for.

        Returns:
            bool: True if the item is in our inventory, False otherwise.
        """
        if inv := self.inventory_items.get("inventory"):
            if isinstance(item_id, int):
                return any(inventory_slot["id"] == item_id for inventory_slot in inv)
            elif isinstance(item_id, list):
                return any(inventory_slot["id"] in item_id for inventory_slot in inv)

    def get_inv_item_indices(self, item_id: Union[List[int], int]) -> List[int]:
        """Get the inventory indices containing any one of a given amount of items.

        For the given item IDs, get a list of corresponding inventory slot indexes
        containing at least one item with a matching ID.

        Args:
            item_id (Union[List[int], int]): The item ID to search for (a single ID,
                or list of IDs).

        Returns:
            List[int]: A list of inventory slot indexes that the item(s) exists in.
        """
        if inv := self.inventory_items.get("inventory"):
            if isinstance(item_id, int):
                return [i for i, inventory_slot in enumerate(inv) if inventory_slot["id"] == item_id]
            elif isinstance(item_id, list):
                return [i for i, inventory_slot in enumerate(inv) if inventory_slot["id"] in item_id]

    def get_inv_first_occurrences(self, item_id: Union[List[int], int]) -> Union[int, List[int]]:
        """Get the first filled inventory slot index for each of the given item IDs.

        e.g. [1, 1, 2, 3, 3, 3, 4, 4, 4, 4] -> [0, 2, 3, 6]

        Args:
            item_id: The item ID to search for (an single ID, or list of IDs).
        Returns:
            Union[int, List[int]]: The first inventory slot index that the item exists
                in for each unique item ID. If a single item ID is provided, returns an
                integer (or -1 on a failure). If a list of item IDs is provided,
                returns a list of integers (or empty list on a failure).
        """
        if inv := self.inventory_items.get("inventory"):
            if isinstance(item_id, int):
                return next(
                    (i for i, inventory_slot in enumerate(inv) if inventory_slot["id"] == item_id),
                    -1,
                )
            elif isinstance(item_id, list):
                first_occurrences = {}
                for i, inventory_slot in enumerate(inv):
                    item_id_in_slot = inventory_slot["id"]
                    if item_id_in_slot not in first_occurrences and item_id_in_slot in item_id:
                        first_occurrences[item_id_in_slot] = i
                return list(first_occurrences.values())

    def get_inv_item_stack_amount(self, item_id: Union[int, List[int]]) -> int:
        """Get the stack size of the first matching item in our character's inventory.

        This method is primarily itended for items that stack (e.g. coins or runes).

        Args:
            item_id (Union[int, List[int]]): The item ID to search for. If a list is
                passed, the first matching item will be used.
        Returns:
            int: The total number of items corresponding to the matched item ID.
        """
        if inv := self.inventory_items.get("inventory"):
            if isinstance(item_id, int):
                item_id = [item_id]
            if result := next((item for item in inv if item["id"] in item_id), None):
                return int(result["quantity"])
            return 0

    def get_total_inventory_value(self) -> int:
        """Get the total gp value of the possessions in our backpack.

        Returns:
            int: The total number of gold pieces all of the items currently in our
                inventory are worth combined.
        """
        return self.inventory_items.get("gePrice")

    def get_num_empty_inv_slots(self) -> int:
        """Get the number of empty inventory slots in our character's backpack.

        Returns:
            int: The number of unoccupied backpack inventory slots.
        """
        if inv := self.inventory_items.get("inventory"):
            return sum(1 for item in inv if item["id"] == 0 and item["quantity"] == 0)

    def is_inv_empty(self) -> bool:
        """Check whether the inventory is empty.

        Returns:
            bool: True if the inventory is empty, False otherwise.
        """
        return self.get_num_empty_inv_slots() == 28

    def get_num_full_inv_slots(self) -> int:
        """Get the number of filled inventory slots in our character's backpack.

        Returns:
            int: The number of already-occupied backpack inventory slots.
        """
        if self.inventory_items.get("inventory"):
            return 28 - self.get_num_empty_inv_slots()

    def is_inv_full(self) -> bool:
        """Check whether our character's inventory is full.

        Returns:
            bool: True if the inventory is full, False otherwise.
        """
        return self.get_num_full_inv_slots() == 28

    def get_inventory_catalogue(self) -> Dict[str, Union[str, int]]:
        """Get a human-readable catalogue of the items in our inventory.

        Returns:
            Dict[str, Union[str, int]]: An unaggregated, human-readable ledger.
        """
        if self.inventory_items:
            human_readable_inventory = []
            for item in self.inventory_items["inventory"]:
                item_id = item["id"]
                if item_id in self.reverse_item_mapping:
                    human_readable_inventory.append(
                        {
                            "id": self.reverse_item_mapping[item_id],
                            "quantity": item["quantity"],
                        }
                    )
                else:
                    human_readable_inventory.append(item)
            return human_readable_inventory

    def get_aggregate_inventory(self) -> Dict[str, Union[str, int]]:
        """Get a dictionary aggregating items and quantities across all inventory slots.

        Returns:
            Dict[str, Union[str, int]]: A ledger detailing items and quantities.
        """
        aggregated = {}
        empty_slots = 0
        inventory_catalogue = self.get_inventory_catalogue()
        for item in inventory_catalogue:
            item_id = item["id"]
            quantity = item["quantity"]
            if item_id == "EMPTY" and quantity == 0:
                empty_slots += 1
            else:
                if item_id not in aggregated:
                    aggregated[item_id] = quantity
                else:
                    aggregated[item_id] += quantity
        aggregated_inventory = [{"id": item_id, "quantity": quantity} for item_id, quantity in aggregated.items()]
        if empty_slots > 0:
            aggregated_inventory.append({"id": "EMPTY", "quantity": empty_slots})

        return aggregated_inventory

    def get_total_bank_value(self) -> int:
        """Get the total gp value of our possessions in the bank.

        Returns:
            int: The total number of gold pieces all of our bank possessions combined
                are currently worth.
        """
        return self.bank.get("value")

    def get_bank_catalogue(self) -> Dict[str, Union[str, int]]:
        """Get a human-readable catalogue of the items in the bank.

        Returns:
            Dict[str, Union[str, int]]: An unaggregated, human-readable bank ledger.
        """
        if self.bank:
            human_readable_bank = []
            for item in self.bank["items"]:
                item_id = item["id"]
                if item_id in self.reverse_item_mapping:
                    human_readable_bank.append(
                        {
                            "id": self.reverse_item_mapping[item_id],
                            "quantity": item["quantity"],
                        }
                    )
                else:
                    human_readable_bank.append(item)
            return human_readable_bank

    def get_aggregate_bank(self) -> Dict[str, Union[str, int]]:
        """Get a dictionary aggregating items and quantities across all bank slots.

        Returns:
            Dict[str, Union[str, int]]: A ledger detailing items and quantities.
        """
        aggregated = {}
        empty_slots = 0
        bank_catalogue = self.get_bank_catalogue()
        for item in bank_catalogue:
            item_id = item["id"]
            quantity = item["quantity"]
            if item_id == "EMPTY" and quantity == 0:
                empty_slots += 1
            else:
                if item_id not in aggregated:
                    aggregated[item_id] = quantity
                else:
                    aggregated[item_id] += quantity
        aggregated_bank = [{"id": item_id, "quantity": quantity} for item_id, quantity in aggregated.items()]
        if empty_slots > 0:
            aggregated_bank.append({"id": "EMPTY", "quantity": empty_slots})
        return aggregated_bank

    def is_item_equipped(self, item_id: Union[int, List[int]]) -> bool:
        """Check whether our character currently equipped with a given item.

        Args:
            item_id (Union[int, List[int]]): The item ID to check for (a single ID, or
                list of IDs).
        Returns:
            bool: True if an item is equipped, False if not. If a list is provided,
                True if any item in the list is equipped, False otherwise.
        """
        if equips := self.equipped_items:
            equipped_ids = [item["id"] for item in equips.values()]
            if isinstance(item_id, int):
                return item_id in equipped_ids
            return any(item in item_id for item in equipped_ids)

    def get_equipped_item_quantity(self, item_id: int) -> int:
        """Get the quantity of an equipped item.

        This endpoint is particularly useful for checking ammunition numbers.

        Args:
            item_id (int): The item ID of the item our character is wearing (which we
                are checking for quantity).
        Returns:
            int: The quantity of the item equipped, or 0 if it is not equipped.
        """
        if equips := self.equipped_items:
            return next(
                (int(equip_slot["quantity"]) for equip_slot in equips.values() if equip_slot["id"] == item_id),
                0,
            )

    def get_name_of_latest_npc_killed(self) -> str:
        """Get the human-readable name of the latest NPC (i.e. monster) killed.

        Returns:
            str: The human-readable name of the latest monster killed.
        """
        if npc_id := self.npc_kill.get("npcId"):
            return self.reverse_npc_mapping[npc_id]

    def is_logged_in(self) -> Union[bool, None]:
        """Determine whether we are logged in.

        Returns:
            Union[bool, None]: True if we are logged in, False if logged out, and None
                if the current `login_state` is undefined.
        """
        return api_e.login_state == "LOGGED_IN"

    def is_logged_out(self) -> Union[bool, None]:
        """Determine whether we are logged out.

        Returns:
            Union[bool, None]: True if we are logged out, False if logged in, and None
                if the current `login_state` is undefined.
        """
        return api_e.login_state == "LOGGED_IN"

    def get_num_quests_finished(self) -> int:
        """Get a count of the number of quests finished, including member quests.

        Returns:
            int: The number of quests finished.
        """
        if quests := self.quest_change.get("quests"):
            return sum(1 for quest in quests if quest["state"] == "FINISHED")

    def get_num_quests_not_started(self) -> int:
        """Get a count of the number of quests not started, including member quests.

        Returns:
            int: The number of quests not started.
        """
        if quests := self.quest_change.get("quests"):
            return sum(1 for quest in quests if quest["state"] == "NOT_STARTED")

    def get_total_skill_level(self) -> int:
        """Get our character's total skill level.

        Note that the maximum total skill level possible is 23 * 99 = 2277.

        Returns:
            int: The sum of all of our character's skill levels.
        """
        return self.level_change.get("totalLevel")

    def get_last_updated_skill(self) -> Tuple[str, int]:
        """Get the name and level of the most recently leveled-up skill.

        Returns:
            Tuple[str, int]: Name and new level of the most recent skill to level up.
        """
        name = self.level_change.get("updatedSkillName")
        level = self.level_change.get("updatedLevelName")
        return (name, level)

    def get_all_skill_levels(self) -> Dict[str, int]:
        """Retrieve a dictionary of our character's current skill levels.

        Returns:
            Dict[str, int]: A dictionary of name:level pairs.
        """
        return self.level_change.get("levels")


if __name__ == "__main__":
    api_e = EventsAPI()
    for _ in range(100):
        if False:  # Emit all data from all endpoints as POST requests arrive.
            msg = (
                f"\nplayer_status: \n{api_e.player_status}"
                "\n----------------------------"
                f"\nlogin_state: \n {api_e.login_state}"
                "\n----------------------------"
                f"\nlevel_change: \n {api_e.level_change}"
                "\n----------------------------"
                f"\nquest_change: \n {api_e.quest_change}"
                "\n----------------------------"
                f"\nequipped_items: \n {api_e.equipped_items}"
                "\n----------------------------"
                f"\nnpc_kill: \n {api_e.npc_kill}"
                "\n----------------------------"
                f"\ninventory_items: \n {api_e.inventory_items}"
                "\n----------------------------"
                f"\nbank: \n {api_e.bank}"
                "\n############################"
            )
        if False:  # Inventory searching.
            item_ids = [iid.GOLD_BAR, iid.WATER_RUNE]
            equips = [iid.CHEFS_HAT, iid.OBSIDIAN_CAPE]
            msg = (
                f"\nitem_in_inv: {api_e.is_item_in_inv(item_ids)}"
                f"\ninv_item_indices: {api_e.get_inv_item_indices(item_ids)}"
                f"\ninv_first_occurrences: {api_e.get_inv_first_occurrences(item_ids)}"
                f"\ninv_item_stack_amount: {api_e.get_inv_item_stack_amount(item_ids)}"
                f"\nis_item_equipped: {api_e.is_item_equipped(equips)}"
                f"\nequipped_item_quant: {api_e.get_equipped_item_quantity(equips[0])}"
            )
        if False:  # Human-readable inventory and bank data.
            msg = (
                f"inventory_catalogue: {api_e.get_inventory_catalogue()}"
                f"aggregate_inventory: {api_e.get_aggregate_inventory()}"
                f"bank_catalogue: {api_e.get_bank_catalogue()}"
                f"aggregate_bank: {api_e.get_aggregate_bank()}"
            )
        if False:  # Skill and level-up information.
            msg = (
                f"\ntotal_skill_level: {api_e.get_total_skill_level()}"
                f"\nlast_updated_skill: {api_e.get_last_updated_skill()}"
                f"\nall_skill_levels: {api_e.get_all_skill_levels()}"
            )
        if True:  # Basic state-based data.
            msg = (
                f"\nusername: {api_e.get_username()}"
                f"\naccount_type: {api_e.get_account_type()}"
                f"\ncombat_level: {api_e.get_combat_level()}"
                f"\ncurrent_world_point: {api_e.get_current_world_point()}"
                f"\ncurrent_world: {api_e.get_current_world()}"
                f"\nmax_health: {api_e.get_max_health()}"
                f"\ncurrent_health: {api_e.get_current_health()}"
                f"\nmax_prayer: {api_e.get_max_prayer()}"
                f"\ncurrent_prayer: {api_e.get_current_prayer()}"
                f"\ncurrent_run_energy: {api_e.get_current_run_energy()}"
                f"\ncurrent_weight: {api_e.get_current_weight()}"
                f"\ntotal_inventory_value: {api_e.get_total_inventory_value()}"
                f"\nnum_empty_inv_slots: {api_e.get_num_empty_inv_slots()}"
                f"\nis_inv_empty: {api_e.is_inv_empty()}"
                f"\nnum_full_inv_slots: {api_e.get_num_full_inv_slots()}"
                f"\ninv_full: {api_e.is_inv_full()}"
                f"\ntotal_bank_value: {api_e.get_total_bank_value()}"
                f"\nname_of_latest_npc_killed: {api_e.get_name_of_latest_npc_killed()}"
                f"\nis_logged_in: {api_e.is_logged_in()}"
                f"\nis_logged_out: {api_e.is_logged_out()}"
                f"\nnum_quests_finished: {api_e.get_num_quests_finished()}"
                f"\nnum_quests_not_started: {api_e.get_num_quests_not_started()}"
            )
        print(msg)
        # print(msg)
        time.sleep(3)
