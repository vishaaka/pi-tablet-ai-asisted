import json
import requests
from fastapi import FastAPI
from config.settings import get_settings, service_url

app = FastAPI()


def build_prompt(text: str, role: str = "child", mode: str = "child") -> str:
    role = str(role or "child").strip().lower()
    mode = str(mode or "child").strip().lower()

    context = (
        f"Konuşan rolü: {role}\n"
        f"Çalışma modu: {mode}\n"
        "Yanıt kısa, güvenli, çocuk dostu ve Türkçe olsun.\n"
        "Eğer kullanıcı ebeveyn ise komut niyetini daha net ele al.\n\n"
    )
    return context + str(text or "").strip()


def llm_call(text: str, role: str = "child", mode: str = "child"):
    llm_settings = get_settings()["llm"]
    try:
        r = requests.post(
            llm_settings["lm_studio_url"],
            json={
                "model": llm_settings["model"],
                "messages": [
                    {"role": "system", "content": llm_settings["tool_prompt"]},
                    {"role": "user", "content": build_prompt(text, role=role, mode=mode)}
                ],
                "temperature": llm_settings.get("temperature", 0.2)
            },
            timeout=float(llm_settings.get("timeout_sec", 30))
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
    except requests.Timeout:
        return {"tool": "chat", "response": "Ana zekâ yanıtı zaman aşımına uğradı."}
    except requests.RequestException:
        return {"tool": "chat", "response": "Ana zekâ servisine şu an ulaşılamıyor."}
    except (KeyError, IndexError, TypeError, ValueError):
        return {"tool": "chat", "response": "Ana zekâdan beklenen yanıt alınamadı."}

    try:
        return json.loads(content)
    except Exception:
        return {"tool": "chat", "response": "Anlayamadım"}


def handle_tool(data: dict):
    args = data.get("args", {}) or {}

    if data.get("tool") == "video_search":
        r = requests.get(
            service_url("tool", "/videos"),
            params={"konu": args["query"]},
            timeout=20
        )
        return {
            "action": "show_grid",
            "data": r.json()
        }

    if data.get("tool") == "image_generate":
        r = requests.post(
            service_url("media", "/generate/image"),
            json={"prompt": args.get("prompt", "")},
            timeout=120,
        )
        r.raise_for_status()
        payload = r.json()
        return {
            "action": "show_image",
            "text": "Görsel hazırlandı.",
            "data": payload,
        }

    if data.get("tool") == "speech_generate":
        r = requests.post(
            service_url("media", "/generate/speech"),
            json={"text": args.get("text", "")},
            timeout=120,
        )
        r.raise_for_status()
        payload = r.json()
        return {
            "action": "play_audio",
            "text": "Ses çıktısı hazırlandı.",
            "data": payload,
        }

    if data.get("tool") == "video_generate":
        r = requests.post(
            service_url("media", "/generate/video"),
            json={"prompt": args.get("prompt", "")},
            timeout=180,
        )
        r.raise_for_status()
        payload = r.json()
        return {
            "action": "play_video",
            "text": "Video hazırlandı.",
            "data": payload,
        }

    return {
        "action": "speak",
        "text": data.get("response", "")
    }


def process_text(text: str, role: str = "child", mode: str = "child") -> dict:
    tool = llm_call(text, role=role, mode=mode)
    return handle_tool(tool)


def to_chat_payload(result: dict) -> dict:
    action = result.get("action", "speak")

    if action == "show_grid":
        videos = result.get("data", {}).get("videos", [])
        count = len(videos) if isinstance(videos, list) else 0
        if count:
            answer = f"{count} video önerisi hazırladım."
        else:
            answer = "Video önerisi hazırlamaya çalıştım ama içerik bulunamadı."
    elif action == "show_image":
        answer = str(result.get("text") or "Görsel hazır.")
    elif action == "play_audio":
        answer = str(result.get("text") or "Ses hazır.")
    elif action == "play_video":
        answer = str(result.get("text") or "Video hazır.")
    else:
        answer = str(result.get("text") or "").strip() or "Yanıt üretildi ama metin boş geldi."

    return {
        "ok": True,
        "answer": answer,
        "action": action,
        "data": result.get("data"),
    }


@app.get("/health")
def health():
    return {"ok": True, "service": "middleware"}


@app.post("/chat")
def chat(data: dict):
    result = process_text(
        text=data.get("text", ""),
        role=data.get("role", "child"),
        mode=data.get("mode", "child"),
    )
    return to_chat_payload(result)


@app.post("/process")
def process(data: dict):
    return process_text(
        text=data["text"],
        role=data.get("role", "child"),
        mode=data.get("mode", "child"),
    )
