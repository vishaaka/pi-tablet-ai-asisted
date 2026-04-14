from __future__ import annotations

from ayda.config import AydaSettings, load_settings
from ayda.core.session import AydaSession
from ayda.dialogue.manager import DialogueManager
from ayda.integrations.bridge_router import BridgeRouter
from ayda.integrations.local_llm_bridge import LocalLLMBridge, LocalLLMBridgeConfig
from ayda.integrations.pc_bridge import PCBridge, PCBridgeConfig


def build_bridge_router(settings: AydaSettings) -> BridgeRouter:
    pc_bridge = None
    if settings.pc.enabled:
        pc_bridge = PCBridge(
            PCBridgeConfig(
                base_url=settings.pc.base_url,
                timeout_sec=settings.pc.timeout_sec,
            )
        )

    local_bridge = None
    if settings.local.enabled:
        local_bridge = LocalLLMBridge(
            LocalLLMBridgeConfig(
                base_url=settings.local.base_url,
                timeout_sec=settings.local.timeout_sec,
                model=settings.local.model,
                max_tokens=settings.local.max_tokens,
                temperature=settings.local.temperature,
                system_prompt=settings.local.system_prompt,
            )
        )

    return BridgeRouter(
        preferred_backend=settings.preferred_backend,
        pc_bridge=pc_bridge,
        local_bridge=local_bridge,
    )


def main() -> None:
    settings = load_settings()

    print("AYDA v1 metin omurgası başlatıldı.")
    print("Çıkmak için: çıkış")
    print("Rol değiştirmek için: /role child veya /role parent")
    print("Ana zekâ sağlık kontrolü için: /health")
    print("Köprü durumunu görmek için: /backend")
    print(f"Köprü tercihi: {settings.preferred_backend}")
    print()

    session = AydaSession()
    bridge_router = build_bridge_router(settings)
    manager = DialogueManager(pc_bridge=bridge_router)

    while True:
        raw = input(f"[{session.active_user_role}/{session.current_mode}] Sen: ").strip()

        if raw.lower() == "çıkış":
            print("AYDA kapanıyor.")
            break

        if raw.startswith("/role "):
            new_role = raw.split(" ", 1)[1].strip().lower()
            if new_role in {"child", "parent"}:
                session.set_role(new_role)
                session.set_mode("parent" if new_role == "parent" else "child")
                print(f"AYDA: Rol güncellendi -> {new_role}")
            else:
                print("AYDA: Geçersiz rol. child veya parent kullan.")
            print()
            continue

        if raw == "/health":
            status = bridge_router.is_available()
            print(f"AYDA: Ana zekâ bağlantısı -> {'hazır' if status else 'ulaşılamıyor'}")
            print()
            continue

        if raw == "/backend":
            print(f"AYDA: Köprü durumları -> {bridge_router.describe_status()}")
            print()
            continue

        response = manager.process(raw, session)

        print(f"AYDA ({response.emotion}, {response.next_state}): {response.text}")
        print()


if __name__ == "__main__":
    main()
