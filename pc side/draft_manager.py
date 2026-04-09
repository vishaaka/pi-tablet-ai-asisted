import json
import os
from datetime import datetime

DRAFTS_FILE = "data/drafts.json"


def ensure_drafts_file():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(DRAFTS_FILE):
        with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
            json.dump({"drafts": []}, f, ensure_ascii=False, indent=2)


def load_drafts():
    ensure_drafts_file()

    with open(DRAFTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("drafts", [])


def save_drafts(drafts):
    with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
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