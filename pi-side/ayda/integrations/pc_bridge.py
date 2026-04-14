from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import requests


@dataclass
class PCBridgeConfig:
    base_url: str = "http://127.0.0.1:7000"
    timeout_sec: float = 8.0


class PCBridge:
    def __init__(self, config: Optional[PCBridgeConfig] = None) -> None:
        self.config = config or PCBridgeConfig()

    @property
    def health_url(self) -> str:
        return f"{self.config.base_url.rstrip('/')}/health"

    @property
    def chat_url(self) -> str:
        return f"{self.config.base_url.rstrip('/')}/chat"

    def is_available(self) -> bool:
        try:
            response = requests.get(self.health_url, timeout=self.config.timeout_sec)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def ask(self, text: str, role: str = "child", mode: str = "child") -> str:
        payload = {
            "text": text,
            "role": role,
            "mode": mode,
        }

        try:
            response = requests.post(
                self.chat_url,
                json=payload,
                timeout=self.config.timeout_sec,
            )
            response.raise_for_status()

            data = response.json()
            answer = data.get("answer")

            if isinstance(answer, str) and answer.strip():
                return answer.strip()

            return "Ana zekâ yanıt verdi ama içerik boş geldi."

        except requests.Timeout:
            return "Ana zekâ bağlantısı zaman aşımına uğradı."
        except requests.RequestException as exc:
            return f"Ana zekâ bağlantısında sorun oluştu: {exc.__class__.__name__}"
        except ValueError:
            return "Ana zekâdan geçersiz JSON yanıtı geldi."
