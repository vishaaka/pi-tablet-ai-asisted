from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class LocalLLMBridgeConfig:
    base_url: str = "http://127.0.0.1:8080"
    timeout_sec: float = 20.0
    model: str = "ayda-qwen2.5-1.5b-tr-seed-q4_k_m.gguf"
    max_tokens: int = 160
    temperature: float = 0.7
    system_prompt: str = (
        "Sen AYDA'sin. Turkce konusan, neseli, sabirli ve cocuk dostu bir oyun arkadasisin. "
        "Kisa cumleler kullan. Cevaplari sicak, destekleyici ve guvenli tut."
    )


class LocalLLMBridge:
    def __init__(self, config: Optional[LocalLLMBridgeConfig] = None) -> None:
        self.config = config or LocalLLMBridgeConfig()

    @property
    def base_url(self) -> str:
        return self.config.base_url.rstrip("/")

    @property
    def chat_url(self) -> str:
        return f"{self.base_url}/v1/chat/completions"

    def is_available(self) -> bool:
        for url in (self.base_url, f"{self.base_url}/health"):
            try:
                response = requests.get(url, timeout=min(self.config.timeout_sec, 5.0))
                if response.status_code < 500:
                    return True
            except requests.RequestException:
                continue
        return False

    def ask(self, text: str, role: str = "child", mode: str = "child") -> str:
        context_hint = (
            f"Kullanici rolu: {role}. Mod: {mode}. "
            "Cevaplar en fazla 2-3 kisa cumle olsun."
        )
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "system", "content": context_hint},
                {"role": "user", "content": text},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False,
        }

        try:
            response = requests.post(
                self.chat_url,
                json=payload,
                timeout=self.config.timeout_sec,
            )
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices") or []
            if choices:
                message = choices[0].get("message") or {}
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
            return "Yerel model yanit verdi ama icerik bos geldi."
        except requests.Timeout:
            return "Yerel model yaniti zaman asimina ugradi."
        except requests.RequestException as exc:
            return f"Yerel model baglantisinda sorun olustu: {exc.__class__.__name__}"
        except ValueError:
            return "Yerel modelden gecersiz JSON yaniti geldi."
