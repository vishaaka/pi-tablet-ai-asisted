from db import profil_getir


def ilgiye_gore_sorgu_uret(konu):
    profil = profil_getir()

    if not profil:
        return konu

    en_iyi = sorted(
        profil,
        key=lambda x: x["skor"],
        reverse=True
    )[0]

    return f"{en_iyi['kategori']} {konu}".strip()