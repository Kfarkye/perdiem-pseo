#!/usr/bin/env python3
"""
Pristine Vercel Config Seeder
Ensures identical SEO and routing rules across all 8 verticals.
"""
import json
from pathlib import Path

# Automatically targets the folder this script lives in (the repo root)
REPO_ROOT = Path(__file__).resolve().parent

VERTICALS = [
    "dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo",
    "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo"
]

# Bulletproof SEO Settings:
# - cleanUrls: Forces /state-name instead of /state-name.html
# - trailingSlash: Removes end slashes (prevents Google indexing duplicate content)
# - headers: Forces browsers/crawlers to parse sitemap & robots correctly
VERCEL_JSON = {
    "cleanUrls": True,
    "trailingSlash": False,
    "headers": [
        {
            "source": "/sitemap.xml",
            "headers": [{"key": "Content-Type", "value": "application/xml; charset=utf-8"}]
        },
        {
            "source": "/robots.txt",
            "headers": [{"key": "Content-Type", "value": "text/plain; charset=utf-8"}]
        }
    ]
}

def main():
    print("Standardizing Vercel configs across all verticals...")
    print("-" * 50)
    
    written, skipped, missing = 0, 0, 0

    for v in VERTICALS:
        v_dir = REPO_ROOT / v
        if not v_dir.exists():
            print(f"  [WARN] Missing directory, skipping: {v}/")
            missing += 1
            continue
            
        config_path = v_dir / "vercel.json"
        
        # Always overwrite to ensure absolute consistency across the monorepo
        config_path.write_text(json.dumps(VERCEL_JSON, indent=2) + "\n", encoding="utf-8")
        print(f"  [ OK ] Synced: {v}/vercel.json")
        written += 1

    print("-" * 50)
    print(f"✅ Synced: {written} | ⏭️ Skipped: {skipped} | ⚠️ Missing Folders: {missing}")

if __name__ == "__main__":
    main()
