import json
import requests
from fastapi import FastAPI
from config.settings import get_settings, service_url

app = FastAPI()


def llm_call(text: str):
    llm_settings = get_settings()["llm"]
    r = requests.post(
        llm_settings["lm_studio_url"],
        json={
            "model": llm_settings["model"],
            "messages": [
                {"role": "system", "content": llm_settings["tool_prompt"]},
                {"role": "user", "content": text}
            ],
            "temperature": llm_settings.get("temperature", 0.2)
        },
        timeout=float(llm_settings.get("timeout_sec", 30))
    )

    content = r.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except Exception:
        return {"tool": "chat", "response": "Anlayamadım"}


def handle_tool(data: dict):
    if data.get("tool") == "video_search":
        r = requests.get(
            service_url("tool", "/videos"),
            params={"konu": data["args"]["query"]},
            timeout=20
        )
        return {
            "action": "show_grid",
            "data": r.json()
        }

    return {
        "action": "speak",
        "text": data.get("response", "")
    }


@app.post("/process")
def process(data: dict):
    tool = llm_call(data["text"])
    return handle_tool(tool)
