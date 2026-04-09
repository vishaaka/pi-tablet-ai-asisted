from adaptive_asset_feedback import process_attention_event


def on_attention_detected(
    asset_id: str,
    label: str,
    attention_seconds: float
):
    return process_attention_event({
        "asset_id": asset_id,
        "label": label,
        "attention_seconds": attention_seconds
    })