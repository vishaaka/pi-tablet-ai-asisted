import json
import os

MODE_FILE = "data/system_mode.json"


def ensure_mode_file():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(MODE_FILE):
        with open(MODE_FILE, "w", encoding="utf-8") as f:
            json.dump({"mode": "prod"}, f, ensure_ascii=False, indent=2)


def get_mode():
    ensure_mode_file()

    with open(MODE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    mode = data.get("mode", "prod")

    if mode not in ("prod", "test"):
        mode = "prod"

    return mode


def set_mode(mode: str):
    if mode not in ("prod", "test"):
        raise ValueError("Geçersiz mod")

    ensure_mode_file()

    with open(MODE_FILE, "w", encoding="utf-8") as f:
        json.dump({"mode": mode}, f, ensure_ascii=False, indent=2)

    return {"mode": mode}