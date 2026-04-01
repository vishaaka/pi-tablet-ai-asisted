from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from command_queue import push_command, get_pending_commands
from server_manager import (
    start_server,
    stop_server,
    start_all,
    stop_all,
    stop_all_safe,
    status_all,
)
import requests
import os

app = FastAPI(title="Parent Control Panel")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE_DIR, "parent_panel_ui.html")


def safe_get_json(url: str):
    try:
        r = requests.get(url, timeout=5)
        return JSONResponse(content=r.json())
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=502
        )


@app.get("/")
def root():
    return {
        "panel": "ok",
        "open": "http://127.0.0.1:9100/panel"
    }


@app.get("/panel", response_class=HTMLResponse)
def panel():
    if not os.path.exists(HTML_PATH):
        return HTMLResponse(
            "<h1>parent_panel_ui.html bulunamadı</h1>",
            status_code=404
        )

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/queue")
def queue_view():
    return {"commands": get_pending_commands()}


@app.post("/screen/speech_cards")
def set_speech_cards(words: list[str]):
    return push_command(
        "set_screen",
        {
            "screen": "speech_cards",
            "cards": words
        }
    )


@app.post("/screen/game")
def set_game(payload: dict):
    return push_command(
        "set_screen",
        {
            "screen": "interactive_game",
            **payload
        }
    )


@app.post("/session/shutdown_after")
def shutdown_after(minutes: int):
    return push_command(
        "shutdown_after",
        {"minutes": minutes}
    )


@app.post("/session/shutdown_now")
def shutdown_now():
    return push_command("shutdown_now")


@app.post("/widget/remove")
def remove_widget(widget_id: str):
    return push_command(
        "remove_widget",
        {"widget_id": widget_id}
    )


@app.post("/content/append")
def append_content(payload: dict):
    return push_command(
        "append_content",
        payload
    )


@app.post("/server/start")
def server_start(name: str):
    return start_server(name)


@app.post("/server/stop")
def server_stop(name: str):
    return stop_server(name)


@app.post("/server/start_all")
def server_start_all():
    return start_all()


@app.post("/server/stop_all")
def server_stop_all():
    return stop_all()


@app.post("/server/stop_all_safe")
def server_stop_all_safe():
    return stop_all_safe()


@app.get("/server/status")
def server_status():
    return status_all()


# ---- Panel için proxy endpointler ----

@app.get("/panel/api/summary")
def panel_api_summary():
    return safe_get_json("http://127.0.0.1:9000/api/summary")


@app.get("/panel/api/milestones")
def panel_api_milestones():
    return safe_get_json("http://127.0.0.1:9000/api/milestones")


@app.get("/panel/api/ai_decision")
def panel_api_ai_decision():
    return safe_get_json("http://127.0.0.1:8000/ai_decision")