import os
from tinydb import TinyDB, Query
from datetime import datetime
from mode_manager import get_mode

os.makedirs("data", exist_ok=True)
User = Query()

def get_db():
    mode = get_mode()
    path = f"data/{mode}_db.json"
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("{}")
    return TinyDB(path)

def izleme_kaydet(video_id, attention, kategori="genel"):
    db = get_db()
    izleme = db.table("izleme")
    izleme.insert({
        "video_id": video_id,
        "attention": attention,
        "kategori": kategori,
        "timestamp": datetime.now().isoformat(),
        "mode": get_mode()
    })

def profil_guncelle(kategori, skor):
    db = get_db()
    profil = db.table("profil")
    mevcut = profil.get(User.kategori == kategori)

    if mevcut:
        profil.update({"skor": mevcut["skor"] + skor}, User.kategori == kategori)
    else:
        profil.insert({"kategori": kategori, "skor": skor})

def profil_getir():
    db = get_db()
    profil = db.table("profil")
    return profil.all()