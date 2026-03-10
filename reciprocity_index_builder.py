from __future__ import annotations

from datetime import datetime


def render_index(*, domain: str, profile: dict, states_manifest: list[dict], css_hash: str, today: str) -> str:
    profession = profile['identity']['title_full']
    slug = profile['slug']
    plural = profile['identity'].get('title_plural', profession + 's')
    latest_verified = today
    cards = []
    for s in sorted(states_manifest, key=lambda item: item['name']):
        compact_badge = 'Compact' if s['state_is_member'] else 'Endorsement'
        cards.append(
            f'''      <a class="link-card" href="/{s['slug']}" data-state="{s['name'].lower()}" data-compact="{'member' if s['state_is_member'] else 'non-member'}" data-tier="{s['processing_tier']}">\n'''
            f'''        <div class="card-top"><h3>{s['name']}</h3><span class="badge {'badge-green' if s['state_is_member'] else 'badge-gray'}">{compact_badge}</span></div>\n'''
            f'''        <p>{s['compact_label']}</p>\n'''
            f'''        <div class="card-meta"><span>${s['endorsement_fee']}</span><span>{s['processing_time']}</span></div>\n'''
            f'''      </a>'''
        )
        latest_verified = max(latest_verified, s.get('last_updated') or today)
    cards_html = '\n'.join(cards)
    title = f"{profession} License Reciprocity by State - Compact Status, Fees and Transfer Timelines (2026)"
    desc = f"Compare {plural.lower()} license reciprocity rules by state, including compact membership, endorsement fees, temporary license availability, and processing times."
    popular = states_manifest[:4]
    popular_links = '\n'.join(f'<li><a href="/{s["slug"]}">{s["name"]}</a></li>' for s in popular)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{domain}/">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="/css/styles.css?v={css_hash}">
<style>
.reciprocity-hero {{ padding: 5rem 1.5rem 3rem; background: linear-gradient(180deg, #0f3d3e 0%, #123d2e 100%); color: #f7f3eb; text-align: center; }}
.reciprocity-hero h1 {{ color: #fff; margin-bottom: 1rem; }}
.reciprocity-hero p {{ max-width: 700px; margin: 0 auto; color: #d8e5df; }}
.reciprocity-toolbar {{ max-width: 1040px; margin: -1.75rem auto 2rem; padding: 1rem; background: #fff; border-radius: 18px; box-shadow: 0 18px 40px rgba(15,61,62,.08); border: 1px solid #e8e0d3; }}
.reciprocity-toolbar input {{ width: 100%; padding: .85rem 1rem; border-radius: 12px; border: 1px solid #d8d0c2; }}
.reciprocity-grid {{ max-width: 1040px; margin: 0 auto 3rem; display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 1rem; padding: 0 1rem; }}
.link-card {{ display: block; background: #fff; border: 1px solid #e8e0d3; border-radius: 18px; padding: 1rem; color: inherit; text-decoration: none; box-shadow: 0 10px 24px rgba(25,31,31,.04); }}
.card-top {{ display: flex; justify-content: space-between; gap: .75rem; align-items: start; }}
.card-top h3 {{ margin: 0; }}
.card-meta {{ margin-top: .75rem; display: flex; justify-content: space-between; color: #0f3d3e; font-size: .9rem; }}
.badge {{ display: inline-flex; padding: .25rem .55rem; border-radius: 999px; font-size: .72rem; text-transform: uppercase; letter-spacing: .04em; }}
.badge-green {{ background: #d8f4df; color: #14532d; }}
.badge-gray {{ background: #eceff1; color: #37474f; }}
.reciprocity-footer {{ max-width: 1040px; margin: 0 auto 3rem; padding: 0 1rem; }}
</style>
</head>
<body>
<nav class="site-nav" aria-label="Site navigation"><div class="site-nav-inner"><a href="/" class="site-nav-brand">State Licensing Reference</a></div></nav>
<header class="reciprocity-hero">
  <p class="eyebrow">License Transfer Tool</p>
  <h1>{profession} License Reciprocity by State</h1>
  <p>Compare compact participation, endorsement fees, fingerprint rules, temporary license availability, and transfer timelines before you apply.</p>
</header>
<main id="main-content">
  <section class="reciprocity-toolbar">
    <input id="stateSearch" type="search" placeholder="Search by state name" aria-label="Search states">
  </section>
  <section class="reciprocity-grid" id="reciprocityGrid">
{cards_html}
  </section>
  <section class="reciprocity-footer">
    <h2>Popular reciprocity pages</h2>
    <ul>{popular_links}</ul>
    <p>Last refreshed {latest_verified}.</p>
  </section>
</main>
<script>
const input = document.getElementById('stateSearch');
const cards = [...document.querySelectorAll('.link-card')];
input.addEventListener('input', () => {{
  const q = input.value.toLowerCase().trim();
  for (const card of cards) {{
    const match = card.dataset.state.includes(q);
    card.style.display = match ? '' : 'none';
  }}
}});
</script>
</body>
</html>'''
