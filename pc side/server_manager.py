import subprocess
import socket
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BAT_PATH = BASE_DIR / "manage_servers.bat"

PANEL_PORT = 9100
TOOL_PORT = 8000
MIDDLEWARE_PORT = 7000
DASHBOARD_PORT = 9000


def _run_bat(*args):
    cmd = [str(BAT_PATH), *args]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=True,
        cwd=str(BASE_DIR)
    )
    return {
        "ok": result.returncode == 0,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "returncode": result.returncode,
    }


def _is_port_open(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def status_all():
    return {
        "panel": _is_port_open(PANEL_PORT),
        "tool": _is_port_open(TOOL_PORT),
        "middleware": _is_port_open(MIDDLEWARE_PORT),
        "dashboard": _is_port_open(DASHBOARD_PORT),
        "ports": {
            "panel": PANEL_PORT,
            "tool": TOOL_PORT,
            "middleware": MIDDLEWARE_PORT,
            "dashboard": DASHBOARD_PORT,
        },
        "panel_url": f"http://127.0.0.1:{PANEL_PORT}/panel"
    }


def start_all():
    result = _run_bat("start", "all")
    return {
        "ok": result["ok"],
        "action": "start_all",
        "result": result,
        "status": status_all()
    }


def stop_all():
    result = _run_bat("stop", "all")
    return {
        "ok": result["ok"],
        "action": "stop_all",
        "result": result,
        "status": status_all()
    }


def stop_all_safe():
    result = _run_bat("stop", "all_safe")
    return {
        "ok": result["ok"],
        "action": "stop_all_safe",
        "result": result,
        "status": status_all()
    }


def start_server(name: str):
    result = _run_bat("start", name)
    return {
        "ok": result["ok"],
        "action": f"start_{name}",
        "result": result,
        "status": status_all()
    }


def stop_server(name: str):
    result = _run_bat("stop", name)
    return {
        "ok": result["ok"],
        "action": f"stop_{name}",
        "result": result,
        "status": status_all()
    }