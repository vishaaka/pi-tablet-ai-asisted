from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from config.settings import data_path, get_settings, root_path, service_settings, service_public_url

try:
    from huggingface_hub import InferenceClient, get_token
except Exception:  # pragma: no cover - dependency can be installed later
    InferenceClient = None

    def get_token() -> str | None:  # type: ignore[override]
        return os.getenv("HF_TOKEN")


app = FastAPI(title="HF Media Gateway")


class MediaGatewayError(RuntimeError):
    pass


def media_settings() -> dict[str, Any]:
    return get_settings()["hf_media"]


def media_root() -> Path:
    path = root_path(media_settings()["output_dir"])
    path.mkdir(parents=True, exist_ok=True)
    for name in ("images", "audio", "video"):
        path.joinpath(name).mkdir(parents=True, exist_ok=True)
    return path


def history_file() -> Path:
    return data_path("media_history.jsonl")


def _slug(value: str, fallback: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", (value or "").strip().lower())
    normalized = normalized.strip("_")
    return normalized[:48] or fallback


def _append_history(item: dict[str, Any]) -> None:
    path = history_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def _client(provider_name: str | None = None):
    if InferenceClient is None:
        raise MediaGatewayError("huggingface_hub kurulu değil. `pip install -r requirements.txt` çalıştırılmalı.")

    token = os.getenv("HF_TOKEN") or get_token()
    kwargs: dict[str, Any] = {
        "timeout": float(media_settings().get("request_timeout_sec", 180)),
    }
    if provider_name:
        kwargs["provider"] = provider_name
    if token:
        kwargs["api_key"] = token
    return InferenceClient(**kwargs)


def _build_output(kind: str, prompt: str, extension: str) -> Path:
    now = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{_slug(prompt, kind)}_{now}{extension}"
    return media_root() / kind / filename


def _public_payload(kind: str, output_path: Path, prompt: str, model: str, provider: str) -> dict[str, Any]:
    service = service_settings("media")
    relative_path = output_path.relative_to(media_root()).as_posix()
    file_url = service_public_url("media", f"/files/{relative_path}")
    item = {
        "ok": True,
        "kind": kind,
        "prompt": prompt,
        "model": model,
        "provider": provider or "default",
        "filename": output_path.name,
        "file_path": str(output_path),
        "file_url": file_url,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "host": service["host"],
        "port": service["port"],
    }
    _append_history(item)
    return item


def generate_image(prompt: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    config = dict(media_settings()["image"])
    if overrides:
        config.update({k: v for k, v in overrides.items() if v is not None})

    prompt = str(prompt or "").strip()
    if not prompt:
        raise MediaGatewayError("Görsel üretimi için prompt boş olamaz.")

    prompt_prefix = str(config.get("prompt_prefix", "")).strip()
    final_prompt = f"{prompt_prefix} {prompt}".strip() if prompt_prefix else prompt
    negative_prompt = str(config.get("negative_prompt", "")).strip() or None

    image = _client(config.get("provider")).text_to_image(
        prompt=final_prompt,
        negative_prompt=negative_prompt,
        model=config.get("model"),
        width=int(config.get("width", 1024)),
        height=int(config.get("height", 1024)),
        num_inference_steps=int(config.get("num_inference_steps", 4)),
        guidance_scale=float(config.get("guidance_scale", 0.0)),
    )
    output_path = _build_output("images", final_prompt, ".png")
    image.save(output_path)
    return _public_payload(
        kind="image",
        output_path=output_path,
        prompt=final_prompt,
        model=str(config.get("model", "")),
        provider=str(config.get("provider", "")),
    )


def generate_speech(text: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    config = dict(media_settings()["speech"])
    if overrides:
        config.update({k: v for k, v in overrides.items() if v is not None})

    text = str(text or "").strip()
    if not text:
        raise MediaGatewayError("Ses üretimi için metin boş olamaz.")

    extra_body = dict(config.get("extra_body", {}) or {})
    voice = config.get("voice")
    if voice and "voice" not in extra_body:
        extra_body["voice"] = voice

    audio = _client(config.get("provider")).text_to_speech(
        text=text,
        model=config.get("model"),
        extra_body=extra_body or None,
    )
    extension = str(config.get("extension", ".flac"))
    if not extension.startswith("."):
        extension = f".{extension}"
    output_path = _build_output("audio", text, extension)
    output_path.write_bytes(audio)
    return _public_payload(
        kind="speech",
        output_path=output_path,
        prompt=text,
        model=str(config.get("model", "")),
        provider=str(config.get("provider", "")),
    )


def generate_video(prompt: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    config = dict(media_settings()["video"])
    if overrides:
        config.update({k: v for k, v in overrides.items() if v is not None})

    prompt = str(prompt or "").strip()
    if not prompt:
        raise MediaGatewayError("Video üretimi için prompt boş olamaz.")

    prompt_prefix = str(config.get("prompt_prefix", "")).strip()
    final_prompt = f"{prompt_prefix} {prompt}".strip() if prompt_prefix else prompt

    video = _client(config.get("provider")).text_to_video(
        prompt=final_prompt,
        model=config.get("model"),
        guidance_scale=float(config.get("guidance_scale", 4.5)),
        num_frames=int(config.get("num_frames", 49)),
        num_inference_steps=int(config.get("num_inference_steps", 30)),
        extra_body=dict(config.get("extra_body", {}) or {}) or None,
    )
    output_path = _build_output("video", final_prompt, ".mp4")
    output_path.write_bytes(video)
    return _public_payload(
        kind="video",
        output_path=output_path,
        prompt=final_prompt,
        model=str(config.get("model", "")),
        provider=str(config.get("provider", "")),
    )


@app.get("/health")
def health():
    token = os.getenv("HF_TOKEN") or get_token()
    return {
        "ok": True,
        "service": "media_gateway",
        "has_token": bool(token),
        "output_dir": str(media_root()),
    }


@app.get("/config")
def config_summary():
    settings = media_settings()
    return {
        "ok": True,
        "models": {
            "image": settings["image"].get("model"),
            "speech": settings["speech"].get("model"),
            "video": settings["video"].get("model"),
        },
        "providers": {
            "image": settings["image"].get("provider"),
            "speech": settings["speech"].get("provider"),
            "video": settings["video"].get("provider"),
        },
    }


@app.post("/generate/image")
def api_generate_image(payload: dict):
    try:
        return generate_image(payload.get("prompt", ""), overrides=payload)
    except MediaGatewayError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Görsel üretimi başarısız: {exc}") from exc


@app.post("/generate/speech")
def api_generate_speech(payload: dict):
    try:
        return generate_speech(payload.get("text", ""), overrides=payload)
    except MediaGatewayError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ses üretimi başarısız: {exc}") from exc


@app.post("/generate/video")
def api_generate_video(payload: dict):
    try:
        return generate_video(payload.get("prompt", ""), overrides=payload)
    except MediaGatewayError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Video üretimi başarısız: {exc}") from exc


@app.get("/files/{kind}/{filename}")
def serve_file(kind: str, filename: str):
    file_path = media_root() / kind / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dosya bulunamadı.")
    return FileResponse(file_path)
