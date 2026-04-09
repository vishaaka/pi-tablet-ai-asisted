import json
from asset_manager import _normalize_manifest_item

OLD_PATH = "asset_manifest.jsonl"
BACKUP_PATH = "asset_manifest.backup.jsonl"


def migrate_manifest():
    items = []

    with open(OLD_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                items.append(_normalize_manifest_item(raw))
            except Exception:
                continue

    with open(BACKUP_PATH, "w", encoding="utf-8") as f:
        with open(OLD_PATH, "r", encoding="utf-8") as old:
            f.write(old.read())

    with open(OLD_PATH, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return {
        "ok": True,
        "migrated_count": len(items),
        "backup_path": BACKUP_PATH,
    }


if __name__ == "__main__":
    print(migrate_manifest())