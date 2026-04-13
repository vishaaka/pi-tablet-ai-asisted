import json
import uuid
from copy import deepcopy
from datetime import datetime

from config.settings import data_dir, data_path

data_dir()
SCENES_PATH = data_path("scene_manifest.json")


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _read_json(path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _scene_store():
    data = _read_json(SCENES_PATH, [])
    return data if isinstance(data, list) else []


def _save_scene_store(items):
    _write_json(SCENES_PATH, items)


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
    return val.strip("_") or "scene"


def _default_canvas():
    return {
        "width": 1280,
        "height": 720,
        "background": "#ffffff",
    }


def _normalize_layer(layer: dict, order_index: int = 0) -> dict:
    layer = deepcopy(layer or {})
    layer_type = (layer.get("type") or "image").strip().lower()

    normalized = {
        "layer_id": layer.get("layer_id") or f"layer_{uuid.uuid4().hex[:8]}",
        "name": layer.get("name") or f"Katman {order_index + 1}",
        "type": layer_type,
        "x": int(layer.get("x", 0) or 0),
        "y": int(layer.get("y", 0) or 0),
        "w": int(layer.get("w", 200) or 200),
        "h": int(layer.get("h", 200) or 200),
        "z": int(layer.get("z", order_index * 10) or 0),
        "opacity": float(layer.get("opacity", 1) or 1),
        "visible": bool(layer.get("visible", True)),
    }

    if layer_type in ("image", "background", "avatar", "decor"):
        normalized["asset_id"] = layer.get("asset_id", "")
        normalized["src"] = layer.get("src", "")
        normalized["fit"] = layer.get("fit", "contain")

    elif layer_type == "text":
        normalized["text"] = layer.get("text", "")
        normalized["font_size"] = int(layer.get("font_size", 42) or 42)
        normalized["font_weight"] = layer.get("font_weight", "700")
        normalized["color"] = layer.get("color", "#111111")
        normalized["align"] = layer.get("align", "left")

    elif layer_type == "guide":
        normalized["text"] = layer.get("text", "")
        normalized["font_size"] = int(layer.get("font_size", 30) or 30)
        normalized["font_weight"] = layer.get("font_weight", "600")
        normalized["color"] = layer.get("color", "#2563eb")
        normalized["align"] = layer.get("align", "left")

    else:
        normalized["meta"] = layer.get("meta", {})

    return normalized


def _normalize_scene(payload: dict) -> dict:
    payload = deepcopy(payload or {})

    target_word = (payload.get("target_word") or "").strip()
    name = (payload.get("name") or target_word or "Yeni Sahne").strip()
    pronunciation = (payload.get("pronunciation") or "").strip()

    raw_layers = payload.get("layers") or []
    if not isinstance(raw_layers, list):
        raw_layers = []

    layers = [_normalize_layer(layer, i) for i, layer in enumerate(raw_layers)]
    layers = sorted(layers, key=lambda x: int(x.get("z", 0)))

    scene = {
        "scene_id": payload.get("scene_id") or f"{_slug(name)}_{uuid.uuid4().hex[:6]}",
        "name": name,
        "target_word": target_word,
        "pronunciation": pronunciation,
        "notes": (payload.get("notes") or "").strip(),
        "status": payload.get("status") or "active",
        "canvas": payload.get("canvas") or _default_canvas(),
        "layers": layers,
        "created_at": payload.get("created_at") or _now_iso(),
        "updated_at": _now_iso(),
    }
    return scene


def list_scenes(q: str = "", target_word: str = "", status: str = "") -> list[dict]:
    items = _scene_store()

    q = (q or "").strip().lower()
    target_word = (target_word or "").strip().lower()
    status = (status or "").strip().lower()

    out = []
    for item in items:
        if q:
            blob = " ".join([
                str(item.get("name", "")),
                str(item.get("target_word", "")),
                str(item.get("pronunciation", "")),
                str(item.get("notes", "")),
            ]).lower()
            if q not in blob:
                continue

        if target_word and target_word != str(item.get("target_word", "")).lower():
            continue

        if status and status != str(item.get("status", "")).lower():
            continue

        out.append(item)

    out.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return out


def get_scene(scene_id: str):
    for item in _scene_store():
        if item.get("scene_id") == scene_id:
            return item
    return None


def create_scene(payload: dict) -> dict:
    items = _scene_store()
    scene = _normalize_scene(payload)

    if get_scene(scene["scene_id"]):
        raise ValueError("Aynı scene_id zaten var")

    items.append(scene)
    _save_scene_store(items)
    return scene


def update_scene(scene_id: str, payload: dict) -> dict:
    items = _scene_store()

    for idx, item in enumerate(items):
        if item.get("scene_id") == scene_id:
            merged = deepcopy(item)
            merged.update(payload or {})
            merged["scene_id"] = scene_id
            merged["created_at"] = item.get("created_at") or _now_iso()
            updated = _normalize_scene(merged)
            items[idx] = updated
            _save_scene_store(items)
            return updated

    raise ValueError("Sahne bulunamadı")


def delete_scene(scene_id: str) -> dict:
    items = _scene_store()
    kept = []
    found = None

    for item in items:
        if item.get("scene_id") == scene_id:
            found = item
        else:
            kept.append(item)

    if not found:
        raise ValueError("Sahne bulunamadı")

    _save_scene_store(kept)
    return {"ok": True, "deleted_scene_id": scene_id}


def scene_stats() -> dict:
    items = _scene_store()
    active_count = sum(1 for x in items if x.get("status") == "active")
    total_layers = sum(len(x.get("layers") or []) for x in items)

    return {
        "total_scenes": len(items),
        "active_scenes": active_count,
        "total_layers": total_layers,
    }


def build_scene_payload(payload: dict) -> dict:
    scene = _normalize_scene(payload)

    return {
        "screen": "layered_speech_scene",
        "scene": {
            "scene_id": scene["scene_id"],
            "name": scene["name"],
            "target_word": scene["target_word"],
            "pronunciation": scene["pronunciation"],
            "notes": scene["notes"],
            "canvas": scene["canvas"],
            "layers": scene["layers"],
        }
    }
