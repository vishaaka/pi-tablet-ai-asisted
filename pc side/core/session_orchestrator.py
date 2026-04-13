import json
import time
from typing import Any

from config.settings import data_dir, data_path, get_settings
from core.content_pack_builder import (
    build_pack_pair,
    pick_default_interest,
    pick_next_target_word,
)
from core.dictionary_bridge import best_tr_to_en, normalize_term_tr
from storage.command_queue import push_command

SETTINGS_PATH = data_path("autonomy_settings.json")
STATE_PATH = data_path("autonomy_state.json")

DEFAULT_SETTINGS = get_settings()["autonomy"]["default_settings"]

DEFAULT_STATE = {
    "running": False,
    "session_id": "",
    "started_at": 0,
    "last_tick_at": 0,
    "last_target_word_tr": "",
    "last_target_word_en": "",
    "last_interest_tr": "",
    "difficulty": 1,
    "repeat_count": 0,
    "recent_targets": [],
    "last_reason": "",
}


def _ensure_data_dir():
    data_dir()


def _load_json(path: str, fallback: Any):
    if not path.exists():
        return fallback

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback


def _save_json(path: str, data: Any):
    _ensure_data_dir()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_settings():
    data = _load_json(SETTINGS_PATH, DEFAULT_SETTINGS.copy())
    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    return merged


def save_settings(payload: dict):
    merged = load_settings()
    merged.update(payload or {})
    _save_json(SETTINGS_PATH, merged)
    return merged


def _load_state():
    data = _load_json(STATE_PATH, DEFAULT_STATE.copy())
    merged = DEFAULT_STATE.copy()
    merged.update(data)
    return merged


def _save_state(state: dict):
    _save_json(STATE_PATH, state)


def get_session_state():
    return _load_state()


def start_session(payload: dict | None = None):
    payload = payload or {}
    settings = load_settings()
    state = _load_state()

    session_id = f"sess_{int(time.time())}"

    interest = normalize_term_tr(
        payload.get("interest")
        or settings.get("fallback_interest")
        or pick_default_interest()
    )

    target_word = normalize_term_tr(
        payload.get("target_word")
        or pick_next_target_word(
            preferred_interest=interest,
            fallback_interest=interest,
        )
    )

    state.update({
        "running": True,
        "session_id": session_id,
        "started_at": time.time(),
        "last_tick_at": 0,
        "last_target_word_tr": target_word,
        "last_target_word_en": best_tr_to_en(target_word, fallback=target_word),
        "last_interest_tr": interest,
        "difficulty": 1,
        "repeat_count": 0,
        "recent_targets": [target_word],
        "last_reason": "session_start",
    })

    _save_state(state)

    result = tick_session(force=True)

    return {
        "ok": True,
        "session_id": session_id,
        "state": _load_state(),
        "tick_result": result,
    }


def stop_session(reason: str = "manual_stop"):
    state = _load_state()
    state["running"] = False
    state["last_reason"] = reason
    _save_state(state)

    return {
        "ok": True,
        "reason": reason,
        "state": state,
    }


def _pick_next_target(state: dict, settings: dict):
    recent = state.get("recent_targets", [])
    current = state.get("last_target_word_tr", "")
    interest = state.get("last_interest_tr", "") or settings["fallback_interest"]

    if state["repeat_count"] < settings["max_repeat"]:
        return current, "repeat_target"

    candidate = pick_next_target_word(
        preferred_interest=interest,
        fallback_interest=interest,
    )

    if candidate in recent[-3:]:
        candidate = interest

    return normalize_term_tr(candidate), "new_target"


def tick_session(force: bool = False):
    settings = load_settings()
    state = _load_state()

    if not state["running"]:
        return {"ok": False, "reason": "session_not_running"}

    now = time.time()
    cooldown = settings.get("tick_cooldown_sec", 8)

    if not force and (now - state["last_tick_at"]) < cooldown:
        return {
            "ok": False,
            "reason": "cooldown",
            "wait_sec": cooldown - (now - state["last_tick_at"]),
        }

    target_word, reason = _pick_next_target(state, settings)

    next_target = pick_next_target_word(
        preferred_interest=state["last_interest_tr"],
        fallback_interest=state["last_interest_tr"],
    )

    packs = build_pack_pair(
        session_id=state["session_id"],
        current_screen="speech_cards",
        target_word=target_word,
        interest=state["last_interest_tr"],
        difficulty=state["difficulty"],
        reason=reason,
        preload_next=True,
        next_target=next_target,
    )

    push_command("set_pack", packs["current_pack"])
    push_command("preload_pack", packs["next_pack"])

    if target_word == state["last_target_word_tr"]:
        state["repeat_count"] += 1
    else:
        state["repeat_count"] = 0

    state["last_tick_at"] = now
    state["last_target_word_tr"] = target_word
    state["last_target_word_en"] = best_tr_to_en(target_word, fallback=target_word)
    state["last_reason"] = reason

    recent = state.get("recent_targets", [])
    recent.append(target_word)
    state["recent_targets"] = recent[-10:]

    if reason == "new_target":
        state["difficulty"] = min(5, state["difficulty"] + 1)

    _save_state(state)

    return {
        "ok": True,
        "reason": reason,
        "target_word_tr": target_word,
        "target_word_en": state["last_target_word_en"],
        "difficulty": state["difficulty"],
        "packs": packs,
    }
