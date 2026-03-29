#!/usr/bin/env python3
"""Root deploy config hygiene guard.

Legacy behavior wrote per-vertical `*-pseo/vercel.json` files.
This is now intentionally blocked because production deploys from root config only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ROOT_VERCEL = REPO_ROOT / "vercel.json"


def main() -> None:
    print("Root deploy hygiene check")
    print("-" * 50)

    if not ROOT_VERCEL.exists():
        print("ERROR: Missing root vercel.json")
        sys.exit(1)

    try:
        root_config = json.loads(ROOT_VERCEL.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid root vercel.json ({exc})")
        sys.exit(1)

    output_dir = root_config.get("outputDirectory")
    if output_dir != "dist":
        print(f"ERROR: root vercel.json outputDirectory must be 'dist' (found {output_dir!r})")
        sys.exit(1)

    legacy_files = sorted(REPO_ROOT.glob("*-pseo/vercel.json"))
    if legacy_files:
        print("ERROR: Legacy per-vertical vercel.json files are not allowed:")
        for path in legacy_files:
            print(f" - {path.relative_to(REPO_ROOT)}")
        sys.exit(1)

    print("PASS: root vercel.json is canonical and no legacy per-vertical configs exist.")


if __name__ == "__main__":
    main()
