from __future__ import annotations

import os

from aida.core.session import AidaSession
from aida.dialogue.manager import DialogueManager
from aida.integrations.pc_bridge import PCBridge, PCBridgeConfig


def build_pc_bridge() -> PCBridge:
    base_url = os.getenv("AIDA_PC_BASE_URL", "http://127.0.0.1:7000")
    timeout_sec = float(os.getenv("AIDA_PC_TIMEOUT", "8.0"))
    return PCBridge(PCBridgeConfig(base_url=base_url, timeout_sec=timeout_sec))


def main() -> None:
    print("AIDA v1 metin omurgası başlatıldı.")
    print("Çıkmak için: çıkış")
    print("Rol değiştirmek için: /role child veya /role parent")
    print("Ana zekâ sağlık kontrolü için: /health")
    print()

    session = AidaSession()
    pc_bridge = build_pc_bridge()
    manager = DialogueManager(pc_bridge=pc_bridge)

    while True:
        raw = input(f"[{session.active_user_role}/{session.current_mode}] Sen: ").strip()

        if raw.lower() == "çıkış":
            print("AIDA kapanıyor.")
            break

        if raw.startswith("/role "):
            new_role = raw.split(" ", 1)[1].strip().lower()
            if new_role in {"child", "parent"}:
                session.set_role(new_role)
                session.set_mode("parent" if new_role == "parent" else "child")
                print(f"AIDA: Rol güncellendi -> {new_role}")
            else:
                print("AIDA: Geçersiz rol. child veya parent kullan.")
            print()
            continue

        if raw == "/health":
            status = pc_bridge.is_available()
            print(f"AIDA: Ana zekâ bağlantısı -> {'hazır' if status else 'ulaşılamıyor'}")
            print()
            continue

        response = manager.process(raw, session)

        print(f"AIDA ({response.emotion}, {response.next_state}): {response.text}")
        print()


if __name__ == "__main__":
    main()
