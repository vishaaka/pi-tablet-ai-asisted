from tinydb import TinyDB
from datetime import datetime
import os

os.makedirs("data", exist_ok=True)

db = TinyDB("data/db.json")
speech = db.table("speech")


def speech_kaydet(data):
    speech.insert({
        "video_id": data.get("video_id", ""),
        "speech_attempt": data.get("speech_attempt", False),
        "speech_level": data.get("speech_level", "none"),
        "response_time": data.get("response_time", 0),
        "target_word": data.get("target_word", ""),
        "child_output": data.get("child_output", ""),
        "success_level": data.get("success_level", ""),
        "phrase": data.get("phrase", ""),
        "spontaneous": data.get("spontaneous", False),
        "timestamp": datetime.now().isoformat()
    })


def konusma_analiz():
    veriler = speech.all()

    if not veriler:
        return {
            "attempt_rate": 0,
            "avg_level": 0,
            "avg_response": 0
        }

    toplam = len(veriler)

    attempt = sum(
        1 for v in veriler
        if v.get("speech_attempt")
    )

    level_map = {
        "none": 0,
        "sound": 1,
        "word": 2,
        "phrase": 3
    }

    ort_level = sum(
        level_map.get(v.get("speech_level", "none"), 0)
        for v in veriler
    ) / toplam

    ort_response = sum(
        v.get("response_time", 0)
        for v in veriler
    ) / toplam

    return {
        "attempt_rate": round(attempt / toplam, 2),
        "avg_level": round(ort_level, 2),
        "avg_response": round(ort_response, 2)
    }


def konusma_seviyesi(data):
    if data["avg_level"] < 0.5:
        return "pre-speech"
    elif data["avg_level"] < 1.5:
        return "sound"
    elif data["avg_level"] < 2.5:
        return "word"
    return "phrase"


def tum_speech_kayitlari():
    return speech.all()