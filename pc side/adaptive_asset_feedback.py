from attention_memory import add_attention


def process_attention_event(payload: dict):
    asset_id = payload.get("asset_id", "")
    label = payload.get("label", "")
    seconds = float(payload.get("attention_seconds", 0))

    if not asset_id or seconds <= 0:
        return {
            "ok": False,
            "reason": "invalid_payload"
        }

    item = add_attention(
        asset_id=asset_id,
        seconds=seconds,
        label=label
    )

    return {
        "ok": True,
        "memory": item
    }