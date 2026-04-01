import os
from tinydb import TinyDB, Query
from datetime import datetime

os.makedirs("data", exist_ok=True)

DB_PATH = "data/db.json"

if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        f.write("{}")

db = TinyDB(DB_PATH)

izleme = db.table("izleme")
profil = db.table("profil")

User = Query()


def izleme_kaydet(video_id, attention, kategori="genel"):
    izleme.insert({
        "video_id": video_id,
        "attention": attention,
        "kategori": kategori,
        "timestamp": datetime.now().isoformat()
    })


def profil_guncelle(kategori, skor):
    mevcut = profil.get(User.kategori == kategori)

    if mevcut:
        profil.update(
            {"skor": mevcut["skor"] + skor},
            User.kategori == kategori
        )
    else:
        profil.insert({
            "kategori": kategori,
            "skor": skor
        })


def profil_getir():
    return profil.all()