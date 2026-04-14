import base64
import json
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any

from config.settings import assets_dir, data_path

ASSETS_DIR = assets_dir()
DB_PATH = data_path("db.json")


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="microseconds")


def _read_db() -> dict:
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


def _write_db(data: dict):
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _assets() -> list[dict]:
    return _read_db().get("assets", [])


def _save_assets(items: list[dict]):
    db = _read_db()
    db["assets"] = items
    _write_db(db)


def _slug(text: str) -> str:
    text = (text or "").strip().lower()
    repl = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
    }
    for k, v in repl.items():
        text = text.replace(k, v)

    out = []
    for ch in text:
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "-", "_"):
            out.append("_")

    val = "".join(out)
    while "__" in val:
        val = val.replace("__", "_")
    return val.strip("_") or "asset"


def _normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    return []


def _normalize_image_path(path: str) -> str:
    if not path:
        return ""
    path = str(path).replace("\\", "/")
    if path.startswith("/asset_files/"):
        return path
    if path.startswith("assets/"):
        return "/asset_files/" + path.replace("assets/", "", 1)
    if path.startswith("/assets/"):
        return "/asset_files/" + path.replace("/assets/", "", 1)
    return path


def _normalize_item(item: dict) -> dict:
    item = deepcopy(item)

    item["label_tr"] = item.get("label_tr") or item.get("label") or ""
    item["label_en"] = item.get("label_en") or item["label_tr"]

    item["tags_tr"] = _normalize_list(item.get("tags_tr") or item.get("tags"))
    item["tags_en"] = _normalize_list(item.get("tags_en") or item["tags_tr"])

    item["interests_tr"] = _normalize_list(item.get("interests_tr") or item.get("interests"))
    item["interests_en"] = _normalize_list(item.get("interests_en") or item["interests_tr"])

    item["label"] = item["label_tr"]
    item["tags"] = item["tags_tr"]
    item["interests"] = item["interests_tr"]

    item["image_path"] = _normalize_image_path(item.get("image_path", ""))
    item["status"] = item.get("status", "active")
    item["preferred"] = bool(item.get("preferred", False))
    item["used_count"] = int(item.get("used_count", 0) or 0)

    return item


def _save_base64_image(label_tr: str, image_base64: str) -> str:
    if "," not in image_base64:
        raise ValueError("Geçersiz image_base64")

    header, encoded = image_base64.split(",", 1)

    ext = ".png"
    h = header.lower()
    if "jpeg" in h or "jpg" in h:
        ext = ".jpg"
    elif "webp" in h:
        ext = ".webp"

    raw = base64.b64decode(encoded)
    filename = f"{_slug(label_tr)}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"
    full_path = ASSETS_DIR / filename

    with full_path.open("wb") as f:
        f.write(raw)

    return f"/asset_files/{filename}"


def create_asset(payload: dict) -> dict:
    items = _assets()

    label_tr = (payload.get("label_tr") or payload.get("label") or "").strip()
    if not label_tr:
        raise ValueError("label_tr gerekli")

    image_base64 = payload.get("image_base64")
    if not image_base64:
        raise ValueError("image_base64 gerekli")

    item = {
        "asset_id": f"ast_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "label_tr": label_tr,
        "label_en": payload.get("label_en", label_tr),
        "tags_tr": _normalize_list(payload.get("tags_tr") or payload.get("tags")),
        "tags_en": _normalize_list(payload.get("tags_en")),
        "interests_tr": _normalize_list(payload.get("interests_tr") or payload.get("interests")),
        "interests_en": _normalize_list(payload.get("interests_en")),
        "image_path": _save_base64_image(label_tr, image_base64),
        "preferred": bool(payload.get("preferred", False)),
        "source": payload.get("source", "manual"),
        "status": "active",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "used_count": 0,
        "last_used_at": "",
        "notes": payload.get("notes", ""),
    }

    items.append(item)
    _save_assets(items)
    return _normalize_item(item)


def list_assets(q="", label="", tag="", interest="", status=""):
    items = [_normalize_item(x) for x in _assets()]
    out = []

    for item in items:
        if status and item.get("status") != status:
            continue
        out.append(item)

    out.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return out


def get_asset(asset_id: str):
    for item in _assets():
        if item.get("asset_id") == asset_id:
            return _normalize_item(item)
    return None


def update_asset(asset_id: str, payload: dict):
    items = _assets()

    for i, item in enumerate(items):
        if item.get("asset_id") == asset_id:
            item = _normalize_item(item)
            item["label_tr"] = payload.get("label_tr", item["label_tr"])
            item["tags_tr"] = _normalize_list(payload.get("tags_tr") or item["tags_tr"])
            item["interests_tr"] = _normalize_list(payload.get("interests_tr") or item["interests_tr"])
            item["notes"] = payload.get("notes", item.get("notes", ""))
            item["preferred"] = bool(payload.get("preferred", item.get("preferred", False)))
            item["updated_at"] = _now_iso()

            items[i] = item
            _save_assets(items)
            return _normalize_item(item)

    raise ValueError("Asset bulunamadı")


def asset_stats():
    items = [_normalize_item(x) for x in _assets()]
    return {
        "total_assets": len(items),
        "preferred_assets": sum(1 for x in items if x.get("preferred")),
        "active_assets": sum(1 for x in items if x.get("status") == "active"),
        "total_used_count": sum(int(x.get("used_count", 0)) for x in items),
    }


def increment_asset_usage(asset_id: str, count: int = 1):
    items = _assets()

    for i, item in enumerate(items):
        if item.get("asset_id") == asset_id:
            item["used_count"] = int(item.get("used_count", 0)) + count
            item["last_used_at"] = _now_iso()
            item["updated_at"] = _now_iso()
            items[i] = item
            _save_assets(items)
            return _normalize_item(item)

    raise ValueError("Asset bulunamadı")
