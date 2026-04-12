from __future__ import annotations


VALID_STATES = {
    "idle",
    "listening",
    "thinking",
    "speaking",
    "waiting_attention",
    "parent_control",
    "play_mode",
}


class StateMachine:
    def __init__(self) -> None:
        self.state = "idle"

    def transition(self, next_state: str) -> str:
        if next_state not in VALID_STATES:
            raise ValueError(f"Invalid state: {next_state}")
        self.state = next_state
        return self.state

    def get_state(self) -> str:
        return self.state
