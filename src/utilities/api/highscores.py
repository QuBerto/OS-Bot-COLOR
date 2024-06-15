import requests


class HighScores:
    SKILLS = [
        "overall",
        "attack",
        "defence",
        "strength",
        "hitpoints",
        "ranged",
        "prayer",
        "magic",
        "cooking",
        "woodcutting",
        "fletching",
        "fishing",
        "firemaking",
        "crafting",
        "smithing",
        "mining",
        "herblore",
        "agility",
        "thieving",
        "slayer",
        "farming",
        "runecrafting",
        "hunter",
        "construction",
    ]

    def __init__(self, username: str):
        self.username = username
        self.skill_levels = {}
        self._fetch_player_data()

    def _fetch_player_data(self):
        url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" + self.username
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data for player {self.username}")

        data = response.text.split("\n")
        for index, skill in enumerate(self.SKILLS):
            skill_data = data[index].split(",")
            if len(skill_data) < 2:
                self.skill_levels[skill] = None
            else:
                self.skill_levels[skill] = int(skill_data[1])

    def get_skill_level(self, skill: str) -> int:
        if skill not in self.SKILLS:
            raise ValueError(f"Skill {skill} is not valid. Valid skills are: {', '.join(self.SKILLS)}")

        return self.skill_levels.get(skill)
