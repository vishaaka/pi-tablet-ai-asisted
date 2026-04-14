from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = Path(__file__).with_name("settings.json")

DEFAULT_SETTINGS: dict[str, Any] = {
    "paths": {
        "data_dir": "data",
        "assets_dir": "assets",
        "panel_ui": "ui/parent_panel_ui.html",
    },
    "mode": {
        "default": "prod",
        "allowed": ["prod", "test"],
    },
    "services": {
        "panel": {
            "host": "127.0.0.1",
            "port": 9100,
            "uvicorn_app": "services.parent_panel:app",
            "open_path": "/panel",
        },
        "tool": {
            "host": "127.0.0.1",
            "port": 8000,
            "uvicorn_app": "services.app:app",
        },
        "middleware": {
            "host": "127.0.0.1",
            "port": 7000,
            "uvicorn_app": "services.middleware:app",
        },
        "dashboard": {
            "host": "127.0.0.1",
            "port": 9000,
            "uvicorn_app": "services.dashboard:app",
        },
        "media": {
            "host": "127.0.0.1",
            "public_host": "",
            "port": 7200,
            "uvicorn_app": "services.media_gateway:app",
        },
    },
    "youtube": {
        "api_key": "api key",
        "safe_search": "strict",
        "max_results": 12,
        "query_suffix": "çocuk eğitici",
    },
    "llm": {
        "lm_studio_url": "http://127.0.0.1:1234/v1/chat/completions",
        "model": "qwen3.5-9b-abliterated",
        "temperature": 0.2,
        "timeout_sec": 30,
        "tool_prompt": (
            "Sen bir çocuk AI asistanısın.\n\n"
            "Araçlar:\n"
            "1. video_search(query: string)\n"
            "2. image_generate(prompt: string)\n"
            "3. speech_generate(text: string)\n"
            "4. video_generate(prompt: string)\n"
            "5. chat(response: string)\n\n"
            "Kurallar:\n"
            "- SADECE JSON döndür\n"
            "- Video isteğinde:\n"
            "{\n"
            '  "tool": "video_search",\n'
            '  "args": {"query": "dinozor"}\n'
            "}\n"
            "- Görsel üretim isteğinde:\n"
            "{\n"
            '  "tool": "image_generate",\n'
            '  "args": {"prompt": "mutlu bir dinozor, çocuk kitabı stili"}\n'
            "}\n"
            "- Ses üretim isteğinde:\n"
            "{\n"
            '  "tool": "speech_generate",\n'
            '  "args": {"text": "Merhaba, hadi oyun oynayalım"}\n'
            "}\n"
            "- Video üretim isteğinde:\n"
            "{\n"
            '  "tool": "video_generate",\n'
            '  "args": {"prompt": "gökkuşağı altında zıplayan top"}\n'
            "}\n"
            "- Normal konuşmada:\n"
            "{\n"
            '  "tool": "chat",\n'
            '  "response": "Merhaba!"\n'
            "}"
        ),
    },
    "hf_media": {
        "output_dir": "assets/generated",
        "request_timeout_sec": 240,
        "image": {
            "provider": "",
            "model": "black-forest-labs/FLUX.1-schnell",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 4,
            "guidance_scale": 0.0,
            "prompt_prefix": "çocuk dostu, eğitici, renkli illüstrasyon",
            "negative_prompt": "korkutucu, gerçekçi şiddet, uygunsuz içerik",
        },
        "speech": {
            "provider": "replicate",
            "model": "hexgrad/Kokoro-82M",
            "voice": "af_nicole",
            "extension": ".flac",
            "extra_body": {},
        },
        "video": {
            "provider": "",
            "model": "genmo/mochi-1-preview",
            "num_frames": 49,
            "num_inference_steps": 30,
            "guidance_scale": 4.5,
            "prompt_prefix": "çocuk dostu, eğitici, yumuşak hareketli kısa video",
            "extra_body": {},
        },
    },
    "autonomy": {
        "default_settings": {
            "enabled": False,
            "mode": "semi_auto",
            "intervention_level": 0.4,
            "max_repeat": 2,
            "interest_bias": 0.7,
            "difficulty_ramp": 0.15,
            "session_duration_min": 20,
            "attention_threshold": 45,
            "tick_cooldown_sec": 8,
            "fallback_interest": "oyuncak",
        }
    },
    "deployment": {
        "package_name": "pi-side",
        "target_dir": "C:\\pitablet",
        "backup_root": "C:\\pitablet_backups",
        "exclude_dirs": ["__pycache__", ".git", ".venv", "venv"],
        "exclude_files": ["*.pyc", "*.pyo"],
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


@lru_cache(maxsize=1)
def get_settings() -> dict[str, Any]:
    data: dict[str, Any] = {}
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    merged = deepcopy(DEFAULT_SETTINGS)
    if isinstance(data, dict):
        _deep_merge(merged, data)
    return merged


def reload_settings() -> dict[str, Any]:
    get_settings.cache_clear()
    return get_settings()


def root_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)


def data_dir() -> Path:
    path = root_path(get_settings()["paths"]["data_dir"])
    path.mkdir(parents=True, exist_ok=True)
    return path


def assets_dir() -> Path:
    path = root_path(get_settings()["paths"]["assets_dir"])
    path.mkdir(parents=True, exist_ok=True)
    return path


def data_path(filename: str) -> Path:
    return data_dir() / filename


def ui_path() -> Path:
    return root_path(get_settings()["paths"]["panel_ui"])


def service_settings(name: str) -> dict[str, Any]:
    return deepcopy(get_settings()["services"][name])


def service_url(name: str, path: str = "") -> str:
    service = service_settings(name)
    suffix = path if path.startswith("/") or not path else f"/{path}"
    return f"http://{service['host']}:{service['port']}{suffix}"


def service_public_url(name: str, path: str = "") -> str:
    service = service_settings(name)
    host = str(service.get("public_host") or service["host"])
    suffix = path if path.startswith("/") or not path else f"/{path}"
    return f"http://{host}:{service['port']}{suffix}"


def deployment_settings() -> dict[str, Any]:
    return deepcopy(get_settings()["deployment"])
