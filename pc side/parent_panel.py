# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
LIBRARY_DIR = ASSETS_DIR / "library"
THUMBS_DIR = LIBRARY_DIR / "thumbs"
UI_FILE = BASE_DIR / "parent_panel_ui.html"
MANIFEST_PATH = DATA_DIR / "asset_manifest.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
THUMBS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Pi Tablet Parent Panel", version="manual-assets-v1")
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_manifest() -> list[dict[str, Any]]:
    if not MANIFEST_PATH.exists():
        return []
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def save_manifest(data: list[dict[str, Any]]) -> None:
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    repl = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "İ": "i",
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

    result = "".join(out)
    while "__" in result:
        result = result.replace("__", "_")
    return result.strip("_") or "asset"


def parse_csv_text(value: str) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def build_asset_id(label: str) -> str:
    return f"{slugify(label)}_{uuid.uuid4().hex[:6]}"


def make_thumbnail(src_path: Path, thumb_path: Path, size: tuple[int, int] = (256, 256)) -> None:
    with Image.open(src_path) as img:
        img = img.convert("RGB")
        img.thumbnail(size)
        img.save(thumb_path, format="JPEG", quality=90)


@app.get("/")
async def root() -> FileResponse:
    if not UI_FILE.exists():
        raise HTTPException(status_code=404, detail="parent_panel_ui.html bulunamadı")
    return FileResponse(str(UI_FILE))


@app.get("/server/status")
async def server_status() -> dict[str, Any]:
    manifest = load_manifest()
    return {
        "ok": True,
        "server": "running",
        "asset_count": len(manifest),
        "library_dir": str(LIBRARY_DIR),
        "thumbs_dir": str(THUMBS_DIR),
        "manifest_path": str(MANIFEST_PATH),
        "time": now_iso(),
    }


@app.get("/assets/list")
async def assets_list() -> dict[str, Any]:
    manifest = load_manifest()
    manifest_sorted = sorted(
        manifest,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    return {
        "ok": True,
        "count": len(manifest_sorted),
        "items": manifest_sorted,
    }


@app.get("/assets/stats")
async def assets_stats() -> dict[str, Any]:
    manifest = load_manifest()
    preferred_count = sum(1 for x in manifest if x.get("preferred"))
    total_usage = sum(int(x.get("usage_count", 0) or 0) for x in manifest)
    total_success = sum(int(x.get("success_count", 0) or 0) for x in manifest)
    total_fail = sum(int(x.get("fail_count", 0) or 0) for x in manifest)

    return {
        "ok": True,
        "asset_count": len(manifest),
        "preferred_count": preferred_count,
        "total_usage": total_usage,
        "total_success": total_success,
        "total_fail": total_fail,
    }


@app.post("/assets/create_manual")
async def create_manual_asset(
    label: str = Form(...),
    tags: str = Form(""),
    interests: str = Form(""),
    notes: str = Form(""),
    preferred: str = Form("false"),
    image: UploadFile = File(...),
) -> dict[str, Any]:
    label = (label or "").strip()
    if not label:
        raise HTTPException(status_code=400, detail="label gerekli")

    if not image.filename:
        raise HTTPException(status_code=400, detail="görsel dosyası gerekli")

    ext = Path(image.filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        ext = ".jpg"

    asset_id = build_asset_id(label)
    image_path = LIBRARY_DIR / f"{asset_id}{ext}"
    thumb_path = THUMBS_DIR / f"{asset_id}.jpg"

    with open(image_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    try:
        make_thumbnail(image_path, thumb_path)
    except Exception as e:
        if image_path.exists():
            image_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"thumbnail üretilemedi: {e}")

    manifest = load_manifest()

    item = {
        "asset_id": asset_id,
        "label": label,
        "tags": parse_csv_text(tags),
        "interests": parse_csv_text(interests),
        "notes": (notes or "").strip(),
        "preferred": str(preferred).lower() == "true",
        "type": "image",
        "image_path": f"/assets/library/{image_path.name}",
        "thumb_path": f"/assets/library/thumbs/{thumb_path.name}",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "usage_count": 0,
        "success_count": 0,
        "fail_count": 0,
        "preferred_score": 0.0,
        "attention_score": 0.0,
        "speech_success_score": 0.0,
    }

    manifest.append(item)
    save_manifest(manifest)

    return {
        "ok": True,
        "item": item,
    }


@app.post("/assets/update")
async def update_asset(
    asset_id: str = Form(...),
    label: str = Form(""),
    tags: str = Form(""),
    interests: str = Form(""),
    notes: str = Form(""),
    preferred: str = Form("false"),
) -> dict[str, Any]:
    manifest = load_manifest()
    target = None

    for item in manifest:
        if item.get("asset_id") == asset_id:
            target = item
            break

    if target is None:
        raise HTTPException(status_code=404, detail="asset bulunamadı")

    if label.strip():
        target["label"] = label.strip()

    target["tags"] = parse_csv_text(tags)
    target["interests"] = parse_csv_text(interests)
    target["notes"] = notes.strip()
    target["preferred"] = str(preferred).lower() == "true"
    target["updated_at"] = now_iso()

    save_manifest(manifest)

    return {
        "ok": True,
        "item": target,
    }


@app.post("/assets/delete")
async def delete_asset(asset_id: str = Form(...)) -> dict[str, Any]:
    manifest = load_manifest()
    kept: list[dict[str, Any]] = []
    target = None

    for item in manifest:
        if item.get("asset_id") == asset_id:
            target = item
        else:
            kept.append(item)

    if target is None:
        raise HTTPException(status_code=404, detail="asset bulunamadı")

    image_rel = target.get("image_path", "")
    thumb_rel = target.get("thumb_path", "")

    if image_rel.startswith("/assets/"):
        image_abs = ASSETS_DIR / image_rel.replace("/assets/", "", 1)
        Path(image_abs).unlink(missing_ok=True)

    if thumb_rel.startswith("/assets/"):
        thumb_abs = ASSETS_DIR / thumb_rel.replace("/assets/", "", 1)
        Path(thumb_abs).unlink(missing_ok=True)

    save_manifest(kept)

    return {
        "ok": True,
        "deleted_asset_id": asset_id,
    }


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("parent_panel:app", host="0.0.0.0", port=7000, reload=False)
