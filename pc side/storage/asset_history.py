import json
from copy import deepcopy

from config.settings import data_path

DB_PATH = data_path("db.json")


def _read_db():
    if not DB_PATH.exists():
        return {"assets": []}

    try:
        with DB_PATH.open("r", encoding="utf-8") as f:
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
