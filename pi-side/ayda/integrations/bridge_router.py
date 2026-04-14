from __future__ import annotations

from typing import Any


class BridgeRouter:
    def __init__(
        self,
        preferred_backend: str = "auto",
        pc_bridge: Any | None = None,
        local_bridge: Any | None = None,
    ) -> None:
        self.preferred_backend = preferred_backend
        self.pc_bridge = pc_bridge
        self.local_bridge = local_bridge

    def _ordered_bridges(self) -> list[tuple[str, Any]]:
        bridges = {
            "pc": self.pc_bridge,
            "local": self.local_bridge,
        }

        if self.preferred_backend == "pc":
            order = ["pc", "local"]
        elif self.preferred_backend == "local":
            order = ["local", "pc"]
        else:
            order = ["pc", "local"]

        return [(name, bridges[name]) for name in order if bridges.get(name) is not None]

    def is_available(self) -> bool:
        return any(bridge.is_available() for _, bridge in self._ordered_bridges())

    def describe_status(self) -> str:
        parts: list[str] = []
        for name, bridge in self._ordered_bridges():
            status = "hazir" if bridge.is_available() else "ulasilamiyor"
            parts.append(f"{name}:{status}")
        if not parts:
            return "hicbir-kopru-yok"
        return ", ".join(parts)

    def ask(self, text: str, role: str = "child", mode: str = "child") -> str:
        for _, bridge in self._ordered_bridges():
            if not bridge.is_available():
                continue
            response = bridge.ask(text=text, role=role, mode=mode)
            if isinstance(response, str) and response.strip():
                return response.strip()
        return "Ne PC tarafi ne de Pi uzerindeki yerel model su an hazir degil."
