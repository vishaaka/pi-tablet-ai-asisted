from __future__ import annotations

from typing import Dict, List


TEMPLATES: Dict[str, List[str]] = {
    "greeting": [
        "Merhaba, ben AIDA.",
        "Selam, ben buradayım.",
        "Merhaba! Birlikte oynayabiliriz."
    ],
    "daily_chat": [
        "Seni dinliyorum.",
        "İstersen beraber konuşabiliriz.",
        "Bugün ne yapmak istersin?"
    ],
    "play_request": [
        "Harika. Bir oyun oynayalım mı?",
        "Tamam. Oyun başlatabiliriz.",
        "Süper. Sana küçük bir oyun hazırlayabilirim."
    ],
    "help": [
        "Tabii, sana yardım etmeye çalışırım.",
        "Buradayım. Birlikte deneyelim.",
        "İstersen adım adım gidelim."
    ],
    "repeat": [
        "Tabii, tekrar söyleyebilirim.",
        "Tamam, bir kez daha anlatayım.",
        "Elbette, yeniden deneyelim."
    ],
    "parent_required": [
        "Bunu ebeveyn izniyle yapabilirim.",
        "Bu işlem için ebeveyn modu gerekiyor.",
        "Önce bir ebeveynin onayı gerekli."
    ],
    "story_request": [
        "Kısa bir hikâye ister misin? Bunu hazırlayabilirim.",
        "Bir masal anlatmamı ister misin?",
        "Hikâye modu açılabilir."
    ],
    "object_talk": [
        "İstersen bana bir nesne gösterebilirsin.",
        "Beraber bir nesne hakkında konuşabiliriz.",
        "Bana göster, birlikte bakalım."
    ],
    "unknown": [
        "Seni tam anlayamadım. Bir daha söyler misin?",
        "Bunu biraz daha farklı söyleyebilir misin?",
        "Anlamama yardımcı olur musun?"
    ],
}


def choose_template(intent: str) -> str:
    options = TEMPLATES.get(intent, TEMPLATES["unknown"])
    return options[0]
