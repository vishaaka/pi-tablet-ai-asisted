from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from speech import konusma_analiz
from tinydb import TinyDB
from milestone_engine import (
    get_milestone_payload,
    get_new_word_count,
    get_two_word_count,
)
import os

app = FastAPI()

os.makedirs("data", exist_ok=True)
db = TinyDB("data/db.json")
izleme = db.table("izleme")


@app.get("/", response_class=HTMLResponse)
def dash():
    s = konusma_analiz()

    return f"""
    <html>
    <body style='background:#111;color:white;font-family:Arial'>
    <h1>🧠 Dashboard</h1>
    <p>Deneme: {s['attempt_rate']}</p>
    <p>Seviye: {s['avg_level']}</p>
    <p>Tepki: {s['avg_response']}</p>
    </body>
    </html>
    """


@app.get("/api/summary")
def api_summary():
    all_items = izleme.all()
    avg_attention = 0

    if all_items:
        avg_attention = sum(
            float(x.get("attention", 0))
            for x in all_items
        ) / len(all_items)

    return {
        "average_attention_percent": round(avg_attention * 100, 2),
        "new_word_count": get_new_word_count(),
        "two_word_count": get_two_word_count(),
        "priorities": [
            {
                "title": "Son ses tamamlama",
                "score": 78,
                "note": "Kelime sonlarını tam söyleme çalışılmalı."
            },
            {
                "title": "2'li ifade üretimi",
                "score": 66,
                "note": "Nesne + sıfat yapıları artırılmalı."
            }
        ]
    }


@app.get("/api/milestones")
def api_milestones():
    return get_milestone_payload()