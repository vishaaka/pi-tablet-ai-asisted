import json
from datetime import datetime

from config.settings import data_dir, data_path

DRAFTS_FILE = data_path("drafts.json")


def ensure_drafts_file():
    data_dir()

    if not DRAFTS_FILE.exists():
        with DRAFTS_FILE.open("w", encoding="utf-8") as f:
            json.dump({"drafts": []}, f, ensure_ascii=False, indent=2)


def load_drafts():
    ensure_drafts_file()

    with DRAFTS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("drafts", [])


def save_drafts(drafts):
    with DRAFTS_FILE.open("w", encoding="utf-8") as f:
        json.dump({"drafts": drafts}, f, ensure_ascii=False, indent=2)


def add_draft(name: str, payload: dict):
    drafts = load_drafts()

    item = {
        "name": name.strip(),
        "payload": payload,
        "updated_at": datetime.now().isoformat()
    }

    replaced = False

    for i, d in enumerate(drafts):
        if d.get("name", "").strip().lower() == name.strip().lower():
            drafts[i] = item
            replaced = True
            break

    if not replaced:
        drafts.append(item)

    save_drafts(drafts)
    return item


def get_all_drafts():
    return load_drafts()


def get_draft(name: str):
    drafts = load_drafts()

    for d in drafts:
        if d.get("name", "").strip().lower() == name.strip().lower():
            return d

    return None


def delete_draft(name: str):
    drafts = load_drafts()
    new_drafts = [
        d for d in drafts
        if d.get("name", "").strip().lower() != name.strip().lower()
    ]

    save_drafts(new_drafts)
    return {"ok": True, "deleted": name}
