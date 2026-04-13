import json
import re
from typing import Any

from config.settings import data_dir, data_path

DICTIONARY_PATH = data_path("dictionary.json")
TRANSLATION_CACHE_PATH = data_path("translation_cache.json")


def _ensure_data_dir() -> None:
    data_dir()


def _normalize_text(value: str) -> str:
    value = (value or "").strip().lower()
    value = value.replace("I", "ı").replace("İ", "i")
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _tokenize(value: str) -> list[str]:
    value = _normalize_text(value)
    return [x for x in re.split(r"[,\s/;]+", value) if x]


def _load_json(path: str, fallback: Any) -> Any:
    if not path.exists():
        return fallback

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback


def _save_json(path: str, data: Any) -> None:
    _ensure_data_dir()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_cache() -> dict[str, Any]:
    return _load_json(TRANSLATION_CACHE_PATH, {})


def _save_cache(cache: dict[str, Any]) -> None:
    _save_json(TRANSLATION_CACHE_PATH, cache)


def _load_dictionary_raw() -> Any:
    return _load_json(DICTIONARY_PATH, [])


def _extract_pairs_from_item(item: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []

    if isinstance(item, dict):
        tr_candidates = []
        en_candidates = []

        for key in ("tr", "turkish", "turkce", "kelime_tr", "source_tr"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                tr_candidates.append(value)

        for key in ("en", "english", "ingilizce", "kelime_en", "source_en"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                en_candidates.append(value)

        if not tr_candidates and "word" in item and "meanings" in item:
            word = item.get("word")
            meanings = item.get("meanings")
            if isinstance(word, str) and isinstance(meanings, list):
                for m in meanings:
                    if isinstance(m, str) and m.strip():
                        pairs.append((_normalize_text(word), _normalize_text(m)))

        if tr_candidates and en_candidates:
            for tr in tr_candidates:
                for en in en_candidates:
                    pairs.append((_normalize_text(tr), _normalize_text(en)))

        if "translations" in item and isinstance(item["translations"], list):
            src = item.get("word") or item.get("source") or item.get("term") or ""
            if isinstance(src, str) and src.strip():
                for t in item["translations"]:
                    if isinstance(t, str) and t.strip():
                        pairs.append((_normalize_text(src), _normalize_text(t)))

    elif isinstance(item, list) and len(item) >= 2:
        left = item[0]
        right = item[1]
        if isinstance(left, str) and isinstance(right, str):
            pairs.append((_normalize_text(left), _normalize_text(right)))

    return pairs


def _build_indexes() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    raw = _load_dictionary_raw()

    tr_to_en: dict[str, list[str]] = {}
    en_to_tr: dict[str, list[str]] = {}

    items = raw if isinstance(raw, list) else []

    for item in items:
        for tr, en in _extract_pairs_from_item(item):
            if not tr or not en:
                continue

            tr_to_en.setdefault(tr, [])
            if en not in tr_to_en[tr]:
                tr_to_en[tr].append(en)

            en_to_tr.setdefault(en, [])
            if tr not in en_to_tr[en]:
                en_to_tr[en].append(tr)

    return tr_to_en, en_to_tr


def _score_candidate(source: str, candidate: str) -> int:
    source_n = _normalize_text(source)
    candidate_n = _normalize_text(candidate)

    if not candidate_n:
        return -999

    score = 0

    if source_n == candidate_n:
        score += 100

    source_tokens = _tokenize(source_n)
    candidate_tokens = _tokenize(candidate_n)

    overlap = len(set(source_tokens) & set(candidate_tokens))
    score += overlap * 10

    score -= len(candidate_tokens)
    score -= len(candidate_n) // 10

    return score


def _sort_candidates(source: str, candidates: list[str]) -> list[str]:
    unique = []
    seen = set()

    for c in candidates:
        c_n = _normalize_text(c)
        if not c_n or c_n in seen:
            continue
        unique.append(c_n)
        seen.add(c_n)

    unique.sort(key=lambda x: (-_score_candidate(source, x), len(x), x))
    return unique


def _lookup_with_partial(term: str, index: dict[str, list[str]]) -> list[str]:
    term_n = _normalize_text(term)
    if not term_n:
        return []

    if term_n in index:
        return _sort_candidates(term_n, index[term_n])

    term_tokens = _tokenize(term_n)
    found: list[str] = []

    for key, values in index.items():
        if key == term_n:
            found.extend(values)
            continue

        key_tokens = _tokenize(key)
        if term_n in key or key in term_n:
            found.extend(values)
            continue

        if term_tokens and key_tokens and set(term_tokens) & set(key_tokens):
            found.extend(values)

    return _sort_candidates(term_n, found)


def tr_to_en(term: str, limit: int = 5) -> list[str]:
    term_n = _normalize_text(term)
    if not term_n:
        return []

    cache = _load_cache()
    cache_key = f"tr_to_en::{term_n}"
    if cache_key in cache:
        return cache[cache_key][:limit]

    tr_index, _ = _build_indexes()
    result = _lookup_with_partial(term_n, tr_index)

    cache[cache_key] = result
    _save_cache(cache)

    return result[:limit]


def en_to_tr(term: str, limit: int = 5) -> list[str]:
    term_n = _normalize_text(term)
    if not term_n:
        return []

    cache = _load_cache()
    cache_key = f"en_to_tr::{term_n}"
    if cache_key in cache:
        return cache[cache_key][:limit]

    _, en_index = _build_indexes()
    result = _lookup_with_partial(term_n, en_index)

    cache[cache_key] = result
    _save_cache(cache)

    return result[:limit]


def best_tr_to_en(term: str, fallback: str = "") -> str:
    results = tr_to_en(term, limit=1)
    if results:
        return results[0]
    return _normalize_text(fallback or term)


def best_en_to_tr(term: str, fallback: str = "") -> str:
    results = en_to_tr(term, limit=1)
    if results:
        return results[0]
    return _normalize_text(fallback or term)


def normalize_term_tr(term: str) -> str:
    return _normalize_text(term)


def normalize_term_en(term: str) -> str:
    return _normalize_text(term)
