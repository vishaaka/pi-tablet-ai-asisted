def ai_oneri(attention, speech_level, interest):
    if attention < 0.3:
        return {
            "action": "change_video",
            "reason": "dikkat düşük"
        }

    if speech_level == "pre-speech":
        return {
            "action": "wait",
            "content": "visual"
        }

    if speech_level == "sound":
        return {
            "action": "ask_simple",
            "content": "interactive"
        }

    if speech_level == "word":
        return {
            "action": "expand",
            "content": "story"
        }

    return {
        "action": "conversation",
        "content": "advanced"
    }