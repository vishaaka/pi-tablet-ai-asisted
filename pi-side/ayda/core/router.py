from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RouteDecision:
    route: str
    template_key: Optional[str] = None
    delegate_to_pc: bool = False
    next_state: str = "speaking"


class Router:
    def decide(self, intent: str, role: str) -> RouteDecision:
        if intent == "greeting":
            return RouteDecision(route="template", template_key="greeting")

        if intent == "daily_chat":
            return RouteDecision(route="template", template_key="daily_chat")

        if intent == "play_request":
            return RouteDecision(route="template", template_key="play_request", next_state="play_mode")

        if intent == "help":
            return RouteDecision(route="template", template_key="help")

        if intent == "repeat":
            return RouteDecision(route="template", template_key="repeat")

        if intent == "story_request":
            return RouteDecision(route="delegate", template_key="story_request", delegate_to_pc=True)

        if intent == "object_talk":
            return RouteDecision(route="template", template_key="object_talk")

        if intent == "parent_command":
            return RouteDecision(route="parent_skill", next_state="parent_control")

        if intent == "restricted_command":
            return RouteDecision(route="template", template_key="parent_required")

        if intent == "complex_request":
            return RouteDecision(route="delegate", delegate_to_pc=True)

        return RouteDecision(route="template", template_key="unknown")
