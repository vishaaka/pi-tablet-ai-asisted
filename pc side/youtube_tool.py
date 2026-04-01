import requests
from config import API_KEY
from db import profil_getir

YASAK_KELIMELER = [
    "korku", "şiddet", "silah", "adult", "horror",
    "violence", "weapon", "18+"
]

KALITE_KELIMELER = [
    "çocuk", "kids", "eğitici", "learning", "learn",
    "okul öncesi", "preschool", "abc", "sayma"
]


def guvenli_mi(title, desc):
    text = (title + " " + desc).lower()
    return not any(k in text for k in YASAK_KELIMELER)


def kalite_skor(title, desc):
    text = (title + " " + desc).lower()
    score = 0
    for k in KALITE_KELIMELER:
        if k in text:
            score += 2
    return score


def ilgi_skoru(title):
    profil = profil_getir()
    if not profil:
        return 0

    text = title.lower()
    score = 0

    for item in profil:
        kategori = item["kategori"]
        ilgi = item["skor"]
        if kategori in text:
            score += ilgi

    return score


def toplam_skor(title, desc):
    return kalite_skor(title, desc) + ilgi_skoru(title)


def enrich_query(query):
    profil = profil_getir()

    if not profil:
        return f"{query} çocuk eğitici".strip()

    top = sorted(profil, key=lambda x: x["skor"], reverse=True)[:2]
    ekstra = " ".join([x["kategori"] for x in top])

    return f"{query} {ekstra} çocuk eğitici".strip()


def fallback(query):
    return [{
        "video_id": "",
        "title": f"{query} için uygun içerik bulunamadı",
        "thumbnail": ""
    }]


def youtube_ara(query):
    query = enrich_query(query)

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY,
        "q": query,
        "part": "snippet",
        "type": "video",
        "safeSearch": "strict",
        "maxResults": 12
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    adaylar = []

    for item in data.get("items", []):
        snip = item["snippet"]
        title = snip["title"]
        desc = snip.get("description", "")
        video_id = item["id"]["videoId"]

        if not guvenli_mi(title, desc):
            continue

        skor = toplam_skor(title, desc)

        adaylar.append({
            "video_id": video_id,
            "title": title,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/0.jpg",
            "score": skor
        })

    adaylar = sorted(adaylar, key=lambda x: x["score"], reverse=True)

    if not adaylar:
        return fallback(query)

    return [
        {
            "video_id": v["video_id"],
            "title": v["title"],
            "thumbnail": v["thumbnail"]
        }
        for v in adaylar[:6]
    ]