import json
import requests
from fastapi import FastAPI
from config import LM_STUDIO_URL, MODEL, TOOL_PROMPT

app = FastAPI()


def llm_call(text: str):
    r = requests.post(
        LM_STUDIO_URL,
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": TOOL_PROMPT},
                {"role": "user", "content": text}
            ],
            "temperature": 0.2
        },
        timeout=30
    )

    content = r.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except Exception:
        return {"tool": "chat", "response": "Anlayamadım"}


def handle_tool(data: dict):
    if data.get("tool") == "video_search":
        r = requests.get(
            "http://localhost:8000/videos",
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