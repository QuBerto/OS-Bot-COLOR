import json
import math
import os
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


class GroupData:
    group_name = "Placeholder"

    def __init__(self, username: str = ""):
        if username and os.path.exists(DATA_DIR + "/" + username + ".json"):
            # TODO: Load data from previous session
            # self.load_data("username")
            pass
        self.bank = []
        self.inventory = []
        self.stats = {}
        self.name = ""
        self.coordinates = {}
        self.skills = {}
        self.interacting = {}
        self.equipment = {}
        self.quests = []
        self.rune_pouch = {}
        self.diary_vars = {}
        self.shared_bank = []
        self.xp_table = self.calculate_xp_to_level()

    def set_bank(self, bank_data):
        self.bank = bank_data

    def set_inventory(self, inventory_data):
        self.inventory = inventory_data

    def set_stats(self, stats_data):
        keys = ["boosted_hitpoints", "hitpoints", "boosted_prayer", "prayer", "run_energy", "special_attack", "unknown"]
        self.stats = {keys[i]: stats_data[i] for i in range(min(len(keys), len(stats_data)))}

    def set_name(self, name_data):
        self.name = name_data

    def set_coordinates(self, coordinates_data):
        self.coordinates = coordinates_data

    def set_skills(self, skills_data):
        keys = [
            "agility",
            "attack",
            "construction",
            "cooking",
            "crafting",
            "defence",
            "farming",
            "firemaking",
            "fishing",
            "fletching",
            "herblore",
            "hitpoints",
            "hunter",
            "magic",
            "mining",
            "prayer",
            "ranged",
            "runecrafting",
            "slayer",
            "smithing",
            "strength",
            "thieving",
            "woodcutting",
        ]
        self.skills = {keys[i]: skills_data[i] for i in range(min(len(keys), len(skills_data)))}

    def set_interacting(self, interacting_data):
        self.interacting = interacting_data

    def set_equipment(self, equipment_data):
        self.equipment = equipment_data

    def set_quests(self, quests_data):
        self.quests = quests_data

    def set_rune_pouch(self, rune_pouch_data):
        self.rune_pouch = rune_pouch_data

    def set_diary_vars(self, diary_vars_data):
        self.diary_vars = diary_vars_data

    def set_shared_bank(self, shared_bank_data):
        self.shared_bank = shared_bank_data

    def render_bank(self):
        rendered_bank = []
        for i in range(0, len(self.bank), 2):
            item = {"item_id": self.bank[i], "quantity": self.bank[i + 1]}
            rendered_bank.append(item)
        return rendered_bank

    def render_inventory(self):
        rendered_inventory = []
        for i in range(0, len(self.equipment), 2):
            item = {"item_id": self.equipment[i], "quantity": self.equipment[i + 1]}
            rendered_inventory.append(item)
        return rendered_inventory

    def render_equipment(self):
        rendered_equipment = []
        for i in range(0, len(self.inventory), 2):
            item = {"item_id": self.inventory[i], "quantity": self.inventory[i + 1]}
            rendered_equipment.append(item)
        return rendered_equipment

    def render_shared(self):
        rendered_shared = []
        for i in range(0, len(self.shared_bank), 2):
            item = {"item_id": self.shared_bank[i], "quantity": self.shared_bank[i + 1]}
            rendered_shared.append(item)
        return rendered_shared

    def load_data(self, username: str):
        # TODO: How to dynamicly populate username, i dont think thats possible.
        file_path = os.path.join(DATA_DIR, f"{username}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                if "bank" in data:
                    self.set_bank(data["bank"])
                if "inventory" in data:
                    self.set_inventory(data["inventory"])
                if "stats" in data:
                    self.set_stats(data["stats"])
                if "name" in data:
                    self.set_name(data["name"])
                if "coordinates" in data:
                    self.set_coordinates(data["coordinates"])
                if "skills" in data:
                    self.set_skills(data["skills"])
                if "interacting" in data:
                    self.set_interacting(data["interacting"])
                if "equipment" in data:
                    self.set_equipment(data["equipment"])
                if "quests" in data:
                    self.set_quests(data["quests"])
                if "rune_pouch" in data:
                    self.set_rune_pouch(data["rune_pouch"])
                if "diary_vars" in data:
                    self.set_diary_vars(data["diary_vars"])
                if "shared_bank" in data:
                    self.set_shared_bank(data["shared_bank"])

    def get_data(self):
        return {
            "bank": self.render_bank(),
            "inventory": self.render_inventory(),
            "stats": self.stats,
            "name": self.name,
            "coordinates": self.coordinates,
            "skills": self.skills,
            "interacting": self.interacting,
            "equipment": self.render_equipment(),
            "quests": self.quests,
            "rune_pouch": self.rune_pouch,
            "diary_vars": self.diary_vars,
            "shared_bank": self.render_shared(),
        }

    def get_username(self) -> str:
        """Get the username of the account currently logged in.

        Returns:
            str: The up-to-12-character username associated with the logged-in account.
        """
        return self.name

    def get_combat_level(self) -> int:
        """Get our character's combat level.

        Returns:
            int: Our character's integer combat level (i.e. power level).
        """
        # Base level
        base_level = (self.get_level("defence") + self.get_level("hitpoints") + self.get_level("prayer")) / 4

        # Melee combat level
        melee_level = base_level + (self.get_level("attack") + self.get_level("strength")) / 4

        # Ranged combat level
        ranged_level = base_level + (self.get_level("ranged") * 3 / 8)

        # Magic combat level
        magic_level = base_level + (self.get_level("magic") * 3 / 8)

        # Combat level is the maximum of the melee, ranged, and magic levels
        combat_level = max(melee_level, ranged_level, magic_level)

        return combat_level

    def calculate_xp_to_level(self):
        xp_table = [0] * 100
        for level in range(1, 100):
            xp = math.floor((level - 1 + 300 * math.pow(2, (level - 1) / 7.0)) / 4)
            xp_table[level] = xp_table[level - 1] + xp
        return xp_table

    def get_level(self, skill: str):
        xp = self.skills.get(skill, 1)
        return self.get_level_from_xp(xp)

    def get_level_from_xp(self, xp):
        for level in range(1, 100):
            if xp < self.xp_table[level]:
                return level - 1
        return 99

    def debug(self):
        print(f"get_username(): {self.get_username()}")
        print(f"get_combat_level(): {self.get_combat_level()}")
        print(self.get_level("magic"))


group_data = GroupData()


def save_data(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        json.dump(data, f, indent=4)


@app.route(f"/api/group/{group_data.group_name}/am-i-in-group", methods=["GET"])
def update_data2():
    return jsonify({"status": "success", "in_group": True}), 200


@app.route(f"/api/group/{group_data.group_name}/update-group-member", methods=["POST"])
def update_data():
    data = request.json
    undefined_keys = []

    if "bank" in data:
        group_data.set_bank(data["bank"])
    if "inventory" in data:
        group_data.set_inventory(data["inventory"])
    if "stats" in data:
        group_data.set_stats(data["stats"])
    if "name" in data:
        group_data.set_name(data["name"])
    if "coordinates" in data:
        group_data.set_coordinates(data["coordinates"])
    if "skills" in data:
        group_data.set_skills(data["skills"])
    if "interacting" in data:
        group_data.set_interacting(data["interacting"])
    if "equipment" in data:
        group_data.set_equipment(data["equipment"])
    if "quests" in data:
        group_data.set_quests(data["quests"])
    if "rune_pouch" in data:
        group_data.set_rune_pouch(data["rune_pouch"])
    if "diary_vars" in data:
        group_data.set_diary_vars(data["diary_vars"])
    if "shared_bank" in data:
        group_data.set_shared_bank(data["shared_bank"])

    for key in data:
        if key not in [
            "bank",
            "inventory",
            "stats",
            "name",
            "coordinates",
            "skills",
            "interacting",
            "equipment",
            "quests",
            "rune_pouch",
            "diary_vars",
            "shared_bank",
        ]:
            undefined_keys.append(key)

    if undefined_keys:
        print(f"Undefined keys: {undefined_keys}")

    if group_data.get_username():
        save_data(group_data.get_username() + ".json", group_data.get_data())
        group_data.debug()
    return jsonify({"status": "success", "undefined_keys": undefined_keys}), 200


def start_server():
    app.run(host="0.0.0.0", port=9420)


if __name__ == "__main__":
    start_server()
    group = GroupData()
    print(group.inventory)
    time.sleep(1)
