from fastapi import FastAPI
from core.ai_engine import ai_oneri
from core.milestone_engine import (
    get_new_word_count,
    get_two_word_count,
    get_two_word_rate,
)
from core.youtube_tool import youtube_ara
from storage.db import izleme_kaydet, profil_guncelle
from storage.speech import speech_kaydet, konusma_analiz, konusma_seviyesi

app = FastAPI()


@app.get("/videos")
def videos(konu: str):
    return {"videos": youtube_ara(konu)}


@app.post("/attention")
def attention(data: dict):
    video_id = data.get("video_id", "")
    att = float(data.get("attention", 0))
    kategori = data.get("kategori", "genel")

    izleme_kaydet(video_id, att, kategori)

    if att > 0.7:
        profil_guncelle(kategori, att)

    return {"ok": True}


@app.post("/speech")
def speech_api(data: dict):
    speech_kaydet(data)
    return {"ok": True}


@app.get("/ai_decision")
def ai_decision():
    speech_data = konusma_analiz()
    level = konusma_seviyesi(speech_data)
    karar = ai_oneri(0.5, level, "genel")

    return {
        "speech": speech_data,
        "level": level,
        "decision": karar,
        "new_word_count": get_new_word_count(),
        "two_word_count": get_two_word_count(),
        "two_word_rate": get_two_word_rate()
    }
