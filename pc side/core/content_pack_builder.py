from core.asset_selector import select_best_asset
from core.dictionary_bridge import (
    best_en_to_tr,
    best_tr_to_en,
    normalize_term_tr,
    normalize_term_en,
)
from core.milestone_engine import get_milestone_payload
from storage.asset_manager import increment_asset_usage


def pick_default_interest(fallback_interest: str = "oyuncak") -> str:
    fallback_interest = (fallback_interest or "").strip()
    return normalize_term_tr(fallback_interest or "oyuncak")


def pick_next_target_word(
    preferred_interest: str = "",
    fallback_interest: str = "oyuncak",
) -> str:
    try:
        payload = get_milestone_payload()
        words = payload.get("words", [])
    except Exception:
        words = []

    developing = [
        normalize_term_tr(x.get("word", ""))
        for x in words
        if (x.get("status") or "").strip() != "tam" and x.get("word")
    ]

    if developing:
        return developing[0]

    interest_map = {
        "araba": "araba",
        "hayvan": "kedi",
        "top": "top",
        "renkler": "mavi",
        "dinozor": "dinozor",
        "oyuncak": "ayı",
    }

    preferred_interest = normalize_term_tr(preferred_interest)
    fallback_interest = normalize_term_tr(fallback_interest)

    if preferred_interest:
        return interest_map.get(preferred_interest, preferred_interest)

    return interest_map.get(fallback_interest, "top")


def _build_card_from_asset(
    target_word_tr: str,
    interest_tr: str,
    asset: dict | None,
    reason: str = "",
) -> dict:
    label_tr = target_word_tr
    image_path = ""

    if asset:
        label_tr = asset.get("label_tr") or target_word_tr
        image_path = asset.get("image_path", "")

    prompt_text = "Bu ne?"
    if interest_tr:
        prompt_text = f"Bu ne? Söyle: {label_tr}"

    return {
        "label": normalize_term_tr(label_tr),
        "tts_text": normalize_term_tr(label_tr),
        "prompt_text": prompt_text,
        "image_path": image_path,
        "reason": reason,
    }


def build_speech_pack(
    target_word: str,
    interest: str = "",
    next_target: str | None = None
):
    target_word_tr = normalize_term_tr(target_word)
    interest_tr = normalize_term_tr(interest)

    current_asset = select_best_asset(
        target_label=target_word_tr,
        interest=interest_tr
    )

    next_asset = None
    if next_target:
        next_asset = select_best_asset(
            target_label=normalize_term_tr(next_target),
            interest=interest_tr
        )

    if current_asset:
        increment_asset_usage(
            current_asset["asset_id"],
            {
                "reason": "speech_pack",
                "target_word_tr": target_word_tr,
                "target_word_en": best_tr_to_en(target_word_tr, fallback=target_word_tr),
            }
        )

    if next_asset and next_target:
        increment_asset_usage(
            next_asset["asset_id"],
            {
                "reason": "next_preload",
                "target_word_tr": normalize_term_tr(next_target),
                "target_word_en": best_tr_to_en(next_target, fallback=next_target),
            }
        )

    active_pack = {
        "screen": "speech_cards",
        "cards": [
            _build_card_from_asset(
                target_word_tr=target_word_tr,
                interest_tr=interest_tr,
                asset=current_asset,
                reason="active_pack"
            )
        ]
    }

    next_pack = None
    if next_target:
        next_pack = {
            "screen": "speech_cards",
            "cards": [
                _build_card_from_asset(
                    target_word_tr=normalize_term_tr(next_target),
                    interest_tr=interest_tr,
                    asset=next_asset,
                    reason="next_pack"
                )
            ]
        }

    return {
        "active_pack": active_pack,
        "next_pack": next_pack
    }


def build_pack_pair(
    session_id: str | None = None,
    current_screen: str = "speech_cards",
    target_word: str = "",
    interest: str = "",
    difficulty: int = 1,
    target_type: str = "single_word",
    reason: str = "",
    preload_next: bool = True,
    next_target: str | None = None,
):
    target_word_tr = normalize_term_tr(target_word)
    interest_tr = normalize_term_tr(interest)

    if not target_word_tr:
        target_word_tr = pick_next_target_word(
            preferred_interest=interest_tr,
            fallback_interest="oyuncak"
        )

    if not next_target:
        next_target = target_word_tr

    next_target_tr = normalize_term_tr(next_target)

    packs = build_speech_pack(
        target_word=target_word_tr,
        interest=interest_tr,
        next_target=next_target_tr
    )

    current_pack = {
        "pack_id": f"{session_id or 'sess'}_current",
        "screen": packs["active_pack"]["screen"],
        "version": 1,
        "cards": packs["active_pack"]["cards"],
        "audio": [],
        "meta": {
            "session_id": session_id or "",
            "goal": "speech_encouragement",
            "reason": reason,
            "target_word_tr": target_word_tr,
            "target_word_en": best_tr_to_en(target_word_tr, fallback=target_word_tr),
            "interest_tr": interest_tr,
            "interest_en": best_tr_to_en(interest_tr, fallback=interest_tr),
            "difficulty": difficulty,
            "target_type": target_type,
            "preload_next": preload_next,
            "expected_duration_sec": 20,
        },
    }

    if packs["next_pack"]:
        next_pack = {
            "pack_id": f"{session_id or 'sess'}_next",
            "screen": packs["next_pack"]["screen"],
            "version": 1,
            "cards": packs["next_pack"]["cards"],
            "audio": [],
            "meta": {
                "session_id": session_id or "",
                "goal": "speech_encouragement",
                "reason": "next_preload",
                "target_word_tr": next_target_tr,
                "target_word_en": best_tr_to_en(next_target_tr, fallback=next_target_tr),
                "interest_tr": interest_tr,
                "interest_en": best_tr_to_en(interest_tr, fallback=interest_tr),
                "difficulty": difficulty,
                "target_type": target_type,
                "preload_next": preload_next,
                "expected_duration_sec": 20,
            },
        }
    else:
        next_pack = {
            "pack_id": f"{session_id or 'sess'}_next",
            "screen": "speech_cards",
            "version": 1,
            "cards": [],
            "audio": [],
            "meta": {
                "session_id": session_id or "",
                "goal": "speech_encouragement",
                "reason": "next_preload_empty",
                "target_word_tr": "",
                "target_word_en": "",
                "interest_tr": interest_tr,
                "interest_en": best_tr_to_en(interest_tr, fallback=interest_tr),
                "difficulty": difficulty,
                "target_type": target_type,
                "preload_next": preload_next,
                "expected_duration_sec": 20,
            },
        }

    return {
        "current_pack": current_pack,
        "next_pack": next_pack
    }
