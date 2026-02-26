# Dietitian pSEO — Enhanced Game Plan

> Last updated: 2026-02-25
> Status: Phase 1 complete, Phase 2 in progress

---

## Current State (What We Have)

| Layer | Asset | Count | Status |
|---|---|---|---|
| JSON data | `database/json/*.json` | 5 | ✅ CA, NM, TX, FL, DC |
| Hand-crafted HTML | `dist/*.html` (reference) | 3 | ✅ NM, DC, WA-fingerprint |
| Jinja template | `src/templates/state-hub.html` | 1 | ✅ Compiles all 5 JSON |
| Compiler | `build.py` | 1 | ✅ StrictUndefined passing |
| Agent config | `.cursorrules` + `.agents/workflows/build.md` | 2 | ✅ Dual-engine workflow |
| **CSS** | **Extracted stylesheet** | **0** | ❌ **MISSING** |

---

## Gap Analysis (What's Missing Before Scale-Out)

### GAP 1: No extracted CSS file

The template references `<link rel="stylesheet" href="/css/styles.css">` but this file doesn't exist.
The 3 hand-crafted reference pages each carry ~150 lines of inline `<style>`.
**Fix:** Extract the master CSS from the NM reference into `dist/css/styles.css`.

### GAP 2: No `index.html` hub page

All 5 compiled pages are orphans — no directory page links to them.
Googlebot has no way to discover the pages without crawling individual URLs.
**Fix:** Auto-generate `dist/index.html` as a state directory grid during build.

### GAP 3: No `sitemap.xml`

Without a sitemap, Googlebot relies entirely on internal links for discovery.
For a 50-state site, this means slower indexing and missed pages.
**Fix:** Auto-generate `dist/sitemap.xml` during build from the JSON manifest.

### GAP 4: No `vercel.json` deployment config

The project has no hosting configuration. Vercel needs `cleanUrls`, cache headers,
and the build command defined.
**Fix:** Write `vercel.json` with `cleanUrls: true`, immutable CSS caching, and the Python build command.

### GAP 5: No `robots.txt`

Standard SEO hygiene — Googlebot needs to find the sitemap.
**Fix:** Auto-generate `dist/robots.txt` during build.

### GAP 6: Template vs. hand-crafted content gap

The Jinja template produces ~10KB pages with structured data from JSON.
The hand-crafted reference pages are 41-68KB with rich editorial content (callouts,
source lists, fee tables, troubleshooting grids, FD-258 card guides).
**This gap is by design.** The template is the "Tier 1" baseline that scales to 50 states.
Hand-crafted "Tier 2" pages are the premium editorial layer added selectively.
**No fix needed** — but the workflow must document both tiers clearly.

### GAP 7: Hand-crafted pages will be OVERWRITTEN by build.py

`build.py` writes to `dist/new-mexico-dietitian.html` — overwriting the 41KB
hand-crafted reference page with a 10KB template-compiled version.
**Fix:** Build script must skip files that already exist as hand-crafted pages,
OR hand-crafted pages must live in a protected directory that build.py copies verbatim.

---

## Architecture (Enhanced)

```
dietitian-pseo/
├── .agents/workflows/
│   ├── build.md            # Dual-engine JSON generation workflow
│   └── audit.md            # Quality audit workflow
├── .cursorrules            # Agent system prompt & schema
├── build.py                # SSG compiler (Jinja2 + sitemap + index)
├── vercel.json             # Deployment config
├── requirements.txt        # Jinja2==3.1.3
│
├── database/
│   └── json/               # 📦 Structured data (one per state)
│       ├── california-dietitian.json
│       ├── dc-dietitian.json
│       ├── florida-dietitian.json
│       ├── new-mexico-dietitian.json
│       └── texas-dietitian.json
│
├── src/
│   ├── templates/
│   │   └── state-hub.html       # Jinja master template (Tier 1)
│   └── css/
│       └── styles.css           # Master extracted CSS (source of truth)
│
├── content/                     # 📝 Hand-crafted HTML bodies (Tier 2)
│   ├── new-mexico-dietitian.html
│   ├── dc-dietitian.html
│   └── washington-dietitian-fingerprint.html
│
└── dist/                        # 🚀 Build output (Vercel serves this)
    ├── index.html               # Auto-generated state directory
    ├── sitemap.xml              # Auto-generated sitemap
    ├── robots.txt               # Auto-generated robots
    ├── css/
    │   └── styles.css           # Copied from src/css/
    ├── california-dietitian.html
    ├── dc-dietitian.html        # Hand-crafted (Tier 2) — NOT overwritten
    ├── florida-dietitian.html
    ├── new-mexico-dietitian.html # Hand-crafted (Tier 2) — NOT overwritten
    ├── texas-dietitian.html
    └── washington-dietitian-fingerprint.html  # Hand-crafted sub-page
```

### Two-Tier Content Strategy

| Tier | Source | Size | Coverage | When |
|---|---|---|---|---|
| **Tier 1** (Template) | JSON → Jinja `state-hub.html` | ~10KB | All 50 states | Automated via build.py |
| **Tier 2** (Editorial) | Hand-crafted HTML in `content/` | 40-70KB | High-value states | Manual, copied verbatim to dist/ |

**Rule:** If a Tier 2 file exists in `content/`, build.py copies it to `dist/` instead
of compiling the Jinja template for that slug. This means Tier 2 always wins.

---

## Execution Phases

### Phase 1 ✅ COMPLETE — Foundation

- [x] Establish JSON schema (14 keys, StrictUndefined-validated)
- [x] Write 5 seed JSON files (CA, NM, TX, FL, DC)
- [x] Create 3 hand-crafted reference HTML pages (NM, DC, WA-fingerprint)
- [x] Map full CSS component registry (14 components)
- [x] Write `.cursorrules` and `.agents/workflows/build.md`
- [x] Write Jinja template and build.py compiler
- [x] Validate: 5/5 JSON compile cleanly

### Phase 2 🔧 IN PROGRESS — Infrastructure

- [x] Extract master CSS into `src/css/styles.css`
- [ ] Write `vercel.json` + `requirements.txt`
- [ ] Patch `build.py`: add sitemap.xml, index.html, robots.txt generation
- [ ] Patch `build.py`: add Tier 2 override logic (hand-crafted wins)
- [ ] Patch `build.py`: copy `src/css/styles.css` → `dist/css/styles.css`
- [ ] Move hand-crafted HTML from `dist/` to `content/` directory
- [ ] Run full build and verify all outputs
- [ ] Serve locally and visual-check all pages

### Phase 3 🔜 NEXT — Scale-Out (Batch 1: 8 high-population states)

- [ ] NY, PA, IL, OH, MI, GA, NC, NJ
- [ ] Use `/build` workflow: Gemini researches → User pastes → Agent writes JSON
- [ ] Run `python3 build.py` after each batch
- [ ] Verify sitemap grows, index updates

### Phase 4 — Scale-Out (Batch 2-5: Remaining 37 states)

- [ ] Batch 2: VA, MA, WA, AZ, TN, MO, MD, IN (8 states)
- [ ] Batch 3: WI, MN, CO, SC, AL, LA, KY, OR (8 states)
- [ ] Batch 4: OK, CT, UT, IA, NV, AR, MS, KS (8 states)
- [ ] Batch 5: NE, ID, WV, NM✓, HI, NH, ME, RI, MT, DE, SD, ND, AK, VT, WY, DC✓ (remaining)
- [ ] Sub-pages: Fingerprint guides for states that require CBC (like WA template)

### Phase 5 — Launch

- [ ] Configure domain: statelicensingreference.com
- [ ] `vercel deploy --prod`
- [ ] Submit sitemap to Google Search Console
- [ ] Verify Core Web Vitals (target: 100/100)
- [ ] Monitor indexing rate

---

## Scaling Guardrails

1. **Batch size:** 5-8 states per agent session (prevents context window overflow)
2. **YMYL compliance:** Every JSON must pass StrictUndefined — no guessed fees
3. **Source verification:** Florida JSON still needs Gemini verification
4. **No .gov scraping:** Agent generates Gemini prompts; USER runs them in Gemini
5. **Anti-bot safety:** Never hit the same .gov domain more than 3x in one session
6. **Hand-crafted protection:** Tier 2 pages in `content/` are NEVER overwritten by build

---

## Domain & URL Strategy

| URL Pattern | Source |
|---|---|
| `/` | `index.html` — State directory hub |
| `/california-dietitian` | Tier 1 compiled (cleanUrls strips .html) |
| `/new-mexico-dietitian` | Tier 2 hand-crafted (override) |
| `/dc-dietitian` | Tier 2 hand-crafted (override) |
| `/washington-dietitian-fingerprint` | Tier 2 sub-page (no JSON, standalone) |
| `/sitemap.xml` | Auto-generated |
| `/robots.txt` | Auto-generated |
| `/css/styles.css` | Immutable cache (max-age=31536000) |
