def is_bit_set(num, bit):
    return (num & (1 << bit)) != 0


def parse_diary_data(diary_vars):
    result = {
        "Ardougne": {"Easy": []},
        "Desert": {"Easy": []},
        "Falador": {"Easy": []},
        "Fremennik": {"Easy": []},
        "Kandarin": {"Easy": []},
        "Karamja": {"Easy": []},
        "Kourend & Kebos": {"Easy": []},
        "Lumbridge & Draynor": {"Easy": []},
        "Morytania": {"Easy": []},
        "Varrock": {"Easy": []},
        "Western Provinces": {"Easy": []},
        "Wilderness": {"Easy": []},
    }

    result["Ardougne"]["Easy"] = [
        is_bit_set(diary_vars[0], 0),
        is_bit_set(diary_vars[0], 1),
        is_bit_set(diary_vars[0], 2),
        is_bit_set(diary_vars[0], 4),
        is_bit_set(diary_vars[0], 5),
        is_bit_set(diary_vars[0], 6),
        is_bit_set(diary_vars[0], 7),
        is_bit_set(diary_vars[0], 9),
        is_bit_set(diary_vars[0], 11),
        is_bit_set(diary_vars[0], 12),
    ]
    result["Ardougne"]["Medium"] = [
        is_bit_set(diary_vars[0], 13),
        is_bit_set(diary_vars[0], 14),
        is_bit_set(diary_vars[0], 15),
        is_bit_set(diary_vars[0], 16),
        is_bit_set(diary_vars[0], 17),
        is_bit_set(diary_vars[0], 18),
        is_bit_set(diary_vars[0], 19),
        is_bit_set(diary_vars[0], 20),
        is_bit_set(diary_vars[0], 21),
        is_bit_set(diary_vars[0], 23),
        is_bit_set(diary_vars[0], 24),
        is_bit_set(diary_vars[0], 25),
    ]
    result["Ardougne"]["Hard"] = [
        is_bit_set(diary_vars[0], 26),
        is_bit_set(diary_vars[0], 27),
        is_bit_set(diary_vars[0], 28),
        is_bit_set(diary_vars[0], 29),
        is_bit_set(diary_vars[0], 30),
        is_bit_set(diary_vars[0], 31),
        is_bit_set(diary_vars[1], 0),
        is_bit_set(diary_vars[1], 1),
        is_bit_set(diary_vars[1], 2),
        is_bit_set(diary_vars[1], 3),
        is_bit_set(diary_vars[1], 4),
        is_bit_set(diary_vars[1], 5),
    ]
    result["Ardougne"]["Elite"] = [
        is_bit_set(diary_vars[1], 6),
        is_bit_set(diary_vars[1], 7),
        is_bit_set(diary_vars[1], 9),
        is_bit_set(diary_vars[1], 8),
        is_bit_set(diary_vars[1], 10),
        is_bit_set(diary_vars[1], 11),
        is_bit_set(diary_vars[1], 12),
        is_bit_set(diary_vars[1], 13),
    ]
    result["Desert"]["Easy"] = [
        is_bit_set(diary_vars[2], 1),
        is_bit_set(diary_vars[2], 2),
        is_bit_set(diary_vars[2], 3),
        is_bit_set(diary_vars[2], 4),
        is_bit_set(diary_vars[2], 5),
        is_bit_set(diary_vars[2], 6),
        is_bit_set(diary_vars[2], 7),
        is_bit_set(diary_vars[2], 8),
        is_bit_set(diary_vars[2], 9),
        is_bit_set(diary_vars[2], 10),
        is_bit_set(diary_vars[2], 11),
    ]
    result["Desert"]["Medium"] = [
        is_bit_set(diary_vars[2], 12),
        is_bit_set(diary_vars[2], 13),
        is_bit_set(diary_vars[2], 14),
        is_bit_set(diary_vars[2], 15),
        is_bit_set(diary_vars[2], 16),
        is_bit_set(diary_vars[2], 17),
        is_bit_set(diary_vars[2], 18),
        is_bit_set(diary_vars[2], 19),
        is_bit_set(diary_vars[2], 20),
        is_bit_set(diary_vars[2], 21),
        (is_bit_set(diary_vars[2], 22) or is_bit_set(diary_vars[3], 9)),
        is_bit_set(diary_vars[2], 23),
    ]
    result["Desert"]["Hard"] = [
        is_bit_set(diary_vars[2], 24),
        is_bit_set(diary_vars[2], 25),
        is_bit_set(diary_vars[2], 26),
        is_bit_set(diary_vars[2], 27),
        is_bit_set(diary_vars[2], 28),
        is_bit_set(diary_vars[2], 29),
        is_bit_set(diary_vars[2], 30),
        is_bit_set(diary_vars[2], 31),
        is_bit_set(diary_vars[3], 0),
        is_bit_set(diary_vars[3], 1),
    ]
    result["Desert"]["Elite"] = [
        is_bit_set(diary_vars[3], 2),
        is_bit_set(diary_vars[3], 4),
        is_bit_set(diary_vars[3], 5),
        is_bit_set(diary_vars[3], 6),
        is_bit_set(diary_vars[3], 7),
        is_bit_set(diary_vars[3], 8),
    ]
    result["Falador"]["Easy"] = [
        is_bit_set(diary_vars[4], 0),
        is_bit_set(diary_vars[4], 1),
        is_bit_set(diary_vars[4], 2),
        is_bit_set(diary_vars[4], 3),
        is_bit_set(diary_vars[4], 4),
        is_bit_set(diary_vars[4], 5),
        is_bit_set(diary_vars[4], 6),
        is_bit_set(diary_vars[4], 7),
        is_bit_set(diary_vars[4], 8),
        is_bit_set(diary_vars[4], 9),
        is_bit_set(diary_vars[4], 10),
    ]
    result["Falador"]["Medium"] = [
        is_bit_set(diary_vars[4], 11),
        is_bit_set(diary_vars[4], 12),
        is_bit_set(diary_vars[4], 13),
        is_bit_set(diary_vars[4], 14),
        is_bit_set(diary_vars[4], 15),
        is_bit_set(diary_vars[4], 16),
        is_bit_set(diary_vars[4], 17),
        is_bit_set(diary_vars[4], 18),
        is_bit_set(diary_vars[4], 20),
        is_bit_set(diary_vars[4], 21),
        is_bit_set(diary_vars[4], 22),
        is_bit_set(diary_vars[4], 23),
        is_bit_set(diary_vars[4], 24),
        is_bit_set(diary_vars[4], 25),
    ]
    result["Falador"]["Hard"] = [
        is_bit_set(diary_vars[4], 26),
        is_bit_set(diary_vars[4], 27),
        is_bit_set(diary_vars[4], 28),
        is_bit_set(diary_vars[4], 29),
        is_bit_set(diary_vars[4], 30),
        is_bit_set(diary_vars[4], 31),
        is_bit_set(diary_vars[5], 0),
        is_bit_set(diary_vars[5], 1),
        is_bit_set(diary_vars[5], 2),
        is_bit_set(diary_vars[5], 3),
        is_bit_set(diary_vars[5], 4),
    ]
    result["Falador"]["Elite"] = [
        is_bit_set(diary_vars[5], 5),
        is_bit_set(diary_vars[5], 6),
        is_bit_set(diary_vars[5], 7),
        is_bit_set(diary_vars[5], 8),
        is_bit_set(diary_vars[5], 9),
        is_bit_set(diary_vars[5], 10),
    ]
    result["Fremennik"]["Easy"] = [
        is_bit_set(diary_vars[6], 1),
        is_bit_set(diary_vars[6], 2),
        is_bit_set(diary_vars[6], 3),
        is_bit_set(diary_vars[6], 4),
        is_bit_set(diary_vars[6], 5),
        is_bit_set(diary_vars[6], 6),
        is_bit_set(diary_vars[6], 7),
        is_bit_set(diary_vars[6], 8),
        is_bit_set(diary_vars[6], 9),
        is_bit_set(diary_vars[6], 10),
    ]
    result["Fremennik"]["Medium"] = [
        is_bit_set(diary_vars[6], 11),
        is_bit_set(diary_vars[6], 12),
        is_bit_set(diary_vars[6], 13),
        is_bit_set(diary_vars[6], 14),
        is_bit_set(diary_vars[6], 15),
        is_bit_set(diary_vars[6], 17),
        is_bit_set(diary_vars[6], 18),
        is_bit_set(diary_vars[6], 19),
        is_bit_set(diary_vars[6], 20),
    ]
    result["Fremennik"]["Hard"] = [
        is_bit_set(diary_vars[6], 21),
        is_bit_set(diary_vars[6], 23),
        is_bit_set(diary_vars[6], 24),
        is_bit_set(diary_vars[6], 25),
        is_bit_set(diary_vars[6], 26),
        is_bit_set(diary_vars[6], 27),
        is_bit_set(diary_vars[6], 28),
        is_bit_set(diary_vars[6], 29),
        is_bit_set(diary_vars[6], 30),
    ]
    result["Fremennik"]["Elite"] = [
        is_bit_set(diary_vars[6], 31),
        is_bit_set(diary_vars[7], 0),
        is_bit_set(diary_vars[7], 1),
        is_bit_set(diary_vars[7], 2),
        is_bit_set(diary_vars[7], 3),
        is_bit_set(diary_vars[7], 4),
    ]
    result["Kandarin"]["Easy"] = [
        is_bit_set(diary_vars[8], 1),
        is_bit_set(diary_vars[8], 2),
        is_bit_set(diary_vars[8], 3),
        is_bit_set(diary_vars[8], 4),
        is_bit_set(diary_vars[8], 5),
        is_bit_set(diary_vars[8], 6),
        is_bit_set(diary_vars[8], 7),
        is_bit_set(diary_vars[8], 8),
        is_bit_set(diary_vars[8], 9),
        is_bit_set(diary_vars[8], 10),
        is_bit_set(diary_vars[8], 11),
    ]
    result["Kandarin"]["Medium"] = [
        is_bit_set(diary_vars[8], 12),
        is_bit_set(diary_vars[8], 13),
        is_bit_set(diary_vars[8], 14),
        is_bit_set(diary_vars[8], 15),
        is_bit_set(diary_vars[8], 16),
        is_bit_set(diary_vars[8], 17),
        is_bit_set(diary_vars[8], 18),
        is_bit_set(diary_vars[8], 19),
        is_bit_set(diary_vars[8], 20),
        is_bit_set(diary_vars[8], 21),
        is_bit_set(diary_vars[8], 22),
        is_bit_set(diary_vars[8], 23),
        is_bit_set(diary_vars[8], 24),
        is_bit_set(diary_vars[8], 25),
    ]
    result["Kandarin"]["Hard"] = [
        is_bit_set(diary_vars[8], 26),
        is_bit_set(diary_vars[8], 27),
        is_bit_set(diary_vars[8], 28),
        is_bit_set(diary_vars[8], 29),
        is_bit_set(diary_vars[8], 30),
        is_bit_set(diary_vars[8], 31),
        is_bit_set(diary_vars[9], 0),
        is_bit_set(diary_vars[9], 1),
        is_bit_set(diary_vars[9], 2),
        is_bit_set(diary_vars[9], 3),
        is_bit_set(diary_vars[9], 4),
    ]
    result["Kandarin"]["Elite"] = [
        is_bit_set(diary_vars[9], 5),
        is_bit_set(diary_vars[9], 6),
        is_bit_set(diary_vars[9], 7),
        is_bit_set(diary_vars[9], 8),
        is_bit_set(diary_vars[9], 9),
        is_bit_set(diary_vars[9], 10),
        is_bit_set(diary_vars[9], 11),
    ]
    result["Karamja"]["Easy"] = [
        (diary_vars[23] == 5),
        (diary_vars[24] == 1),
        (diary_vars[25] == 1),
        (diary_vars[26] == 1),
        (diary_vars[27] == 1),
        (diary_vars[28] == 1),
        (diary_vars[29] == 1),
        (diary_vars[30] == 5),
        (diary_vars[31] == 1),
        (diary_vars[32] == 1),
    ]
    result["Karamja"]["Medium"] = [
        (diary_vars[33] == 1),
        (diary_vars[34] == 1),
        (diary_vars[35] == 1),
        (diary_vars[36] == 1),
        (diary_vars[37] == 1),
        (diary_vars[38] == 1),
        (diary_vars[39] == 1),
        (diary_vars[40] == 1),
        (diary_vars[41] == 1),
        (diary_vars[42] == 1),
        (diary_vars[43] == 1),
        (diary_vars[44] == 1),
        (diary_vars[45] == 1),
        (diary_vars[46] == 1),
        (diary_vars[47] == 1),
        (diary_vars[48] == 1),
        (diary_vars[49] == 1),
        (diary_vars[50] == 1),
        (diary_vars[51] == 1),
    ]
    result["Karamja"]["Hard"] = [
        (diary_vars[52] == 1),
        (diary_vars[53] == 1),
        (diary_vars[54] == 1),
        (diary_vars[55] == 1),
        (diary_vars[56] == 1),
        (diary_vars[57] == 1),
        (diary_vars[58] == 1),
        (diary_vars[59] == 5),
        (diary_vars[60] == 1),
        (diary_vars[61] == 1),
    ]
    result["Karamja"]["Elite"] = [
        is_bit_set(diary_vars[10], 1),
        is_bit_set(diary_vars[10], 2),
        is_bit_set(diary_vars[10], 3),
        is_bit_set(diary_vars[10], 4),
        is_bit_set(diary_vars[10], 5),
    ]
    result["Kourend & Kebos"]["Easy"] = [
        is_bit_set(diary_vars[11], 1),
        is_bit_set(diary_vars[11], 2),
        is_bit_set(diary_vars[11], 3),
        is_bit_set(diary_vars[11], 4),
        is_bit_set(diary_vars[11], 5),
        is_bit_set(diary_vars[11], 6),
        is_bit_set(diary_vars[11], 7),
        is_bit_set(diary_vars[11], 8),
        is_bit_set(diary_vars[11], 9),
        is_bit_set(diary_vars[11], 10),
        is_bit_set(diary_vars[11], 11),
        is_bit_set(diary_vars[11], 12),
    ]
    result["Kourend & Kebos"]["Medium"] = [
        is_bit_set(diary_vars[11], 25),
        is_bit_set(diary_vars[11], 13),
        is_bit_set(diary_vars[11], 14),
        is_bit_set(diary_vars[11], 15),
        is_bit_set(diary_vars[11], 21),
        is_bit_set(diary_vars[11], 16),
        is_bit_set(diary_vars[11], 17),
        is_bit_set(diary_vars[11], 18),
        is_bit_set(diary_vars[11], 19),
        is_bit_set(diary_vars[11], 22),
        is_bit_set(diary_vars[11], 20),
        is_bit_set(diary_vars[11], 23),
        is_bit_set(diary_vars[11], 24),
    ]
    result["Kourend & Kebos"]["Hard"] = [
        is_bit_set(diary_vars[11], 26),
        is_bit_set(diary_vars[11], 27),
        is_bit_set(diary_vars[11], 28),
        is_bit_set(diary_vars[11], 29),
        is_bit_set(diary_vars[11], 31),
        is_bit_set(diary_vars[11], 30),
        is_bit_set(diary_vars[12], 0),
        is_bit_set(diary_vars[12], 1),
        is_bit_set(diary_vars[12], 2),
        is_bit_set(diary_vars[12], 3),
    ]
    result["Kourend & Kebos"]["Elite"] = [
        is_bit_set(diary_vars[12], 4),
        is_bit_set(diary_vars[12], 5),
        is_bit_set(diary_vars[12], 6),
        is_bit_set(diary_vars[12], 7),
        is_bit_set(diary_vars[12], 8),
        is_bit_set(diary_vars[12], 9),
        is_bit_set(diary_vars[12], 10),
        is_bit_set(diary_vars[12], 11),
    ]
    result["Lumbridge & Draynor"]["Easy"] = [
        is_bit_set(diary_vars[13], 1),
        is_bit_set(diary_vars[13], 2),
        is_bit_set(diary_vars[13], 3),
        is_bit_set(diary_vars[13], 4),
        is_bit_set(diary_vars[13], 5),
        is_bit_set(diary_vars[13], 6),
        is_bit_set(diary_vars[13], 7),
        is_bit_set(diary_vars[13], 8),
        is_bit_set(diary_vars[13], 9),
        is_bit_set(diary_vars[13], 10),
        is_bit_set(diary_vars[13], 11),
        is_bit_set(diary_vars[13], 12),
    ]
    result["Lumbridge & Draynor"]["Medium"] = [
        is_bit_set(diary_vars[13], 13),
        is_bit_set(diary_vars[13], 14),
        is_bit_set(diary_vars[13], 15),
        is_bit_set(diary_vars[13], 16),
        is_bit_set(diary_vars[13], 17),
        is_bit_set(diary_vars[13], 18),
        is_bit_set(diary_vars[13], 19),
        is_bit_set(diary_vars[13], 20),
        is_bit_set(diary_vars[13], 21),
        is_bit_set(diary_vars[13], 22),
        is_bit_set(diary_vars[13], 23),
        is_bit_set(diary_vars[13], 24),
    ]
    result["Lumbridge & Draynor"]["Hard"] = [
        is_bit_set(diary_vars[13], 25),
        is_bit_set(diary_vars[13], 26),
        is_bit_set(diary_vars[13], 27),
        is_bit_set(diary_vars[13], 28),
        is_bit_set(diary_vars[13], 29),
        is_bit_set(diary_vars[13], 30),
        is_bit_set(diary_vars[13], 31),
        is_bit_set(diary_vars[14], 0),
        is_bit_set(diary_vars[14], 1),
        is_bit_set(diary_vars[14], 2),
        is_bit_set(diary_vars[14], 3),
    ]
    result["Lumbridge & Draynor"]["Elite"] = [
        is_bit_set(diary_vars[14], 4),
        is_bit_set(diary_vars[14], 5),
        is_bit_set(diary_vars[14], 6),
        is_bit_set(diary_vars[14], 7),
        is_bit_set(diary_vars[14], 8),
        is_bit_set(diary_vars[14], 9),
    ]
    result["Morytania"]["Easy"] = [
        is_bit_set(diary_vars[15], 1),
        is_bit_set(diary_vars[15], 2),
        is_bit_set(diary_vars[15], 3),
        is_bit_set(diary_vars[15], 4),
        is_bit_set(diary_vars[15], 5),
        is_bit_set(diary_vars[15], 6),
        is_bit_set(diary_vars[15], 7),
        is_bit_set(diary_vars[15], 8),
        is_bit_set(diary_vars[15], 9),
        is_bit_set(diary_vars[15], 10),
        is_bit_set(diary_vars[15], 11),
    ]
    result["Morytania"]["Medium"] = [
        is_bit_set(diary_vars[15], 12),
        is_bit_set(diary_vars[15], 13),
        is_bit_set(diary_vars[15], 14),
        is_bit_set(diary_vars[15], 15),
        is_bit_set(diary_vars[15], 16),
        is_bit_set(diary_vars[15], 17),
        is_bit_set(diary_vars[15], 18),
        is_bit_set(diary_vars[15], 19),
        is_bit_set(diary_vars[15], 20),
        is_bit_set(diary_vars[15], 21),
        is_bit_set(diary_vars[15], 22),
    ]
    result["Morytania"]["Hard"] = [
        is_bit_set(diary_vars[15], 23),
        is_bit_set(diary_vars[15], 24),
        is_bit_set(diary_vars[15], 25),
        is_bit_set(diary_vars[15], 26),
        is_bit_set(diary_vars[15], 27),
        is_bit_set(diary_vars[15], 28),
        is_bit_set(diary_vars[15], 29),
        is_bit_set(diary_vars[15], 30),
        is_bit_set(diary_vars[16], 1),
        is_bit_set(diary_vars[16], 2),
    ]
    result["Morytania"]["Elite"] = [
        is_bit_set(diary_vars[16], 3),
        is_bit_set(diary_vars[16], 4),
        is_bit_set(diary_vars[16], 5),
        is_bit_set(diary_vars[16], 6),
        is_bit_set(diary_vars[16], 7),
        is_bit_set(diary_vars[16], 8),
    ]
    result["Varrock"]["Easy"] = [
        is_bit_set(diary_vars[17], 1),
        is_bit_set(diary_vars[17], 2),
        is_bit_set(diary_vars[17], 3),
        is_bit_set(diary_vars[17], 4),
        is_bit_set(diary_vars[17], 5),
        is_bit_set(diary_vars[17], 6),
        is_bit_set(diary_vars[17], 7),
        is_bit_set(diary_vars[17], 8),
        is_bit_set(diary_vars[17], 9),
        is_bit_set(diary_vars[17], 10),
        is_bit_set(diary_vars[17], 11),
        is_bit_set(diary_vars[17], 12),
        is_bit_set(diary_vars[17], 13),
        is_bit_set(diary_vars[17], 14),
    ]
    result["Varrock"]["Medium"] = [
        is_bit_set(diary_vars[17], 15),
        is_bit_set(diary_vars[17], 16),
        is_bit_set(diary_vars[17], 18),
        is_bit_set(diary_vars[17], 19),
        is_bit_set(diary_vars[17], 20),
        is_bit_set(diary_vars[17], 21),
        is_bit_set(diary_vars[17], 22),
        is_bit_set(diary_vars[17], 23),
        is_bit_set(diary_vars[17], 24),
        is_bit_set(diary_vars[17], 25),
        is_bit_set(diary_vars[17], 26),
        is_bit_set(diary_vars[17], 27),
        is_bit_set(diary_vars[17], 28),
    ]
    result["Varrock"]["Hard"] = [
        is_bit_set(diary_vars[17], 29),
        is_bit_set(diary_vars[17], 30),
        is_bit_set(diary_vars[17], 31),
        is_bit_set(diary_vars[18], 0),
        is_bit_set(diary_vars[18], 1),
        is_bit_set(diary_vars[18], 2),
        is_bit_set(diary_vars[18], 3),
        is_bit_set(diary_vars[18], 4),
        is_bit_set(diary_vars[18], 5),
        is_bit_set(diary_vars[18], 6),
    ]
    result["Varrock"]["Elite"] = [
        is_bit_set(diary_vars[18], 7),
        is_bit_set(diary_vars[18], 8),
        is_bit_set(diary_vars[18], 9),
        is_bit_set(diary_vars[18], 10),
        is_bit_set(diary_vars[18], 11),
    ]
    result["Western Provinces"]["Easy"] = [
        is_bit_set(diary_vars[19], 1),
        is_bit_set(diary_vars[19], 2),
        is_bit_set(diary_vars[19], 3),
        is_bit_set(diary_vars[19], 4),
        is_bit_set(diary_vars[19], 5),
        is_bit_set(diary_vars[19], 6),
        is_bit_set(diary_vars[19], 7),
        is_bit_set(diary_vars[19], 8),
        is_bit_set(diary_vars[19], 9),
        is_bit_set(diary_vars[19], 10),
        is_bit_set(diary_vars[19], 11),
    ]
    result["Western Provinces"]["Medium"] = [
        is_bit_set(diary_vars[19], 12),
        is_bit_set(diary_vars[19], 13),
        is_bit_set(diary_vars[19], 14),
        is_bit_set(diary_vars[19], 15),
        is_bit_set(diary_vars[19], 16),
        is_bit_set(diary_vars[19], 17),
        is_bit_set(diary_vars[19], 18),
        is_bit_set(diary_vars[19], 19),
        is_bit_set(diary_vars[19], 20),
        is_bit_set(diary_vars[19], 21),
        is_bit_set(diary_vars[19], 22),
        is_bit_set(diary_vars[19], 23),
        is_bit_set(diary_vars[19], 24),
    ]
    result["Western Provinces"]["Hard"] = [
        is_bit_set(diary_vars[19], 25),
        is_bit_set(diary_vars[19], 26),
        is_bit_set(diary_vars[19], 27),
        is_bit_set(diary_vars[19], 28),
        is_bit_set(diary_vars[19], 29),
        is_bit_set(diary_vars[19], 30),
        is_bit_set(diary_vars[19], 31),
        is_bit_set(diary_vars[20], 0),
        is_bit_set(diary_vars[20], 1),
        is_bit_set(diary_vars[20], 2),
        is_bit_set(diary_vars[20], 3),
        is_bit_set(diary_vars[20], 4),
        is_bit_set(diary_vars[20], 5),
    ]
    result["Western Provinces"]["Elite"] = [
        is_bit_set(diary_vars[20], 6),
        is_bit_set(diary_vars[20], 7),
        is_bit_set(diary_vars[20], 8),
        is_bit_set(diary_vars[20], 9),
        is_bit_set(diary_vars[20], 12),
        is_bit_set(diary_vars[20], 13),
        is_bit_set(diary_vars[20], 14),
    ]
    result["Wilderness"]["Easy"] = [
        is_bit_set(diary_vars[21], 1),
        is_bit_set(diary_vars[21], 2),
        is_bit_set(diary_vars[21], 3),
        is_bit_set(diary_vars[21], 4),
        is_bit_set(diary_vars[21], 5),
        is_bit_set(diary_vars[21], 6),
        is_bit_set(diary_vars[21], 7),
        is_bit_set(diary_vars[21], 8),
        is_bit_set(diary_vars[21], 9),
        is_bit_set(diary_vars[21], 10),
        is_bit_set(diary_vars[21], 11),
        is_bit_set(diary_vars[21], 12),
    ]
    result["Wilderness"]["Medium"] = [
        is_bit_set(diary_vars[21], 13),
        is_bit_set(diary_vars[21], 14),
        is_bit_set(diary_vars[21], 15),
        is_bit_set(diary_vars[21], 16),
        is_bit_set(diary_vars[21], 18),
        is_bit_set(diary_vars[21], 19),
        is_bit_set(diary_vars[21], 20),
        is_bit_set(diary_vars[21], 21),
        is_bit_set(diary_vars[21], 22),
        is_bit_set(diary_vars[21], 23),
        is_bit_set(diary_vars[21], 24),
    ]
    result["Wilderness"]["Hard"] = [
        is_bit_set(diary_vars[21], 25),
        is_bit_set(diary_vars[21], 26),
        is_bit_set(diary_vars[21], 27),
        is_bit_set(diary_vars[21], 28),
        is_bit_set(diary_vars[21], 29),
        is_bit_set(diary_vars[21], 30),
        is_bit_set(diary_vars[21], 31),
        is_bit_set(diary_vars[22], 0),
        is_bit_set(diary_vars[22], 1),
        is_bit_set(diary_vars[22], 2),
    ]
    result["Wilderness"]["Elite"] = [
        is_bit_set(diary_vars[22], 3),
        is_bit_set(diary_vars[22], 5),
        is_bit_set(diary_vars[22], 7),
        is_bit_set(diary_vars[22], 8),
        is_bit_set(diary_vars[22], 9),
        is_bit_set(diary_vars[22], 10),
        is_bit_set(diary_vars[22], 11),
    ]
    # Additional parsing for other diaries can be added here similarly

    return result


# Example input
diary_vars = [
    -4195593,
    16383,
    -2,
    503,
    -524289,
    2047,
    -4259842,
    31,
    -2,
    4095,
    254,
    -2,
    4095,
    -2,
    1023,
    2147483646,
    510,
    -131074,
    4095,
    -2,
    29695,
    -131074,
    4015,
    5,
    1,
    1,
    1,
    1,
    1,
    1,
    5,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    5,
    1,
    1,
]

diary_vars2 = [
    -1576518921,
    0,
    117848,
    0,
    37814918,
    0,
    8520192,
    0,
    17962524,
    0,
    0,
    34603024,
    0,
    75698754,
    0,
    2136640,
    0,
    277446654,
    0,
    25090,
    0,
    2052,
    0,
    5,
    0,
    0,
    1,
    1,
    1,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    1,
    0,
    0,
    0,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
]


# Parsing the input
parsed_data = parse_diary_data(diary_vars)
print("Maxed")
print(parsed_data)
print("-----------------------------")
# Parsing the input
parsed_data = parse_diary_data(diary_vars2)
print("GIM")
print(parsed_data)