import json
import os
from typing import Any

import requests

from asset_history import append_asset_history
from asset_manager import (
    create_asset_from_saved_path,
    find_asset_by_source_url,
    save_binary_image,
)

OPEN_IMAGES_INDEX_PATH = "data/open_images_index.jsonl"


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def _load_index() -> list[dict[str, Any]]:
    if not os.path.exists(OPEN_IMAGES_INDEX_PATH):
        return []

    items: list[dict[str, Any]] = []
    with open(OPEN_IMAGES_INDEX_PATH, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue

            try:
                item = json.loads(raw)
                if isinstance(item, dict):
                    items.append(item)
            except Exception:
                continue

    return items


def _score_candidate(item: dict[str, Any], query: str) -> int:
    query_terms = [_normalize(x) for x in query.split() if _normalize(x)]
    if not query_terms:
        return 0

    label = _normalize(item.get("label", ""))
    title = _normalize(item.get("title", ""))
    tags = [_normalize(x) for x in item.get("tags", [])]
    categories = [_normalize(x) for x in item.get("categories", [])]
    blob = " ".join([label, title, " ".join(tags), " ".join(categories)])

    score = 0
    for term in query_terms:
        if label == term:
            score += 20
        elif term in label:
            score += 12

        if term in title:
            score += 8

        if term in tags:
            score += 6

        if term in categories:
            score += 4

        if term in blob:
            score += 2

    if item.get("preferred"):
        score += 2

    return score


def search_open_images(query: str, limit: int = 12) -> dict[str, Any]:
    query = (query or "").strip()
    if not query:
        return {
            "ok": False,
            "error": "Arama sorgusu boş olamaz",
            "items": [],
        }

    items = _load_index()
    if not items:
        return {
            "ok": False,
            "error": (
                "data/open_images_index.jsonl bulunamadı veya boş. "
                "Önce yerel Open Images index dosyasını hazırla."
            ),
            "items": [],
        }

    scored = []
    for item in items:
        score = _score_candidate(item, query)
        if score > 0:
            enriched = dict(item)
            enriched["_score"] = score
            scored.append(enriched)

    scored.sort(
        key=lambda x: (
            -int(x.get("_score", 0)),
            str(x.get("label", "")).lower(),
            str(x.get("title", "")).lower(),
        )
    )

    result = []
    for item in scored[: max(1, limit)]:
        result.append({
            "external_id": item.get("external_id", ""),
            "label": item.get("label", ""),
            "title": item.get("title", ""),
            "thumbnail_url": item.get("thumbnail_url", ""),
            "image_url": item.get("image_url", ""),
            "source_url": item.get("source_url", "") or item.get("image_url", ""),
            "tags": item.get("tags", []),
            "categories": item.get("categories", []),
            "license": item.get("license", ""),
            "source": "open_images",
            "score": item.get("_score", 0),
        })

    return {
        "ok": True,
        "query": query,
        "count": len(result),
        "items": result,
    }


def _find_index_item_by_external_id(external_id: str) -> dict[str, Any] | None:
    items = _load_index()
    for item in items:
        if (item.get("external_id") or "") == external_id:
            return item
    return None


def import_open_images_item(payload: dict[str, Any]) -> dict[str, Any]:
    external_id = str(payload.get("external_id", "")).strip()
    label = str(payload.get("label", "")).strip()
    image_url = str(payload.get("image_url", "")).strip()
    source_url = str(payload.get("source_url", "")).strip() or image_url

    if external_id and (not label or not image_url):
        indexed = _find_index_item_by_external_id(external_id)
        if indexed:
            label = label or str(indexed.get("label", "")).strip()
            image_url = image_url or str(indexed.get("image_url", "")).strip()
            source_url = source_url or str(indexed.get("source_url", "")).strip() or image_url
            if "tags" not in payload:
                payload["tags"] = indexed.get("tags", [])
            if "categories" not in payload:
                payload["categories"] = indexed.get("categories", [])

    if not label:
        raise ValueError("label boş olamaz")

    if not image_url:
        raise ValueError("image_url boş olamaz")

    existing = find_asset_by_source_url(source_url)
    if existing:
        append_asset_history(
            action="open_images_duplicate_skip",
            asset_id=existing["asset_id"],
            payload={
                "external_id": external_id,
                "label": label,
                "source_url": source_url,
            },
        )
        return {
            "ok": True,
            "duplicate": True,
            "asset": existing,
        }

    response = requests.get(image_url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "image/jpeg")
    saved_path = save_binary_image(
        binary=response.content,
        content_type=content_type,
        suggested_name=label,
    )

    tags = payload.get("tags", [])
    categories = payload.get("categories", [])
    merged_tags = []
    seen = set()

    for value in list(tags) + list(categories):
        text = str(value).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        merged_tags.append(text)
        seen.add(key)

    item = create_asset_from_saved_path(
        image_path=saved_path,
        label=label,
        tags=merged_tags,
        interests=payload.get("interests", []),
        preferred=bool(payload.get("preferred", False)),
        source="open_images",
        source_query=str(payload.get("source_query", "")).strip(),
        source_url=source_url,
        external_id=external_id,
        notes=str(payload.get("notes", "")).strip(),
    )

    append_asset_history(
        action="open_images_import",
        asset_id=item["asset_id"],
        payload={
            "external_id": external_id,
            "label": label,
            "image_url": image_url,
            "source_url": source_url,
        },
    )

    return {
        "ok": True,
        "duplicate": False,
        "asset": item,
    }