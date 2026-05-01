from __future__ import annotations

import json
import os
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ayda.main import build_runtime


STATIC_DIR = Path(__file__).with_name("static")
INDEX_HTML = STATIC_DIR / "index.html"


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


settings, session, bridge_router, manager = build_runtime()


def build_status_payload() -> dict[str, Any]:
    return {
        "app": "ayda-web",
        "preferred_backend": settings.preferred_backend,
        "backend_status": bridge_router.describe_status(),
        "health": bridge_router.is_available(),
        "session": {
            "mode": session.current_mode,
            "role": session.active_user_role,
            "state": session.current_state,
            "last_intent": session.last_intent,
            "last_response": session.last_response,
            "recent_turns": [asdict(turn) for turn in session.recent_turns],
        },
    }


class AydaRequestHandler(BaseHTTPRequestHandler):
    server_version = "AydaHTTP/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        if _env_flag("AYDA_WEB_QUIET", True):
            return
        super().log_message(fmt, *args)

    def _write_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _write_html(self, path: Path) -> None:
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        if not raw.strip():
            return {}
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            return {}
        return payload

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            self._write_html(INDEX_HTML)
            return

        if self.path in {"/health", "/api/status"}:
            self._write_json(build_status_payload())
            return

        self._write_json({"error": "not-found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/chat":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._write_json({"error": "invalid-json"}, status=HTTPStatus.BAD_REQUEST)
                return

            text = str(payload.get("text", "")).strip()
            if not text:
                self._write_json({"error": "text-required"}, status=HTTPStatus.BAD_REQUEST)
                return

            role = str(payload.get("role", session.active_user_role)).strip().lower() or "child"
            mode = str(payload.get("mode", session.current_mode)).strip().lower() or "child"
            if role in {"child", "parent"}:
                session.set_role(role)
            if mode in {"child", "parent"}:
                session.set_mode(mode)

            response = manager.process(text, session)
            self._write_json(
                {
                    "answer": response.text,
                    "emotion": response.emotion,
                    "next_state": response.next_state,
                    "delegate": response.delegate,
                    "status": build_status_payload(),
                }
            )
            return

        if self.path == "/api/session":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._write_json({"error": "invalid-json"}, status=HTTPStatus.BAD_REQUEST)
                return

            role = str(payload.get("role", session.active_user_role)).strip().lower()
            mode = str(payload.get("mode", session.current_mode)).strip().lower()
            if role in {"child", "parent"}:
                session.set_role(role)
            if mode in {"child", "parent"}:
                session.set_mode(mode)
            self._write_json(build_status_payload())
            return

        self._write_json({"error": "not-found"}, status=HTTPStatus.NOT_FOUND)


def main() -> None:
    host = os.getenv("AYDA_WEB_HOST", "127.0.0.1")
    port = int(os.getenv("AYDA_WEB_PORT", "8090"))
    server = ThreadingHTTPServer((host, port), AydaRequestHandler)
    print(f"AYDA web kiosk arayuzu hazir: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
