from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IntentResult:
    intent: str
    confidence: float
    reason: Optional[str] = None


GREETING_WORDS = {
    "merhaba", "selam", "günaydın", "iyi akşamlar", "hey", "aida"
}

PLAY_WORDS = {
    "oyun", "oynayalım", "oyna", "başlayalım", "eğlenelim"
}

PARENT_COMMAND_WORDS = {
    "sesi", "kıs", "artır", "azalt", "kapat", "aç", "ayar", "süre", "limit"
}

HELP_WORDS = {
    "yardım", "yardım et", "bilmiyorum", "anlamadım"
}

REPEAT_WORDS = {
    "tekrar", "yeniden", "bir daha", "anlamadım"
}

STORY_WORDS = {
    "hikaye", "masal", "anlat"
}

OBJECT_WORDS = {
    "bu ne", "hangi renk", "göster", "bul", "nesne"
}


def normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def classify_intent(text: str, current_role: str = "child") -> IntentResult:
    normalized = normalize_text(text)

    if not normalized:
        return IntentResult(intent="unknown", confidence=0.1, reason="empty_input")

    if any(word in normalized for word in GREETING_WORDS):
        return IntentResult(intent="greeting", confidence=0.95, reason="matched_greeting")

    if any(word in normalized for word in PLAY_WORDS):
        return IntentResult(intent="play_request", confidence=0.90, reason="matched_play")

    if any(word in normalized for word in HELP_WORDS):
        return IntentResult(intent="help", confidence=0.85, reason="matched_help")

    if any(word in normalized for word in REPEAT_WORDS):
        return IntentResult(intent="repeat", confidence=0.80, reason="matched_repeat")

    if any(word in normalized for word in STORY_WORDS):
        return IntentResult(intent="story_request", confidence=0.88, reason="matched_story")

    if any(word in normalized for word in OBJECT_WORDS):
        return IntentResult(intent="object_talk", confidence=0.78, reason="matched_object")

    if any(word in normalized for word in PARENT_COMMAND_WORDS):
        if current_role == "parent":
            return IntentResult(intent="parent_command", confidence=0.92, reason="matched_parent_command")
        return IntentResult(intent="restricted_command", confidence=0.70, reason="command_but_not_parent")

    if len(normalized.split()) <= 8:
        return IntentResult(intent="daily_chat", confidence=0.55, reason="short_chat_fallback")

    return IntentResult(intent="complex_request", confidence=0.60, reason="delegate_to_pc")
