from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class SessionTurn:
    speaker: str
    text: str
    intent: str
    response: str


@dataclass
class AydaSession:
    current_mode: str = "child"
    active_user_role: str = "child"
    current_state: str = "idle"
    last_intent: Optional[str] = None
    last_response: Optional[str] = None
    recent_turns: List[SessionTurn] = field(default_factory=list)
    flags: Dict[str, bool] = field(default_factory=dict)

    def add_turn(self, speaker: str, text: str, intent: str, response: str) -> None:
        self.recent_turns.append(
            SessionTurn(
                speaker=speaker,
                text=text,
                intent=intent,
                response=response,
            )
        )
        self.recent_turns = self.recent_turns[-5:]
        self.last_intent = intent
        self.last_response = response

    def set_mode(self, mode: str) -> None:
        self.current_mode = mode

    def set_role(self, role: str) -> None:
        self.active_user_role = role

    def set_state(self, state: str) -> None:
        self.current_state = state
