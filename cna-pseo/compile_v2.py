import json
import os
from pathlib import Path

jsonl_file = Path("temp_research.jsonl")
output_dir = Path("database/v2")
output_dir.mkdir(parents=True, exist_ok=True)

if not jsonl_file.exists():
    print("No temp_research.jsonl found.")
    exit(0)

count = 0
with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        state_data = json.loads(line)
        slug = state_data["routing"]["canonical_slug"]
        out_path = output_dir / f"{slug}.json"
        
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(state_data, out, indent=2)
        count += 1
        
print(f"Successfully compiled {count} state JSONs into {output_dir}/")
