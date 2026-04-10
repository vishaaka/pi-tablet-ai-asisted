from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


app = FastAPI()


class ChatRequest(BaseModel):
    text: str
    role: str = "child"
    mode: str = "child"


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    text = req.text.lower()

    if "hikaye" in text or "masal" in text:
        answer = "Bir varmış bir yokmuş, meraklı bir çocuk yeni şeyler öğrenmeyi çok severmiş."
    elif "neden" in text or "nasıl" in text:
        answer = "Bu soruyu daha ayrıntılı açıklayabilirim. İstersen birlikte adım adım gidelim."
    elif req.role == "parent":
        answer = f"Ebeveyn komutu işlendi: {req.text}"
    else:
        answer = f"Ana zekâ bu isteği aldı: {req.text}"

    return {"answer": answer}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
