import os
import re
from pathlib import Path

dist_dir = Path("dist-v2")
index_html = dist_dir / "index.html"

content = index_html.read_text(encoding="utf-8")
hrefs = re.findall(r'<a.*?href="(.*?)".*?>', content)

broken = []
for href in hrefs:
    slug = href.strip("/")
    if not slug:
        continue # this might be the root hub link if any
        
    target = dist_dir / f"{slug}.html"
    if not target.exists():
        broken.append(href)

report = Path("link_audit.txt")
if broken:
    report.write_text("Broken Links:\n" + "\n".join(broken))
    print(f"FAILED: Found {len(broken)} broken links.")
    exit(1)
else:
    report.write_text("All internal links resolved successfully.")
    print("SUCCESS: All links resolve.")
