import json
import os
from datetime import datetime

ATTENTION_MEMORY_PATH = "data/attention_memory.json"


def _load():
    if not os.path.exists(ATTENTION_MEMORY_PATH):
        return {}

    try:
        with open(ATTENTION_MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    os.makedirs("data", exist_ok=True)
    with open(ATTENTION_MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_attention(asset_id: str, seconds: float, label: str = ""):
    data = _load()

    item = data.get(asset_id, {
        "asset_id": asset_id,
        "label": label,
        "total_attention": 0.0,
        "hits": 0,
        "avg_attention": 0.0,
        "last_seen": ""
    })

    item["total_attention"] += float(seconds)
    item["hits"] += 1
    item["avg_attention"] = item["total_attention"] / item["hits"]
    item["last_seen"] = datetime.now().isoformat()

    if label:
        item["label"] = label

    data[asset_id] = item
    _save(data)

    return item


def get_attention_score(asset_id: str):
    data = _load()
    item = data.get(asset_id)
    if not item:
        return 0.0

    avg = float(item.get("avg_attention", 0))
    hits = int(item.get("hits", 0))

    return min(40.0, avg * 5 + hits * 0.8)


def get_label_attention_boost(label: str):
    data = _load()

    total = 0.0
    hits = 0

    for item in data.values():
        if item.get("label", "").lower() == label.lower():
            total += float(item.get("avg_attention", 0))
            hits += 1

    if hits == 0:
        return 0.0

    avg = total / hits
    return min(35.0, avg * 4)