from tinydb import TinyDB
from datetime import datetime
import os

os.makedirs("data", exist_ok=True)

db = TinyDB("data/command_queue.json")
queue = db.table("queue")


def push_command(action: str, payload: dict | None = None):
    item = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "payload": payload or {},
        "status": "pending"
    }
    queue.insert(item)
    return item


def get_pending_commands():
    return [x for x in queue.all() if x.get("status") == "pending"]