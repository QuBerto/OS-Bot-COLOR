import json
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def save_data(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        json.dump(data, f, indent=4)


@app.route("/api/player_status/", methods=["POST"])
def update_player_status():
    data = request.json
    save_data("player_status.json", data)
    return jsonify({"status": "success"}), 200


@app.route("/api/monster_kills/", methods=["POST"])
def update_monster_kills():
    data = request.json
    save_data("monster_kills.json", data)
    return jsonify({"status": "success"}), 200


@app.route("/api/level_change_updates/", methods=["POST"])
def update_level_change_updates():
    data = request.json
    save_data("level_change_updates.json", data)
    return jsonify({"status": "success"}), 200


@app.route("/api/equipped_items/", methods=["POST"])
def update_equipped_items():
    data = request.json
    save_data("equipped_items.json", data)
    return jsonify({"status": "success"}), 200


@app.route("/api/inventory_items/", methods=["POST"])
def update_inventory_items():
    data = request.json
    save_data("inventory_items.json", data)
    return jsonify({"status": "success"}), 200


@app.route("/api/bank/", methods=["POST"])
def update_bank_items():
    data = request.json
    save_data("bank_items.json", data)
    return jsonify({"status": "success"}), 200


@app.route("/api/quest_info/", methods=["POST"])
def update_quest_info():
    data = request.json
    save_data("quest_info.json", data)
    return jsonify({"status": "success"}), 200


@app.route("/api/login_state/", methods=["POST"])
def update_login_state():
    data = request.json
    save_data("login_state.json", data)
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9420)
