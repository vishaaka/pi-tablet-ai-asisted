import json
import os
from datetime import datetime
from typing import Any

HISTORY_PATH = "data/asset_history.jsonl"


def ensure_asset_history() -> None:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            f.write("")


def append_asset_history(action: str, asset_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    ensure_asset_history()

    item = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "asset_id": asset_id,
        "payload": payload or {},
    }

    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return item


def list_asset_history(limit: int = 100) -> list[dict[str, Any]]:
    ensure_asset_history()

    items: list[dict[str, Any]] = []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    items.append(data)
            except Exception:
                continue

    items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return items[:limit]