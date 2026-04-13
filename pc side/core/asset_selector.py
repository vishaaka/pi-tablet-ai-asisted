import random

from storage.asset_manager import list_assets
from storage.attention_memory import (
    get_attention_score,
    get_label_attention_boost,
)
from core.dictionary_bridge import (
    best_tr_to_en,
    normalize_term_en,
    normalize_term_tr,
)

RECENT_MEMORY = []


def _score_asset(asset, target_label="", interest="", avoid_recent=True):
    score = 0

    target_tr = normalize_term_tr(target_label)
    target_en = normalize_term_en(best_tr_to_en(target_label, fallback=target_label)) if target_label else ""
    interest_tr = normalize_term_tr(interest)
    interest_en = normalize_term_en(best_tr_to_en(interest, fallback=interest)) if interest else ""

    label_tr = asset.get("label_tr", "").lower()
    label_en = asset.get("label_en", "").lower()
    tags_tr = [x.lower() for x in asset.get("tags_tr", [])]
    tags_en = [x.lower() for x in asset.get("tags_en", [])]
    interests_tr = [x.lower() for x in asset.get("interests_tr", [])]
    interests_en = [x.lower() for x in asset.get("interests_en", [])]
    asset_id = asset.get("asset_id", "")

    if target_tr and target_tr == label_tr:
        score += 45
    if target_en and target_en == label_en:
        score += 30

    if target_tr and target_tr in tags_tr:
        score += 20
    if target_en and target_en in tags_en:
        score += 12

    if interest_tr and interest_tr in interests_tr:
        score += 25
    if interest_en and interest_en in interests_en:
        score += 15

    if asset.get("preferred"):
        score += 10

    used = int(asset.get("used_count", 0))
    score += max(0, 15 - used)

    attention_boost = get_attention_score(asset_id)
    score += attention_boost

    label_boost = get_label_attention_boost(label_tr or label_en)
    score += label_boost

    if avoid_recent and asset_id in RECENT_MEMORY:
        score -= 100

    return score


def select_best_asset(
    target_label: str,
    interest: str = "",
    avoid_recent: bool = True
):
    assets = list_assets(status="active")

    if not assets:
        return None

    scored = []

    for asset in assets:
        score = _score_asset(
            asset,
            target_label=target_label,
            interest=interest,
            avoid_recent=avoid_recent
        )
        scored.append((score, asset))

    scored.sort(key=lambda x: x[0], reverse=True)

    top = [x[1] for x in scored[:5]]
    if not top:
        return None

    selected = random.choice(top)

    RECENT_MEMORY.append(selected["asset_id"])
    if len(RECENT_MEMORY) > 12:
        RECENT_MEMORY.pop(0)

    return selected
