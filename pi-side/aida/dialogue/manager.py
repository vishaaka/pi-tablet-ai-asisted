from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from aida.core.router import Router
from aida.core.session import AidaSession
from aida.core.state_machine import StateMachine
from aida.dialogue.intents import classify_intent
from aida.dialogue.templates import choose_template


@dataclass
class ResponseObject:
    text: str
    emotion: str
    next_state: str
    action: str | None
    delegate: bool


class DialogueManager:
    def __init__(self, pc_bridge: Any | None = None) -> None:
        self.router = Router()
        self.state_machine = StateMachine()
        self.pc_bridge = pc_bridge

    def _handle_parent_command(self, text: str) -> str:
        normalized = text.lower()

        if "ses" in normalized and ("kıs" in normalized or "azalt" in normalized):
            return "Tamam. Ses biraz azaltılabilir."
        if "ses" in normalized and ("aç" in normalized or "artır" in normalized):
            return "Tamam. Ses artırılabilir."
        if "kapat" in normalized:
            return "Tamam. Bu işlem ebeveyn komutu olarak işaretlendi."
        if "süre" in normalized:
            return "Tamam. Süre ayarı ebeveyn modunda değiştirilebilir."

        return "Ebeveyn komutu alındı."

    def _delegate_to_pc(self, text: str) -> str:
        if self.pc_bridge is None:
            return "Bu isteği daha güçlü zekâya gönderebilirim ama bağlantı şu an hazır değil."
        return self.pc_bridge.ask(text)

    def process(self, text: str, session: AidaSession) -> ResponseObject:
        session.set_state(self.state_machine.transition("listening"))
        session.set_state(self.state_machine.transition("thinking"))

        intent_result = classify_intent(text, current_role=session.active_user_role)
        decision = self.router.decide(intent_result.intent, session.active_user_role)

        if decision.route == "template":
            response_text = choose_template(decision.template_key or "unknown")
            emotion = "happy" if intent_result.intent in {"greeting", "play_request"} else "neutral"

        elif decision.route == "parent_skill":
            response_text = self._handle_parent_command(text)
            emotion = "neutral"

        elif decision.route == "delegate":
            response_text = self._delegate_to_pc(text)
            emotion = "thinking"

        else:
            response_text = choose_template("unknown")
            emotion = "confused"

        session.set_state(self.state_machine.transition(decision.next_state))
        session.add_turn(
            speaker=session.active_user_role,
            text=text,
            intent=intent_result.intent,
            response=response_text,
        )

        return ResponseObject(
            text=response_text,
            emotion=emotion,
            next_state=session.current_state,
            action=None,
            delegate=decision.delegate_to_pc,
        )
