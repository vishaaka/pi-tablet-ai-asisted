from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SETTINGS_PATH = Path(__file__).with_name("settings.yaml")


@dataclass
class PCBackendSettings:
    enabled: bool = True
    base_url: str = "http://127.0.0.1:7000"
    timeout_sec: float = 8.0


@dataclass
class LocalBackendSettings:
    enabled: bool = True
    base_url: str = "http://127.0.0.1:8080"
    timeout_sec: float = 20.0
    model: str = "ayda-qwen2.5-1.5b-tr-seed-q4_k_m.gguf"
    max_tokens: int = 160
    temperature: float = 0.7
    system_prompt: str = (
        "Sen AYDA'sin. Turkce konusan, neseli, sabirli ve cocuk dostu bir oyun arkadasisin. "
        "Kisa cumleler kullan. Cevaplari sicak, destekleyici ve guvenli tut."
    )


@dataclass
class AydaSettings:
    preferred_backend: str = "auto"
    pc: PCBackendSettings = field(default_factory=PCBackendSettings)
    local: LocalBackendSettings = field(default_factory=LocalBackendSettings)


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        return {}
    return data


def load_settings(path: str | Path | None = None) -> AydaSettings:
    settings_path = Path(path or os.getenv("AYDA_SETTINGS_PATH") or DEFAULT_SETTINGS_PATH)
    raw = _read_yaml(settings_path)

    bridge = raw.get("bridge", {})
    if not isinstance(bridge, dict):
        bridge = {}

    pc_raw = bridge.get("pc", {})
    if not isinstance(pc_raw, dict):
        pc_raw = {}

    local_raw = bridge.get("local", {})
    if not isinstance(local_raw, dict):
        local_raw = {}

    pc = PCBackendSettings(
        enabled=_as_bool(pc_raw.get("enabled"), True),
        base_url=str(pc_raw.get("base_url", "http://127.0.0.1:7000")),
        timeout_sec=float(pc_raw.get("timeout_sec", 8.0)),
    )
    local = LocalBackendSettings(
        enabled=_as_bool(local_raw.get("enabled"), True),
        base_url=str(local_raw.get("base_url", "http://127.0.0.1:8080")),
        timeout_sec=float(local_raw.get("timeout_sec", 20.0)),
        model=str(local_raw.get("model", "ayda-qwen2.5-1.5b-tr-seed-q4_k_m.gguf")),
        max_tokens=int(local_raw.get("max_tokens", 160)),
        temperature=float(local_raw.get("temperature", 0.7)),
        system_prompt=str(
            local_raw.get(
                "system_prompt",
                "Sen AYDA'sin. Turkce konusan, neseli, sabirli ve cocuk dostu bir oyun arkadasisin. "
                "Kisa cumleler kullan. Cevaplari sicak, destekleyici ve guvenli tut.",
            )
        ),
    )

    preferred_backend = str(bridge.get("preferred_backend", "auto")).strip().lower() or "auto"
    if preferred_backend not in {"auto", "pc", "local"}:
        preferred_backend = "auto"

    settings = AydaSettings(
        preferred_backend=preferred_backend,
        pc=pc,
        local=local,
    )

    preferred_backend_override = os.getenv("AYDA_BRIDGE_BACKEND")
    if preferred_backend_override:
        normalized = preferred_backend_override.strip().lower()
        if normalized in {"auto", "pc", "local"}:
            settings.preferred_backend = normalized

    pc_base_url = os.getenv("AYDA_PC_BASE_URL") or os.getenv("AIDA_PC_BASE_URL")
    if pc_base_url:
        settings.pc.base_url = pc_base_url

    pc_timeout = os.getenv("AYDA_PC_TIMEOUT") or os.getenv("AIDA_PC_TIMEOUT")
    if pc_timeout:
        settings.pc.timeout_sec = float(pc_timeout)

    local_base_url = os.getenv("AYDA_LOCAL_BASE_URL")
    if local_base_url:
        settings.local.base_url = local_base_url

    local_timeout = os.getenv("AYDA_LOCAL_TIMEOUT")
    if local_timeout:
        settings.local.timeout_sec = float(local_timeout)

    local_model = os.getenv("AYDA_LOCAL_MODEL")
    if local_model:
        settings.local.model = local_model

    local_max_tokens = os.getenv("AYDA_LOCAL_MAX_TOKENS")
    if local_max_tokens:
        settings.local.max_tokens = int(local_max_tokens)

    local_temperature = os.getenv("AYDA_LOCAL_TEMPERATURE")
    if local_temperature:
        settings.local.temperature = float(local_temperature)

    return settings
