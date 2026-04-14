from storage.speech import tum_speech_kayitlari


def get_word_milestones():
    kayitlar = tum_speech_kayitlari()

    by_word = {}

    for item in kayitlar:
        target = (item.get("target_word") or "").strip()
        if not target:
            continue

        if target not in by_word:
            by_word[target] = {
                "word": target,
                "previous": "",
                "current": "",
                "status": "gelişiyor",
                "best_rank": -1
            }

        success = (item.get("success_level") or "").strip()
        child_output = (item.get("child_output") or "").strip()

        rank_map = {
            "none": 0,
            "sound": 1,
            "partial_word": 2,
            "full_word": 3
        }

        rank = rank_map.get(success, -1)

        # previous: partial/sound gibi önceki form
        if success in ("sound", "partial_word") and child_output:
            by_word[target]["previous"] = child_output

        # current: en iyi çıkan form
        if rank >= by_word[target]["best_rank"]:
            by_word[target]["best_rank"] = rank
            by_word[target]["current"] = child_output or target

            if success == "full_word":
                by_word[target]["status"] = "tam"
            elif success in ("sound", "partial_word"):
                by_word[target]["status"] = "gelişiyor"

    result = []
    for _, value in by_word.items():
        value.pop("best_rank", None)
        result.append(value)

    result.sort(key=lambda x: x["word"].lower())
    return result


def get_two_word_phrases():
    kayitlar = tum_speech_kayitlari()

    phrase_map = {}

    for item in kayitlar:
        success = (item.get("success_level") or "").strip()
        phrase = (item.get("phrase") or "").strip()

        if success != "two_word_phrase":
            continue

        if not phrase:
            continue

        if phrase not in phrase_map:
            phrase_map[phrase] = {
                "phrase": phrase,
                "spontaneous": bool(item.get("spontaneous", False)),
                "count": 0
            }

        phrase_map[phrase]["count"] += 1

        if item.get("spontaneous", False):
            phrase_map[phrase]["spontaneous"] = True

    result = list(phrase_map.values())
    result.sort(key=lambda x: (-x["count"], x["phrase"].lower()))
    return result


def get_new_word_count():
    return sum(1 for x in get_word_milestones() if x.get("status") == "tam")


def get_two_word_count():
    return len(get_two_word_phrases())


def get_two_word_rate():
    kayitlar = tum_speech_kayitlari()
    if not kayitlar:
        return 0

    two_word = sum(
        1 for x in kayitlar
        if (x.get("success_level") or "") == "two_word_phrase"
    )

    return round(two_word / len(kayitlar), 2)


def get_milestone_payload():
    return {
        "words": get_word_milestones(),
        "two_word_phrases": get_two_word_phrases()
    }
