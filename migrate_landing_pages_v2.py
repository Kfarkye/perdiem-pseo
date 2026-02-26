"""
Landing Page v2 Migration — All 8 Verticals
============================================
Applies conversion-optimized landing page structure to every vertical's build.py:
  1. v2 inline CSS (filter toolbar card, rounded pills, gap grid)
  2. CSS cache-bust hash
  3. Hero copy upgrade (profession-specific, data freshness signal)
  4. Boundaries micro-block (scope clarity)
  5. Bottom CTA (scroll-through capture)
  6. Enhanced footer disclaimer

Usage: python3 migrate_landing_pages_v2.py [--dry-run]
"""
import re
import sys
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv
ROOT = Path(__file__).parent

# ── PROFESSION METADATA ─────────────────────────────────
VERTICALS = {
    "dietitian-pseo": {
        "slug_suffix": "dietitian",
        "title_short": "Dietitian",
        "title_full": "Dietitian & Nutritionist",
        "title_abbr": "RD/RDN",
        "hero_h1_line1": "Dietitian License",
        "hero_h1_line2": "State Directory",
        "hero_sub": "Stop decoding state board websites. Find your state\\'s 2026 dietitian licensing requirements, fees, board contacts, and step-by-step application roadmaps.",
        "meta_title": "Dietitian License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)",
        "meta_desc": "Complete 2026 guide to dietitian and nutritionist licensing requirements, fees, and board contacts for all 50 US states and DC.",
        "meta_kw": "dietitian license by state, dietitian license requirements, nutritionist license requirements, state dietitian board, dietitian license cost, how to become a dietitian",
        "og_title": "Dietitian License Requirements by State (2026)",
        "og_desc": "Compare dietitian licensing fees, board contacts, and application steps across all 50 states.",
        "footer_tagline": "Independent, YMYL-compliant licensing guides for dietitians and nutritionists across the United States.",
        "disclaimer_entity": "any state or federal dietetics licensing board",
        "boundaries_what_is": "We provide the operational intelligence—board-sourced, statute-aligned roadmaps—so you submit a clean application on the first try.",
        "boundaries_what_isnt": "We don\\'t file your application for you.",
    },
    "ot-pseo": {
        "slug_suffix": "ot",
        "title_short": "OT",
        "title_full": "Occupational Therapist",
        "title_abbr": "OT/OTR",
        "hero_h1_line1": "OT License",
        "hero_h1_line2": "State Directory",
        "hero_sub": "Stop decoding state board websites. Find your state\\'s 2026 OT/OTR licensing requirements, fees, board contacts, and step-by-step application roadmaps.",
        "meta_title": "OT License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)",
        "meta_desc": "Complete 2026 guide to occupational therapist (OT/OTR) licensing requirements, fees, and board contacts for all 50 US states and DC.",
        "meta_kw": "OT license by state, occupational therapy license requirements, OTR license requirements, state occupational therapy board, OT license cost, occupational therapist licensure",
        "og_title": "Occupational Therapist License Requirements by State (2026)",
        "og_desc": "Compare OT licensing fees, board contacts, and application steps across all 50 states.",
        "footer_tagline": "Independent, YMYL-compliant licensing guides for occupational therapists (OT/OTR) across the United States.",
        "disclaimer_entity": "the NBCOT, ACOTE, or any state or federal licensing board",
        "boundaries_what_is": "We provide the operational intelligence—board-sourced, statute-aligned roadmaps—so you submit a clean application on the first try.",
        "boundaries_what_isnt": "We don\\'t file your application for you.",
    },
    "pt-pseo": {
        "slug_suffix": "pt",
        "title_short": "Physical Therapist",
        "title_full": "Physical Therapist",
        "title_abbr": "PT/DPT",
        "hero_h1_line1": "PT License",
        "hero_h1_line2": "State Directory",
        "hero_sub": "Stop decoding state board websites. Find your state\\'s 2026 physical therapy licensing requirements, fees, board contacts, and step-by-step application roadmaps.",
        "meta_title": "Physical Therapist License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)",
        "meta_desc": "Complete 2026 guide to physical therapist (PT) licensing requirements, fees, and board contacts for all 50 US states and DC.",
        "meta_kw": "PT license by state, physical therapy license requirements, physical therapist licensure, state PT board, PT license cost, how to become a physical therapist",
        "og_title": "Physical Therapist License Requirements by State (2026)",
        "og_desc": "Compare PT licensing fees, board contacts, and application steps across all 50 states.",
        "footer_tagline": "Independent, YMYL-compliant licensing guides for physical therapists across the United States.",
        "disclaimer_entity": "the FSBPT, CAPTE, or any state or federal licensing board",
        "boundaries_what_is": "We provide the operational intelligence—board-sourced, statute-aligned roadmaps—so you submit a clean application on the first try.",
        "boundaries_what_isnt": "We don\\'t file your application for you.",
    },
    "rrt-pseo": {
        "slug_suffix": "rrt",
        "title_short": "Respiratory Therapist",
        "title_full": "Respiratory Therapist",
        "title_abbr": "RRT/CRT",
        "hero_h1_line1": "RRT License",
        "hero_h1_line2": "State Directory",
        "hero_sub": "Stop decoding state board websites. Find your state\\'s 2026 respiratory therapy licensing requirements, fees, board contacts, and step-by-step application roadmaps.",
        "meta_title": "Respiratory Therapist License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)",
        "meta_desc": "Complete 2026 guide to respiratory therapist (RRT) licensing requirements, fees, and board contacts for all 50 US states and DC.",
        "meta_kw": "RRT license by state, respiratory therapy license requirements, respiratory therapist licensure, state RT board, RRT license cost, how to become a respiratory therapist",
        "og_title": "Respiratory Therapist License Requirements by State (2026)",
        "og_desc": "Compare respiratory therapist licensing fees, board contacts, and application steps across all 50 states.",
        "footer_tagline": "Independent, YMYL-compliant licensing guides for respiratory therapists across the United States.",
        "disclaimer_entity": "the NBRC, CoARC, or any state or federal licensing board",
        "boundaries_what_is": "We provide the operational intelligence—board-sourced, statute-aligned roadmaps—so you submit a clean application on the first try.",
        "boundaries_what_isnt": "We don\\'t file your application for you.",
    },
    "slp-pseo": {
        "slug_suffix": "slp",
        "title_short": "SLP",
        "title_full": "Speech-Language Pathologist",
        "title_abbr": "SLP/CCC-SLP",
        "hero_h1_line1": "SLP License",
        "hero_h1_line2": "State Directory",
        "hero_sub": "Stop decoding state board websites. Find your state\\'s 2026 SLP licensing requirements, telepractice rules, board contacts, and step-by-step application roadmaps.",
        "meta_title": "SLP License Requirements by State &mdash; Fees, Telepractice Rules &amp; How to Apply (2026)",
        "meta_desc": "Complete 2026 guide to speech-language pathologist (SLP) licensing requirements, telepractice rules, fees, and board contacts for all 50 US states and DC.",
        "meta_kw": "SLP license by state, speech-language pathology license requirements, SLP telepractice rules, state SLP board, SLP license cost, how to become an SLP",
        "og_title": "SLP License Requirements by State (2026)",
        "og_desc": "Compare SLP licensing fees, telepractice rules, and application steps across all 50 states.",
        "footer_tagline": "Independent, YMYL-compliant licensing guides for speech-language pathologists across the United States.",
        "disclaimer_entity": "ASHA, CAA, or any state or federal licensing board",
        "boundaries_what_is": "We provide the operational intelligence—board-sourced, statute-aligned roadmaps—so you submit a clean application on the first try.",
        "boundaries_what_isnt": "We don\\'t file your application for you.",
    },
    "aud-pseo": {
        "slug_suffix": "aud",
        "title_short": "Audiologist",
        "title_full": "Audiologist",
        "title_abbr": "AuD",
        "hero_h1_line1": "Audiologist License",
        "hero_h1_line2": "State Directory",
        "hero_sub": "Stop decoding state board websites. Find your state\\'s 2026 audiology licensing requirements, fees, board contacts, and step-by-step application roadmaps.",
        "meta_title": "Audiologist License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)",
        "meta_desc": "Complete 2026 guide to audiologist (AuD) licensing requirements, fees, and board contacts for all 50 US states and DC.",
        "meta_kw": "audiologist license by state, audiology license requirements, AuD licensure, state audiology board, audiologist license cost, how to become an audiologist",
        "og_title": "Audiologist License Requirements by State (2026)",
        "og_desc": "Compare audiologist licensing fees, board contacts, and application steps across all 50 states.",
        "footer_tagline": "Independent, YMYL-compliant licensing guides for audiologists across the United States.",
        "disclaimer_entity": "ASHA, AAA, or any state or federal licensing board",
        "boundaries_what_is": "We provide the operational intelligence—board-sourced, statute-aligned roadmaps—so you submit a clean application on the first try.",
        "boundaries_what_isnt": "We don\\'t file your application for you.",
    },
    "pharm-pseo": {
        "slug_suffix": "pharm",
        "title_short": "Pharmacy Technician",
        "title_full": "Pharmacy Technician",
        "title_abbr": "CPhT",
        "hero_h1_line1": "Pharmacy Tech License",
        "hero_h1_line2": "State Directory",
        "hero_sub": "Stop decoding state board websites. Find your state\\'s 2026 pharmacy technician licensing requirements, fees, board contacts, and step-by-step application roadmaps.",
        "meta_title": "Pharmacy Technician License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)",
        "meta_desc": "Complete 2026 guide to pharmacy technician licensing requirements, fees, and board contacts for all 50 US states and DC.",
        "meta_kw": "pharmacy technician license by state, pharmacy tech license requirements, CPhT licensure, state board of pharmacy, pharmacy tech license cost",
        "og_title": "Pharmacy Technician License Requirements by State (2026)",
        "og_desc": "Compare pharmacy technician licensing fees, board contacts, and application steps across all 50 states.",
        "footer_tagline": "Independent, YMYL-compliant licensing guides for pharmacy technicians across the United States.",
        "disclaimer_entity": "the PTCB, any state board of pharmacy, or any federal agency",
        "boundaries_what_is": "We provide the operational intelligence—board-sourced, statute-aligned roadmaps—so you submit a clean application on the first try.",
        "boundaries_what_isnt": "We don\\'t file your application for you.",
    },
    "pharmacist-pseo": {
        "slug_suffix": "pharmacist",
        "title_short": "Pharmacist",
        "title_full": "Pharmacist",
        "title_abbr": "RPh/PharmD",
        "hero_h1_line1": "Pharmacist License",
        "hero_h1_line2": "State Directory",
        "hero_sub": "Stop decoding state board websites. Find your state\\'s 2026 pharmacist licensing requirements, fees, board contacts, and step-by-step application roadmaps.",
        "meta_title": "Pharmacist License Requirements by State &mdash; Fees, Board Contacts &amp; How to Apply (2026)",
        "meta_desc": "Complete 2026 guide to pharmacist (RPh) licensing requirements, fees, and board contacts for all 50 US states and DC.",
        "meta_kw": "pharmacist license by state, pharmacist license requirements, RPh licensure, state board of pharmacy, pharmacist license cost, NAPLEX requirements",
        "og_title": "Pharmacist License Requirements by State (2026)",
        "og_desc": "Compare pharmacist licensing fees, board contacts, and application steps across all 50 states.",
        "footer_tagline": "Independent, YMYL-compliant licensing guides for pharmacists across the United States.",
        "disclaimer_entity": "the NABP, ACPE, any state board of pharmacy, or any federal agency",
        "boundaries_what_is": "We provide the operational intelligence—board-sourced, statute-aligned roadmaps—so you submit a clean application on the first try.",
        "boundaries_what_isnt": "We don\\'t file your application for you.",
    },
}


def get_v2_index_template(v):
    """Generate the v2 index page f-string block for a given vertical."""
    s = v["slug_suffix"]
    return f'''index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{v["meta_title"]}</title>
<meta name="description" content="{v["meta_desc"]}">
<meta name="keywords" content="{v["meta_kw"]}">
<link rel="canonical" href="{{DOMAIN}}/">
<meta property="og:title" content="{v["og_title"]}">
<meta property="og:description" content="{v["og_desc"]}">
<meta property="og:type" content="website">
<meta property="og:url" content="{{DOMAIN}}/">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="State Licensing Reference">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="/css/styles.css?v={{CSS_HASH}}">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400&display=swap" rel="stylesheet">
<style>
.hub-header {{{{ background: var(--sand-900); color: var(--sand-100); padding: var(--space-9) var(--space-7) var(--space-10); text-align: center; position: relative; overflow: hidden; }}}}
.hub-header::before {{{{ content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 20% 80%, hsla(180,50%,26%,.07) 0%, transparent 70%), radial-gradient(ellipse 60% 50% at 80% 20%, hsla(18,52%,47%,.05) 0%, transparent 70%); pointer-events: none; }}}}
.hub-header h1 {{{{ color: #fff; font-family: var(--serif); font-size: clamp(1.85rem, 4.5vw, 2.65rem); margin-bottom: var(--space-4); font-weight: 400; letter-spacing: -.025em; position: relative; }}}}
.hub-header em {{{{ color: var(--terracotta-light); font-style: italic; font-weight: 300; }}}}
.hub-header p {{{{ color: var(--sand-400); font-size: 0.88rem; max-width: 520px; margin: 0 auto; line-height: 1.6; position: relative; }}}}
.hub-header .overline {{{{ font-family: var(--sans); font-size: .58rem; font-weight: 600; letter-spacing: .18em; text-transform: uppercase; color: var(--sand-400); margin-bottom: var(--space-3); display: block; position: relative; }}}}
.hub-header .freshness {{{{ font-family: var(--sans); font-size: .68rem; color: var(--sand-400); margin-top: var(--space-5); display: flex; align-items: center; justify-content: center; gap: var(--space-3); flex-wrap: wrap; position: relative; }}}}
.hub-header .freshness span {{{{ display: inline-flex; align-items: center; gap: .3rem; }}}}

/* ── Filter Toolbar — contained card ── */
.filter-toolbar {{{{ max-width: 1000px; margin: -2.5rem auto var(--space-6); padding: var(--space-5) var(--space-6); position: relative; z-index: 2; background: #fff; border: var(--border-subtle); border-radius: var(--radius-lg); box-shadow: var(--shadow-md); }}}}
.filter-search {{{{ width: 100%; padding: .8rem 1rem .8rem 2.6rem; border: var(--border-default); border-radius: var(--radius-md); background: var(--sand-50); font-family: var(--sans); font-size: .86rem; color: var(--sand-900); outline: none; box-shadow: var(--shadow-xs); transition: border-color 120ms cubic-bezier(.2,0,0,1), box-shadow 180ms cubic-bezier(.2,0,0,1); }}}}
.filter-search:focus {{{{ border-color: var(--teal); box-shadow: 0 0 0 3px hsla(180,50%,26%,.1), var(--shadow-xs); }}}}
.filter-search-wrap {{{{ position: relative; }}}}
.filter-search-wrap svg {{{{ position: absolute; left: .85rem; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: var(--sand-400); pointer-events: none; }}}}
.filter-row {{{{ display: flex; align-items: center; gap: .75rem; margin-top: var(--space-3); }}}}
.filter-label {{{{ font-family: var(--sans); font-size: .62rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--sand-400); min-width: 56px; flex-shrink: 0; }}}}
.filter-pills {{{{ display: flex; flex-wrap: wrap; gap: var(--space-2); }}}}
.filter-pill {{{{ font-family: var(--sans); font-size: .7rem; font-weight: 500; letter-spacing: .04em; text-transform: uppercase; padding: .35rem .8rem; border: var(--border-default); border-radius: var(--radius-full); background: var(--sand-50); color: var(--sand-500); cursor: pointer; user-select: none; transition: border-color 120ms cubic-bezier(.2,0,0,1), color 120ms cubic-bezier(.2,0,0,1), background 120ms cubic-bezier(.2,0,0,1); }}}}
.filter-pill:hover {{{{ border-color: var(--teal); color: var(--teal); }}}}
.filter-pill.active {{{{ background: var(--teal); border-color: var(--teal); color: #fff; }}}}
.filter-count {{{{ font-family: var(--sans); font-size: .68rem; color: var(--sand-400); margin-top: var(--space-2); text-align: right; }}}}
.filter-empty {{{{ display: none; text-align: center; padding: var(--space-8) var(--space-4); color: var(--sand-400); font-family: var(--sans); font-size: .88rem; max-width: 1000px; margin: 0 auto; }}}}
.filter-empty.visible {{{{ display: block; }}}}

/* ── Boundaries micro-block ── */
.scope-block {{{{ max-width: 1000px; margin: 0 auto var(--space-6); padding: 0 var(--space-4); display: flex; gap: var(--space-6); justify-content: center; flex-wrap: wrap; }}}}
.scope-item {{{{ font-family: var(--sans); font-size: .78rem; color: var(--sand-500); display: flex; align-items: baseline; gap: .4rem; }}}}
.scope-item .scope-icon {{{{ font-size: .85rem; flex-shrink: 0; }}}}
.scope-item strong {{{{ color: var(--sand-700); font-weight: 600; }}}}

/* ── State Grid ── */
.hub-grid {{{{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-3); max-width: 1000px; margin: 0 auto var(--space-9); padding: 0 var(--space-4); position: relative; }}}}
.hub-grid .link-card {{{{ background: #fff; border: var(--border-subtle); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-5); box-shadow: var(--shadow-xs); min-height: 56px; display: flex; flex-direction: column; justify-content: center; will-change: transform; transition: transform 120ms cubic-bezier(.2,0,0,1), box-shadow 180ms cubic-bezier(.2,0,0,1), border-color 120ms cubic-bezier(.2,0,0,1); }}}}
.hub-grid .link-card:hover {{{{ transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: hsla(180,50%,26%,.15); }}}}
.hub-grid .link-card h3 {{{{ font-family: var(--serif); font-size: 1.02rem; font-weight: 500; color: var(--sand-900); margin: 0; transition: margin 180ms cubic-bezier(.2,0,0,1); }}}}
.hub-grid .link-card:hover h3 {{{{ margin-bottom: .3rem; }}}}
.hub-grid .link-card .link-card-reveal {{{{ max-height: 0; opacity: 0; overflow: hidden; transition: max-height 280ms cubic-bezier(.2,0,0,1), opacity 180ms cubic-bezier(.2,0,0,1); }}}}
.hub-grid .link-card:hover .link-card-reveal {{{{ max-height: 60px; opacity: 1; }}}}
.hub-grid .link-card .link-card-desc {{{{ font-size: 0.73rem; color: var(--sand-500); margin-bottom: .15rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}}}
.hub-grid .link-card .link-card-meta {{{{ font-size: 0.68rem; color: var(--teal); font-weight: 500; display: block; }}}}
.hub-grid .link-card[data-hidden="true"] {{{{ display: none; }}}}

/* ── Bottom CTA ── */
.bottom-cta {{{{ background: var(--sand-900); padding: var(--space-9) var(--space-7); text-align: center; position: relative; overflow: hidden; }}}}
.bottom-cta::before {{{{ content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 60% 50% at 50% 100%, hsla(180,50%,26%,.06) 0%, transparent 70%); pointer-events: none; }}}}
.bottom-cta h2 {{{{ color: #fff; font-family: var(--serif); font-size: clamp(1.35rem, 3vw, 1.8rem); font-weight: 400; letter-spacing: -.02em; margin-bottom: var(--space-3); position: relative; }}}}
.bottom-cta p {{{{ color: var(--sand-400); font-size: .84rem; max-width: 480px; margin: 0 auto var(--space-5); line-height: 1.55; position: relative; }}}}
.bottom-cta .cta-select-wrap {{{{ max-width: 420px; margin: 0 auto; display: flex; gap: var(--space-2); position: relative; }}}}
.bottom-cta select {{{{ flex: 1; padding: .75rem 1rem; border: 1px solid hsla(0,0%,100%,.12); border-radius: var(--radius-md); background: hsla(0,0%,100%,.06); color: var(--sand-200); font-family: var(--sans); font-size: .84rem; outline: none; appearance: none; cursor: pointer; transition: border-color 120ms cubic-bezier(.2,0,0,1); }}}}
.bottom-cta select:focus {{{{ border-color: var(--teal); }}}}
.bottom-cta .cta-go {{{{ padding: .75rem 1.5rem; background: var(--teal); color: #fff; border: none; border-radius: var(--radius-md); font-family: var(--sans); font-size: .82rem; font-weight: 500; cursor: pointer; transition: background 120ms cubic-bezier(.2,0,0,1), transform 120ms cubic-bezier(.2,0,0,1); }}}}
.bottom-cta .cta-go:hover {{{{ background: var(--teal-hover); transform: translateY(-1px); }}}}
</style>
</head>
<body>

<a href="#main-content" class="skip-link">Skip to main content</a>

<nav class="site-nav" aria-label="Site navigation">
  <div class="site-nav-inner">
    <a href="/" class="site-nav-brand">State Licensing Reference</a>
    <ul class="site-nav-links">
      <li><a href="/" class="active">All States</a></li>
    </ul>
  </div>
</nav>

<header class="hub-header">
  <span class="overline">Board-Sourced Licensing Intelligence</span>
  <h1>{v["hero_h1_line1"]}<br><em>{v["hero_h1_line2"]}</em></h1>
  <p>{v["hero_sub"]}</p>
  <div class="freshness">
    <span>&#128197; Updated weekly</span>
    <span>&middot;</span>
    <span>Last verified: <strong>February 2026</strong></span>
    <span>&middot;</span>
    <span>&#127963; Board sources cited per state</span>
  </div>
</header>
<main id="main-content">
  <div class="filter-toolbar">
    <div class="filter-search-wrap">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" /></svg>
      <input type="text" class="filter-search" id="stateSearch" placeholder="Search by state name\\u2026" autocomplete="off" />
    </div>
    <div class="filter-row">
      <span class="filter-label">Timeline</span>
      <div class="filter-pills" data-group="time">
        <button class="filter-pill" data-filter="fastest">\\u22642 Weeks</button>
        <button class="filter-pill" data-filter="2-4wk">2\\u20134 Weeks</button>
        <button class="filter-pill" data-filter="4-6wk">4\\u20136 Weeks</button>
        <button class="filter-pill" data-filter="6-plus">6+ Weeks</button>
      </div>
    </div>
    <div class="filter-row">
      <span class="filter-label">Fee</span>
      <div class="filter-pills" data-group="fee">
        <button class="filter-pill" data-filter="no-fee">No Fee</button>
        <button class="filter-pill" data-filter="under-100">Under $100</button>
        <button class="filter-pill" data-filter="100-200">$100\\u2013$200</button>
        <button class="filter-pill" data-filter="over-200">Over $200</button>
      </div>
    </div>
    <div class="filter-count" id="filterCount"></div>
  </div>

  <div class="scope-block">
    <div class="scope-item"><span class="scope-icon">\\u2705</span> <strong>What this is:</strong> {v["boundaries_what_is"]}</div>
    <div class="scope-item"><span class="scope-icon">\\U0001f6ab</span> <strong>Not a filing service.</strong> {v["boundaries_what_isnt"]}</div>
  </div>

  <div class="hub-grid" id="hubGrid">
{{cards_html}}
  </div>
  <div class="filter-empty" id="filterEmpty">No states match your search. Try a different name or clear the filter.</div>
</main>

<section class="bottom-cta" aria-label="Get started">
  <h2>Don\\u2019t let bad paperwork delay your first paycheck.</h2>
  <p>Select your target state to see board-sourced requirements, exact fees, and a step-by-step application roadmap.</p>
  <div class="cta-select-wrap">
    <select id="bottomStateSelect" aria-label="Select a state">
      <option value="">Select target state\\u2026</option>
    </select>
    <button class="cta-go" id="bottomCtaGo">Continue \\u2794</button>
  </div>
</section>

<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div>
        <div class="footer-brand">State Licensing Reference</div>
        <p class="footer-tagline">{v["footer_tagline"]}</p>
      </div>
      <div>
        <div class="footer-col-title">Popular States</div>
        <ul class="footer-links">
          <li><a href="/california-{s}">California</a></li>
          <li><a href="/texas-{s}">Texas</a></li>
          <li><a href="/florida-{s}">Florida</a></li>
          <li><a href="/new-york-{s}">New York</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-col-title">More States</div>
        <ul class="footer-links">
          <li><a href="/illinois-{s}">Illinois</a></li>
          <li><a href="/ohio-{s}">Ohio</a></li>
          <li><a href="/georgia-{s}">Georgia</a></li>
          <li><a href="/pennsylvania-{s}">Pennsylvania</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="footer-disclaimer"><strong>Disclaimer:</strong> State Licensing Reference is an independent software tool and workflow resource. We are not a law firm, and we are not affiliated with {v["disclaimer_entity"]}. While our roadmaps are board-sourced and statute-aligned, state laws change frequently. Users must always verify final regulatory requirements directly with their specific state board prior to submitting applications or fees.</p>
      <p class="footer-copyright">&copy; 2026 State Licensing Reference</p>
    </div>
  </div>
</footer>
<script>
(function(){{{{
  const search = document.getElementById('stateSearch');
  const cards = document.querySelectorAll('.hub-grid .link-card');
  const empty = document.getElementById('filterEmpty');
  const countEl = document.getElementById('filterCount');
  let activeTime = 'all';
  let activeFee = 'all';

  function applyFilters() {{{{
    const q = search.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(c => {{{{
      const name = c.getAttribute('data-state') || '';
      const tb = c.getAttribute('data-time-bucket') || '';
      const fb = c.getAttribute('data-fee-bucket') || '';
      const matchName = !q || name.includes(q);
      const matchTime = activeTime === 'all' || tb === activeTime;
      const matchFee  = activeFee  === 'all' || fb === activeFee;
      const show = matchName && matchTime && matchFee;
      c.setAttribute('data-hidden', show ? 'false' : 'true');
      if (show) visible++;
    }}}});
    empty.classList.toggle('visible', visible === 0);
    if (activeTime !== 'all' || activeFee !== 'all' || q) {{{{
      countEl.textContent = visible + ' state' + (visible !== 1 ? 's' : '') + ' matched';
    }}}} else {{{{
      countEl.textContent = '';
    }}}}
  }}}}

  search.addEventListener('input', applyFilters);

  document.querySelectorAll('.filter-pills').forEach(group => {{{{
    const groupName = group.getAttribute('data-group');
    group.querySelectorAll('.filter-pill').forEach(pill => {{{{
      pill.addEventListener('click', function() {{{{
        const wasActive = this.classList.contains('active');
        group.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        if (wasActive) {{{{
          if (groupName === 'time') activeTime = 'all';
          else activeFee = 'all';
        }}}} else {{{{
          this.classList.add('active');
          const val = this.getAttribute('data-filter');
          if (groupName === 'time') activeTime = val;
          else activeFee = val;
        }}}}
        applyFilters();
      }}}});
    }}}});
  }}}});

  /* Bottom CTA — populate select from state cards */
  const bottomSelect = document.getElementById('bottomStateSelect');
  const bottomGo = document.getElementById('bottomCtaGo');
  cards.forEach(c => {{{{
    const opt = document.createElement('option');
    opt.value = c.href;
    opt.textContent = c.querySelector('h3').textContent;
    bottomSelect.appendChild(opt);
  }}}});
  bottomGo.addEventListener('click', function() {{{{
    if (bottomSelect.value) window.location.href = bottomSelect.value;
  }}}});
  bottomSelect.addEventListener('change', function() {{{{
    if (this.value) window.location.href = this.value;
  }}}});
}}}})();
</script>
</body>
</html>"""'''


def patch_build_py(vertical_dir, vdata):
    """Patch a vertical's build.py with v2 landing page."""
    build_py = vertical_dir / "build.py"
    if not build_py.exists():
        print(f"  SKIP: {build_py} not found")
        return False

    content = build_py.read_text()

    # 1. Add CSS_HASH if not present
    if "CSS_HASH" not in content:
        # Insert after TODAY = ... line
        content = content.replace(
            'TODAY = datetime.now().strftime("%Y-%m-%d")\n',
            'TODAY = datetime.now().strftime("%Y-%m-%d")\n\n'
            '# CSS cache-bust hash\n'
            'import hashlib as _hashlib\n'
            'CSS_HASH = _hashlib.md5(CSS_SRC.read_bytes()).hexdigest()[:8] if CSS_SRC.exists() else "0"\n'
        )

    # 2. Replace index_html block
    # Find the start: `index_html = f"""`
    start_marker = 'index_html = f"""'
    end_marker = '"""'

    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"  SKIP: {build_py} — no index_html f-string found")
        return False

    # Find the closing """ after the opening one
    search_from = start_idx + len(start_marker)
    end_idx = content.find(end_marker, search_from)
    if end_idx == -1:
        print(f"  SKIP: {build_py} — no closing triple-quote found")
        return False
    end_idx += len(end_marker)

    # Replace
    new_template = get_v2_index_template(vdata)
    content = content[:start_idx] + new_template + content[end_idx:]

    if DRY_RUN:
        print(f"  DRY-RUN: Would patch {build_py} ({len(content):,} bytes)")
    else:
        build_py.write_text(content)
        print(f"  ✅ PATCHED: {build_py} ({len(content):,} bytes)")

    return True


def main():
    print("\n=== LANDING PAGE v2 MIGRATION ===")
    print(f"Mode: {'DRY-RUN' if DRY_RUN else 'LIVE'}\n")

    patched = 0
    for dirname, vdata in VERTICALS.items():
        vertical_dir = ROOT / dirname
        if not vertical_dir.exists():
            print(f"  SKIP: {vertical_dir} does not exist")
            continue
        print(f"Processing {dirname}...")
        if patch_build_py(vertical_dir, vdata):
            patched += 1

    print(f"\n{'Would patch' if DRY_RUN else 'Patched'}: {patched}/{len(VERTICALS)} verticals")
    if not DRY_RUN:
        print("\nNext: run `python3 build.py` in each vertical to regenerate dist/")


if __name__ == "__main__":
    main()
