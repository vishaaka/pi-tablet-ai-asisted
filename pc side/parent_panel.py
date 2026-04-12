from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from command_queue import push_command, get_pending_commands
from server_manager import (
    start_server,
    stop_server,
    start_all,
    stop_all,
    stop_all_safe,
    status_all,
)
from mode_manager import get_mode, set_mode
from draft_manager import add_draft, get_all_drafts, get_draft, delete_draft
from session_orchestrator import (
    load_settings as autonomy_load_settings,
    save_settings as autonomy_save_settings,
    start_session as autonomy_start_session,
    stop_session as autonomy_stop_session,
    get_session_state as autonomy_get_session_state,
    tick_session as autonomy_tick_session,
)
from asset_manager import (
    create_asset,
    list_assets,
    get_asset,
    update_asset,
    asset_stats,
)
from asset_history import list_asset_history
from scene_manager import (
    list_scenes,
    get_scene,
    create_scene,
    update_scene,
    delete_scene,
    scene_stats,
    build_scene_payload,
)

import requests
import os

app = FastAPI(title="Parent Control Panel")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE_DIR, "parent_panel_ui.html")
ASSETS_PATH = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_PATH, exist_ok=True)

# NOT:
# /assets API endpointleri ile çakışmaması için statik mount yolu /asset_files yapıldı
app.mount("/asset_files", StaticFiles(directory=ASSETS_PATH), name="asset_files")


def safe_get_json(url: str):
    try:
        r = requests.get(url, timeout=5)
        return JSONResponse(content=r.json())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=502)


@app.get("/")
def root():
    return {
        "panel": "ok",
        "open": "http://127.0.0.1:9100/panel",
        "mode": get_mode(),
    }


@app.get("/panel", response_class=HTMLResponse)
def panel():
    if not os.path.exists(HTML_PATH):
        return HTMLResponse(
            "<h1>parent_panel_ui.html bulunamadı</h1>",
            status_code=404,
        )

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/mode")
def current_mode():
    return {"mode": get_mode()}


@app.post("/mode/set")
def change_mode(mode: str):
    return set_mode(mode)


@app.get("/queue")
def queue_view():
    return {"commands": get_pending_commands()}


@app.post("/screen/speech_cards")
def set_speech_cards(words: list[str]):
    return push_command(
        "set_screen",
        {"screen": "speech_cards", "cards": words},
    )


@app.post("/screen/game")
def set_game(payload: dict):
    return push_command(
        "set_screen",
        {"screen": "interactive_game", **payload},
    )


@app.post("/screen/layered_scene")
def screen_layered_scene(payload: dict):
    try:
        built = build_scene_payload(payload)
        return push_command("set_screen", built)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.post("/session/shutdown_after")
def shutdown_after(minutes: int):
    return push_command("shutdown_after", {"minutes": minutes})


@app.post("/session/shutdown_now")
def shutdown_now():
    return push_command("shutdown_now")


@app.post("/widget/remove")
def remove_widget(widget_id: str):
    return push_command("remove_widget", {"widget_id": widget_id})


@app.post("/content/append")
def append_content(payload: dict):
    return push_command("append_content", payload)


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
    data = status_all()
    data["mode"] = get_mode()
    data["manual_asset_mode"] = True
    return data


# ---- Taslaklar ----

@app.get("/drafts")
def drafts_list():
    return {"drafts": get_all_drafts()}


@app.get("/draft")
def draft_get(name: str):
    draft = get_draft(name)
    if not draft:
        return JSONResponse({"error": "Taslak bulunamadı"}, status_code=404)
    return draft


@app.post("/draft/save")
def draft_save(payload: dict):
    name = payload.get("name", "").strip()
    data = payload.get("payload", {})
    if not name:
        return JSONResponse({"error": "Taslak adı boş olamaz"}, status_code=400)
    return add_draft(name, data)


@app.post("/draft/delete")
def draft_delete(name: str):
    return delete_draft(name)


# ---- Test modu yardımcıları ----

@app.post("/dev/fake_speech")
def dev_fake_speech():
    if get_mode() != "test":
        return JSONResponse(
            {"ok": False, "error": "Sadece test modunda kullanılabilir"},
            status_code=400,
        )

    try:
        requests.post(
            "http://127.0.0.1:8000/speech",
            json={
                "video_id": "test_video",
                "speech_attempt": True,
                "speech_level": "word",
                "response_time": 1.4,
                "target_word": "top",
                "child_output": "top",
                "success_level": "full_word",
            },
            timeout=5,
        )
        requests.post(
            "http://127.0.0.1:8000/speech",
            json={
                "video_id": "test_video",
                "speech_attempt": True,
                "speech_level": "phrase",
                "response_time": 2.0,
                "phrase": "mavi top",
                "success_level": "two_word_phrase",
                "spontaneous": True,
            },
            timeout=5,
        )
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ---- Otonom seans ----

@app.get("/autonomy/settings")
def autonomy_settings_get():
    return autonomy_load_settings()


@app.post("/autonomy/settings/save")
def autonomy_settings_save(payload: dict):
    saved = autonomy_save_settings(payload)
    return {"ok": True, "settings": saved}


@app.get("/autonomy/session/state")
def autonomy_session_state():
    return autonomy_get_session_state()


@app.post("/autonomy/session/start")
def autonomy_session_start(payload: dict | None = None):
    payload = payload or {}
    return autonomy_start_session(payload)


@app.post("/autonomy/session/stop")
def autonomy_session_stop(reason: str = "manual_stop"):
    return autonomy_stop_session(reason=reason)


@app.post("/autonomy/session/tick")
def autonomy_session_tick(force: bool = False):
    return autonomy_tick_session(force=force)


# ---- Asset Stüdyosu ----

@app.get("/assets/list")
def assets_list(
    q: str = "",
    label: str = "",
    tag: str = "",
    interest: str = "",
    status: str = "",
):
    return {
        "assets": list_assets(
            q=q,
            label=label,
            tag=tag,
            interest=interest,
            status=status,
        )
    }


@app.get("/assets/get")
def assets_get(asset_id: str):
    item = get_asset(asset_id)
    if not item:
        return JSONResponse({"error": "Asset bulunamadı"}, status_code=404)
    return item


@app.post("/assets/create")
def assets_create(payload: dict):
    try:
        item = create_asset(payload)
        return {"ok": True, "asset": item}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.post("/assets/update")
def assets_update(asset_id: str, payload: dict):
    try:
        item = update_asset(asset_id, payload)
        return {"ok": True, "asset": item}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.get("/assets/stats")
def assets_stats():
    return asset_stats()


@app.get("/assets/history")
def assets_history(limit: int = 100):
    return {"items": list_asset_history(limit=limit)}


# ---- Katmanlı Sahne Editörü ----

@app.get("/scenes/list")
def scenes_list(
    q: str = "",
    target_word: str = "",
    status: str = "",
):
    return {
        "items": list_scenes(
            q=q,
            target_word=target_word,
            status=status,
        )
    }


@app.get("/scenes/get")
def scenes_get(scene_id: str):
    item = get_scene(scene_id)
    if not item:
        return JSONResponse({"error": "Sahne bulunamadı"}, status_code=404)
    return item


@app.post("/scenes/create")
def scenes_create(payload: dict):
    try:
        item = create_scene(payload)
        return {"ok": True, "scene": item}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.post("/scenes/update")
def scenes_update(scene_id: str, payload: dict):
    try:
        item = update_scene(scene_id, payload)
        return {"ok": True, "scene": item}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.post("/scenes/delete")
def scenes_delete(scene_id: str):
    try:
        return delete_scene(scene_id)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.get("/scenes/stats")
def scenes_stats():
    return scene_stats()


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("parent_panel:app", host="127.0.0.1", port=9100, reload=False)