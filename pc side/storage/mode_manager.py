import json
from config.settings import data_dir, data_path, get_settings

MODE_FILE = data_path("system_mode.json")
DEFAULT_MODE = get_settings()["mode"]["default"]
ALLOWED_MODES = tuple(get_settings()["mode"]["allowed"])


def ensure_mode_file():
    data_dir()

    if not MODE_FILE.exists():
        with MODE_FILE.open("w", encoding="utf-8") as f:
            json.dump({"mode": DEFAULT_MODE}, f, ensure_ascii=False, indent=2)


def get_mode():
    ensure_mode_file()

    with MODE_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    mode = data.get("mode", DEFAULT_MODE)

    if mode not in ALLOWED_MODES:
        mode = DEFAULT_MODE

    return mode


def set_mode(mode: str):
    if mode not in ALLOWED_MODES:
        raise ValueError("Geçersiz mod")

    ensure_mode_file()

    with MODE_FILE.open("w", encoding="utf-8") as f:
        json.dump({"mode": mode}, f, ensure_ascii=False, indent=2)

    return {"mode": mode}
