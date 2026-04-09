from pathlib import Path
from asset_manager import create_asset_from_saved_path


SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}


def infer_tags_from_name(name: str):
    stem = Path(name).stem.lower()
    parts = (
        stem.replace("_", " ")
        .replace("-", " ")
        .split()
    )
    return list(dict.fromkeys(parts))


def bulk_import_assets(folder: str):
    folder_path = Path(folder)

    imported = []
    skipped = []

    for file in folder_path.rglob("*"):
        if file.suffix.lower() not in SUPPORTED:
            continue

        label = Path(file).stem.split("_")[0].lower()
        tags = infer_tags_from_name(file.name)

        try:
            item = create_asset_from_saved_path(
                image_path=str(file).replace("\\", "/"),
                label=label,
                tags=tags,
                source="bulk_import",
                source_url=str(file.resolve()).replace("\\", "/"),
            )
            imported.append(item["asset_id"])
        except Exception:
            skipped.append(str(file))

    return {
        "ok": True,
        "imported": len(imported),
        "skipped": len(skipped),
        "imported_ids": imported,
        "skipped_files": skipped[:30]
    }