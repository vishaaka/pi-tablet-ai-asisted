from tinydb import TinyDB
from datetime import datetime
from config.settings import data_dir, data_path
from storage.mode_manager import get_mode

data_dir()

def get_queue_db():
    mode = get_mode()
    path = data_path(f"{mode}_command_queue.json")
    if not path.exists():
        with path.open("w", encoding="utf-8") as f:
            f.write("{}")
    return TinyDB(str(path))

def push_command(action: str, payload: dict | None = None):
    db = get_queue_db()
    queue = db.table("queue")
    item = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "payload": payload or {},
        "status": "pending",
        "mode": get_mode()
    }
    queue.insert(item)
    return item

def get_pending_commands():
    db = get_queue_db()
    queue = db.table("queue")
    return [x for x in queue.all() if x.get("status") == "pending"]
