import json
import os
from copy import deepcopy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "db.json")


def _read_db():
    if not os.path.exists(DB_PATH):
        return {"assets": []}

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"assets": []}
            data.setdefault("assets", [])
            return data
    except Exception:
        return {"assets": []}


def list_asset_history(limit: int = 100):
    """
    Ayrı history dosyası yerine db.json içindeki assetleri
    updated_at / created_at bazlı geçmiş gibi gösterir.
    """
    assets = deepcopy(_read_db().get("assets", []))

    for item in assets:
        item["label_tr"] = item.get("label_tr") or item.get("label") or ""
        item["image_path"] = item.get("image_path", "")
        item["used_count"] = int(item.get("used_count", 0) or 0)
        item["preferred"] = bool(item.get("preferred", False))

    assets.sort(
        key=lambda x: x.get("updated_at") or x.get("created_at") or "",
        reverse=True
    )

    return assets[:limit]