import base64
import json
import mimetypes
import os
import re
import shutil
from datetime import datetime
from typing import Any

from asset_history import append_asset_history
from dictionary_bridge import (
    best_en_to_tr,
    best_tr_to_en,
    normalize_term_en,
    normalize_term_tr,
)

ASSET_DIR = "assets"
MANIFEST_PATH = "asset_manifest.jsonl"


def ensure_asset_storage() -> None:
    os.makedirs(ASSET_DIR, exist_ok=True)
    if not os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            f.write("")


def _now_iso() -> str:
    return datetime.now().isoformat()


def _asset_id() -> str:
    return datetime.now().strftime("ast_%Y%m%d_%H%M%S_%f")


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    replacements = {
        "ı": "i",
        "ğ": "g",
        "ü": "u",
        "ş": "s",
        "ö": "o",
        "ç": "c",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)

    value = re.sub(r"[^a-z0-9._-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "asset"


def _parse_csv_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        raw_items = value
    else:
        raw_items = str(value).split(",")

    cleaned = []
    seen = set()

    for item in raw_items:
        text = str(item).strip()
        if not text:
            continue

        key = text.lower()
        if key in seen:
            continue

        cleaned.append(text)
        seen.add(key)

    return cleaned


def _normalize_list_tr(values: list[str]) -> list[str]:
    result = []
    seen = set()

    for value in values:
        n = normalize_term_tr(value)
        if not n or n in seen:
            continue
        result.append(n)
        seen.add(n)

    return result


def _normalize_list_en(values: list[str]) -> list[str]:
    result = []
    seen = set()

    for value in values:
        n = normalize_term_en(value)
        if not n or n in seen:
            continue
        result.append(n)
        seen.add(n)

    return result


def _read_manifest() -> list[dict[str, Any]]:
    ensure_asset_storage()

    items: list[dict[str, Any]] = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            try:
                item = json.loads(raw)
                if isinstance(item, dict):
                    items.append(_normalize_manifest_item(item))
            except Exception:
                continue
    return items


def _write_manifest(items: list[dict[str, Any]]) -> None:
    ensure_asset_storage()
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def _normalize_manifest_item(item: dict[str, Any]) -> dict[str, Any]:
    label_tr = item.get("label_tr") or item.get("label") or ""
    label_en = item.get("label_en") or ""

    if not label_en and label_tr:
        label_en = best_tr_to_en(label_tr, fallback=label_tr)

    if not label_tr and label_en:
        label_tr = best_en_to_tr(label_en, fallback=label_en)

    tags_tr = item.get("tags_tr")
    tags_en = item.get("tags_en")
    interests_tr = item.get("interests_tr")
    interests_en = item.get("interests_en")

    if tags_tr is None:
        tags_tr = item.get("tags", [])
    if tags_en is None:
        tags_en = [best_tr_to_en(x, fallback=x) for x in (tags_tr or [])]

    if interests_tr is None:
        interests_tr = item.get("interests", [])
    if interests_en is None:
        interests_en = [best_tr_to_en(x, fallback=x) for x in (interests_tr or [])]

    source_query_tr = item.get("source_query_tr", "")
    source_query_en = item.get("source_query_en", "") or item.get("source_query", "")

    if not source_query_en and source_query_tr:
        source_query_en = best_tr_to_en(source_query_tr, fallback=source_query_tr)

    if not source_query_tr and source_query_en:
        source_query_tr = best_en_to_tr(source_query_en, fallback=source_query_en)

    normalized = {
        "asset_id": item.get("asset_id", ""),
        "label_tr": normalize_term_tr(label_tr),
        "label_en": normalize_term_en(label_en),
        "tags_tr": _normalize_list_tr(_parse_csv_list(tags_tr)),
        "tags_en": _normalize_list_en(_parse_csv_list(tags_en)),
        "interests_tr": _normalize_list_tr(_parse_csv_list(interests_tr)),
        "interests_en": _normalize_list_en(_parse_csv_list(interests_en)),
        "image_path": item.get("image_path", ""),
        "preferred": bool(item.get("preferred", False)),
        "source": item.get("source", "manual"),
        "source_query_tr": normalize_term_tr(source_query_tr),
        "source_query_en": normalize_term_en(source_query_en),
        "source_url": item.get("source_url", ""),
        "external_id": item.get("external_id", ""),
        "status": item.get("status", "active"),
        "created_at": item.get("created_at", ""),
        "updated_at": item.get("updated_at", ""),
        "used_count": int(item.get("used_count", 0) or 0),
        "last_used_at": item.get("last_used_at", ""),
        "notes": item.get("notes", ""),
        # geriye uyumluluk yardımcı alanları
        "label": normalize_term_tr(label_tr),
        "tags": _normalize_list_tr(_parse_csv_list(tags_tr)),
        "interests": _normalize_list_tr(_parse_csv_list(interests_tr)),
        "source_query": normalize_term_en(source_query_en),
    }

    return normalized


def list_assets(
    q: str = "",
    label: str = "",
    tag: str = "",
    interest: str = "",
    status: str = "",
) -> list[dict[str, Any]]:
    items = _read_manifest()

    q_n = normalize_term_tr(q)
    q_en = normalize_term_en(best_tr_to_en(q, fallback=q)) if q else ""
    label_n = normalize_term_tr(label)
    label_en = normalize_term_en(best_tr_to_en(label, fallback=label)) if label else ""
    tag_n = normalize_term_tr(tag)
    tag_en = normalize_term_en(best_tr_to_en(tag, fallback=tag)) if tag else ""
    interest_n = normalize_term_tr(interest)
    interest_en = normalize_term_en(best_tr_to_en(interest, fallback=interest)) if interest else ""
    status_n = (status or "").strip().lower()

    def match(item: dict[str, Any]) -> bool:
        text_blob = " ".join(
            [
                item.get("label_tr", ""),
                item.get("label_en", ""),
                " ".join(item.get("tags_tr", [])),
                " ".join(item.get("tags_en", [])),
                " ".join(item.get("interests_tr", [])),
                " ".join(item.get("interests_en", [])),
                str(item.get("source", "")).lower(),
                item.get("source_query_tr", ""),
                item.get("source_query_en", ""),
                str(item.get("source_url", "")).lower(),
                str(item.get("notes", "")).lower(),
            ]
        )

        if q and not any(x and x in text_blob for x in [q_n, q_en]):
            return False

        if label and not (
            item.get("label_tr", "") == label_n or
            item.get("label_en", "") == label_en
        ):
            return False

        if tag and not (
            tag_n in item.get("tags_tr", []) or
            tag_en in item.get("tags_en", [])
        ):
            return False

        if interest and not (
            interest_n in item.get("interests_tr", []) or
            interest_en in item.get("interests_en", [])
        ):
            return False

        if status_n and status_n != str(item.get("status", "")).lower():
            return False

        return True

    result = [x for x in items if match(x)]
    result.sort(
        key=lambda x: (
            x.get("status", "") != "active",
            -(1 if x.get("preferred") else 0),
            x.get("label_tr", "").lower(),
            x.get("created_at", ""),
        )
    )
    return result


def get_asset(asset_id: str) -> dict[str, Any] | None:
    items = _read_manifest()
    for item in items:
        if item.get("asset_id") == asset_id:
            return item
    return None


def find_asset_by_source_url(source_url: str) -> dict[str, Any] | None:
    source_url = (source_url or "").strip()
    if not source_url:
        return None

    items = _read_manifest()
    for item in items:
        if (item.get("source_url") or "").strip() == source_url:
            return item
    return None


def _infer_extension_from_data_url(image_base64: str) -> str:
    head = image_base64.split(",", 1)[0].lower()

    if "image/png" in head:
        return ".png"
    if "image/webp" in head:
        return ".webp"
    if "image/jpeg" in head or "image/jpg" in head:
        return ".jpg"

    return ".png"


def _guess_extension_from_content_type(content_type: str) -> str:
    if not content_type:
        return ".png"

    guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
    if guessed == ".jpe":
        return ".jpg"
    return guessed or ".png"


def _save_base64_image(image_base64: str, suggested_name: str) -> str:
    if "," not in image_base64:
        raise ValueError("Geçersiz base64 veri")

    _, encoded = image_base64.split(",", 1)
    ext = _infer_extension_from_data_url(image_base64)

    file_name = f"{_slugify(suggested_name)}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"
    full_path = os.path.join(ASSET_DIR, file_name)

    binary = base64.b64decode(encoded)
    with open(full_path, "wb") as f:
        f.write(binary)

    return full_path.replace("\\", "/")


def save_binary_image(binary: bytes, content_type: str, suggested_name: str) -> str:
    ensure_asset_storage()

    ext = _guess_extension_from_content_type(content_type)
    file_name = f"{_slugify(suggested_name)}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"
    full_path = os.path.join(ASSET_DIR, file_name)

    with open(full_path, "wb") as f:
        f.write(binary)

    return full_path.replace("\\", "/")


def _prepare_image_path(
    label_tr: str,
    image_path: str,
    image_base64: str | None,
    copy_source_file: bool = True,
) -> str:
    ensure_asset_storage()

    if image_base64:
        return _save_base64_image(image_base64, label_tr)

    if not image_path:
        raise ValueError("Görsel seçilmedi")

    image_path = image_path.strip()

    if not os.path.exists(image_path):
        raise ValueError("Görsel dosyası bulunamadı")

    normalized_asset_dir = os.path.abspath(ASSET_DIR)
    normalized_image_path = os.path.abspath(image_path)

    if not copy_source_file and normalized_image_path.startswith(normalized_asset_dir):
        return image_path.replace("\\", "/")

    ext = os.path.splitext(image_path)[1] or ".png"
    dest_name = f"{_slugify(label_tr)}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"
    dest_path = os.path.join(ASSET_DIR, dest_name)
    shutil.copy2(image_path, dest_path)

    return dest_path.replace("\\", "/")


def _build_asset_item(payload: dict[str, Any], final_image_path: str) -> dict[str, Any]:
    label_tr = normalize_term_tr(payload.get("label_tr") or payload.get("label") or "")
    label_en = normalize_term_en(payload.get("label_en") or best_tr_to_en(label_tr, fallback=label_tr))

    tags_tr = _normalize_list_tr(_parse_csv_list(payload.get("tags_tr") or payload.get("tags")))
    tags_en_input = _parse_csv_list(payload.get("tags_en"))
    if tags_en_input:
        tags_en = _normalize_list_en(tags_en_input)
    else:
        tags_en = _normalize_list_en([best_tr_to_en(x, fallback=x) for x in tags_tr])

    interests_tr = _normalize_list_tr(_parse_csv_list(payload.get("interests_tr") or payload.get("interests")))
    interests_en_input = _parse_csv_list(payload.get("interests_en"))
    if interests_en_input:
        interests_en = _normalize_list_en(interests_en_input)
    else:
        interests_en = _normalize_list_en([best_tr_to_en(x, fallback=x) for x in interests_tr])

    source_query_tr = normalize_term_tr(payload.get("source_query_tr") or "")
    source_query_en = normalize_term_en(payload.get("source_query_en") or payload.get("source_query") or "")
    if not source_query_en and source_query_tr:
        source_query_en = normalize_term_en(best_tr_to_en(source_query_tr, fallback=source_query_tr))
    if not source_query_tr and source_query_en:
        source_query_tr = normalize_term_tr(best_en_to_tr(source_query_en, fallback=source_query_en))

    item = {
        "asset_id": _asset_id(),
        "label_tr": label_tr,
        "label_en": label_en,
        "tags_tr": tags_tr,
        "tags_en": tags_en,
        "interests_tr": interests_tr,
        "interests_en": interests_en,
        "image_path": final_image_path,
        "preferred": bool(payload.get("preferred", False)),
        "source": str(payload.get("source", "manual") or "manual").strip(),
        "source_query_tr": source_query_tr,
        "source_query_en": source_query_en,
        "source_url": str(payload.get("source_url", "")).strip(),
        "external_id": str(payload.get("external_id", "")).strip(),
        "status": "active",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "used_count": 0,
        "last_used_at": "",
        "notes": str(payload.get("notes", "")).strip(),
        # geriye uyumluluk
        "label": label_tr,
        "tags": tags_tr,
        "interests": interests_tr,
        "source_query": source_query_en,
    }

    return item


def create_asset(payload: dict[str, Any], copy_source_file: bool = True) -> dict[str, Any]:
    ensure_asset_storage()

    label_tr = normalize_term_tr(payload.get("label_tr") or payload.get("label") or "")
    label_en = normalize_term_en(payload.get("label_en") or "")

    if not label_tr and label_en:
        label_tr = best_en_to_tr(label_en, fallback=label_en)
    if not label_en and label_tr:
        label_en = best_tr_to_en(label_tr, fallback=label_tr)

    if not label_tr:
        raise ValueError("label_tr boş olamaz")

    payload = dict(payload)
    payload["label_tr"] = label_tr
    payload["label_en"] = label_en

    source_url = str(payload.get("source_url", "")).strip()
    if source_url:
        existing = find_asset_by_source_url(source_url)
        if existing:
            return existing

    image_path = str(payload.get("image_path", "")).strip()
    image_base64 = payload.get("image_base64")

    final_image_path = _prepare_image_path(
        label_tr=label_tr,
        image_path=image_path,
        image_base64=image_base64,
        copy_source_file=copy_source_file,
    )

    item = _build_asset_item(payload, final_image_path)

    items = _read_manifest()
    items.append(item)
    _write_manifest(items)

    append_asset_history(
        action="create",
        asset_id=item["asset_id"],
        payload={
            "label_tr": item["label_tr"],
            "label_en": item["label_en"],
            "image_path": item["image_path"],
            "source": item["source"],
            "source_url": item["source_url"],
            "tags_tr": item["tags_tr"],
            "tags_en": item["tags_en"],
            "interests_tr": item["interests_tr"],
            "interests_en": item["interests_en"],
        },
    )

    return item


def create_asset_from_saved_path(
    image_path: str,
    label: str = "",
    label_tr: str = "",
    label_en: str = "",
    tags: str | list[str] | None = None,
    tags_tr: str | list[str] | None = None,
    tags_en: str | list[str] | None = None,
    interests: str | list[str] | None = None,
    interests_tr: str | list[str] | None = None,
    interests_en: str | list[str] | None = None,
    preferred: bool = False,
    source: str = "manual",
    source_query: str = "",
    source_query_tr: str = "",
    source_query_en: str = "",
    source_url: str = "",
    external_id: str = "",
    notes: str = "",
) -> dict[str, Any]:
    payload = {
        "label": label,
        "label_tr": label_tr,
        "label_en": label_en,
        "tags": tags or [],
        "tags_tr": tags_tr or [],
        "tags_en": tags_en or [],
        "interests": interests or [],
        "interests_tr": interests_tr or [],
        "interests_en": interests_en or [],
        "preferred": preferred,
        "source": source,
        "source_query": source_query,
        "source_query_tr": source_query_tr,
        "source_query_en": source_query_en,
        "source_url": source_url,
        "external_id": external_id,
        "notes": notes,
        "image_path": image_path,
    }
    return create_asset(payload, copy_source_file=False)


def update_asset(asset_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    items = _read_manifest()
    updated_item = None

    for item in items:
        if item.get("asset_id") != asset_id:
            continue

        if "label_tr" in payload or "label" in payload:
            new_label_tr = normalize_term_tr(payload.get("label_tr") or payload.get("label") or "")
            if not new_label_tr:
                raise ValueError("label_tr boş olamaz")
            item["label_tr"] = new_label_tr
            item["label"] = new_label_tr

            if "label_en" not in payload:
                item["label_en"] = best_tr_to_en(new_label_tr, fallback=new_label_tr)

        if "label_en" in payload:
            item["label_en"] = normalize_term_en(payload.get("label_en", ""))

        if "tags_tr" in payload or "tags" in payload:
            item["tags_tr"] = _normalize_list_tr(_parse_csv_list(payload.get("tags_tr") or payload.get("tags")))
            item["tags"] = item["tags_tr"]
            if "tags_en" not in payload:
                item["tags_en"] = _normalize_list_en([best_tr_to_en(x, fallback=x) for x in item["tags_tr"]])

        if "tags_en" in payload:
            item["tags_en"] = _normalize_list_en(_parse_csv_list(payload.get("tags_en")))

        if "interests_tr" in payload or "interests" in payload:
            item["interests_tr"] = _normalize_list_tr(_parse_csv_list(payload.get("interests_tr") or payload.get("interests")))
            item["interests"] = item["interests_tr"]
            if "interests_en" not in payload:
                item["interests_en"] = _normalize_list_en([best_tr_to_en(x, fallback=x) for x in item["interests_tr"]])

        if "interests_en" in payload:
            item["interests_en"] = _normalize_list_en(_parse_csv_list(payload.get("interests_en")))

        if "preferred" in payload:
            item["preferred"] = bool(payload.get("preferred"))

        if "source" in payload:
            item["source"] = str(payload.get("source", "")).strip()

        if "source_query_tr" in payload or "source_query" in payload:
            item["source_query_tr"] = normalize_term_tr(payload.get("source_query_tr") or payload.get("source_query") or "")
            if "source_query_en" not in payload:
                item["source_query_en"] = normalize_term_en(
                    best_tr_to_en(item["source_query_tr"], fallback=item["source_query_tr"])
                )
            item["source_query"] = item["source_query_en"]

        if "source_query_en" in payload:
            item["source_query_en"] = normalize_term_en(payload.get("source_query_en", ""))
            item["source_query"] = item["source_query_en"]
            if not item.get("source_query_tr"):
                item["source_query_tr"] = normalize_term_tr(
                    best_en_to_tr(item["source_query_en"], fallback=item["source_query_en"])
                )

        if "source_url" in payload:
            source_url = str(payload.get("source_url", "")).strip()
            existing = find_asset_by_source_url(source_url)
            if existing and existing.get("asset_id") != asset_id:
                raise ValueError("Bu source_url ile kayıtlı başka bir asset zaten var")
            item["source_url"] = source_url

        if "external_id" in payload:
            item["external_id"] = str(payload.get("external_id", "")).strip()

        if "status" in payload:
            item["status"] = str(payload.get("status", "active")).strip() or "active"

        if "notes" in payload:
            item["notes"] = str(payload.get("notes", "")).strip()

        item["updated_at"] = _now_iso()
        updated_item = _normalize_manifest_item(item)
        break

    if not updated_item:
        raise ValueError("Asset bulunamadı")

    normalized_items = []
    for item in items:
        if item.get("asset_id") == asset_id:
            normalized_items.append(updated_item)
        else:
            normalized_items.append(_normalize_manifest_item(item))

    _write_manifest(normalized_items)

    append_asset_history(
        action="update",
        asset_id=asset_id,
        payload=payload,
    )

    return updated_item


def increment_asset_usage(asset_id: str, context: dict[str, Any] | None = None) -> dict[str, Any] | None:
    items = _read_manifest()
    updated_item = None

    for item in items:
        if item.get("asset_id") == asset_id:
            item["used_count"] = int(item.get("used_count", 0)) + 1
            item["last_used_at"] = _now_iso()
            item["updated_at"] = _now_iso()
            updated_item = item
            break

    if updated_item:
        _write_manifest(items)
        append_asset_history(
            action="use",
            asset_id=asset_id,
            payload=context or {},
        )

    return updated_item


def asset_stats() -> dict[str, Any]:
    items = _read_manifest()

    active = [x for x in items if x.get("status") == "active"]
    preferred = [x for x in items if x.get("preferred")]
    by_source: dict[str, int] = {}
    by_label_tr: dict[str, int] = {}

    for item in items:
        source = str(item.get("source", "unknown"))
        by_source[source] = by_source.get(source, 0) + 1

        label = str(item.get("label_tr", ""))
        if label:
            by_label_tr[label] = by_label_tr.get(label, 0) + 1

    top_labels = sorted(
        [{"label_tr": k, "count": v} for k, v in by_label_tr.items()],
        key=lambda x: (-x["count"], x["label_tr"].lower())
    )[:10]

    return {
        "total_assets": len(items),
        "active_assets": len(active),
        "preferred_assets": len(preferred),
        "by_source": by_source,
        "top_labels": top_labels,
    }