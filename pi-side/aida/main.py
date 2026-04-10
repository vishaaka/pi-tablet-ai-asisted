from __future__ import annotations

from aida.core.session import AidaSession
from aida.dialogue.manager import DialogueManager


class DummyPCBridge:
    def ask(self, text: str) -> str:
        return f"Bu istek ana zekâya yönlendirildi: {text}"


def main() -> None:
    print("AIDA v1 metin omurgası başlatıldı.")
    print("Çıkmak için: çıkış")
    print("Rol değiştirmek için: /role child veya /role parent")
    print()

    session = AidaSession()
    manager = DialogueManager(pc_bridge=DummyPCBridge())

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
            continue

        response = manager.process(raw, session)

        print(f"AIDA ({response.emotion}, {response.next_state}): {response.text}")
        print()


if __name__ == "__main__":
    main()
