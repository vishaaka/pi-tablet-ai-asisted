import json
import os
from pathlib import Path


SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}


def normalize_label(name: str) -> str:
    name = Path(name).stem.lower()
    name = name.replace("_", " ").replace("-", " ")
    return name.strip()


def build_index_from_folder(
    source_dir: str,
    output_path: str = "data/open_images_index.jsonl"
):
    source = Path(source_dir)
    output = Path(output_path)

    output.parent.mkdir(parents=True, exist_ok=True)

    count = 0

    with output.open("w", encoding="utf-8") as f:
        for file in source.rglob("*"):
            if file.suffix.lower() not in SUPPORTED:
                continue

            label = normalize_label(file.name)

            item = {
                "external_id": f"local_{count}",
                "label": label,
                "title": file.stem,
                "thumbnail_url": "",
                "image_url": str(file.resolve()).replace("\\", "/"),
                "source_url": str(file.resolve()).replace("\\", "/"),
                "tags": [label],
                "categories": ["local_dataset"],
                "license": "local",
            }

            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            count += 1

    return {
        "ok": True,
        "count": count,
        "output": str(output)
    }


if __name__ == "__main__":
    result = build_index_from_folder("assets")
    print(result)