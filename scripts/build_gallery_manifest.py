#!/usr/bin/env python3
"""Generate _data/gallery.json, ordered for display.

Each gallery image is tagged with the date of its most recent git commit.
The list is sorted by commit date (newest first), with filename A->Z breaking
ties. In practice that puts one-at-a-time uploads on top (newest first) and the
big bulk-import batches at the bottom in plain alphabetical order.

File modification times are deliberately NOT used: git does not preserve them,
so on a fresh CI checkout they are all identical and meaningless.
"""

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GALLERY_DIR = REPO_ROOT / "assets" / "gallery"
OUTPUT = REPO_ROOT / "_data" / "gallery.json"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
EPOCH = "1970-01-01T00:00:00+00:00"  # fallback for uncommitted files


def last_commit_date(path: Path) -> str:
    """ISO-8601 author date of the file's most recent commit, or EPOCH."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%aI", "--", str(path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() or EPOCH


def main() -> None:
    images = [
        p
        for p in sorted(GALLERY_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]

    items = [
        {
            "name": p.name,
            "path": "/" + p.relative_to(REPO_ROOT).as_posix(),
            "date": last_commit_date(p),
        }
        for p in images
    ]

    # Stable sort: name A->Z first, then commit date newest-first on top.
    items.sort(key=lambda x: x["name"])
    items.sort(key=lambda x: x["date"], reverse=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(items, indent=2) + "\n")
    print(f"Wrote {len(items)} images to {OUTPUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
