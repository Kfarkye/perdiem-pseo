#!/usr/bin/env python3
"""Live trust-regression guard for statelicensingreference.com.

Checks:
1) Critical smoke URLs return expected status/content type.
2) Canonical + og:url fixes stay correct on known high-risk pages.
3) PT pages do not reintroduce banned contradiction phrases.
4) Sampled state pages keep HTML/API contracts aligned.
5) Legacy API aliases continue resolving to canonical /api/{slug}.json.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

import requests

DEFAULT_BASE_URL = "https://www.statelicensingreference.com"
DEFAULT_REQUIRED_PATHS = [
    "/dc-dietitian",
    "/new-mexico-dietitian",
    "/api/california-pt.json",
    "/api/california-cna.json",
    "/api/california-da.json",
]
DEFAULT_CANONICAL_PATHS = [
    "/dc-dietitian",
    "/new-mexico-dietitian",
]
DEFAULT_ALIAS_PATHS = [
    "/api/v1/california-cna.json",
    "/pt-pseo/api/california-pt.json",
    "/cna-pseo/api/california-cna.json",
]
BANNED_PT_PHRASES = [
    "varies, often around $100 to $200",
    "processing generally takes 4 to 6 weeks",
    "timelines vary, but many applications are reviewed in around 4 to 6 weeks",
]
STATE_SLUG_PATTERN = re.compile(
    r"/[a-z0-9-]+-(dietitian|ot|pt|rrt|slp|aud|pharm|pharmacist|cna|da)$"
)


def normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def load_sitemap_urls(session: requests.Session, base_url: str, timeout: float) -> list[str]:
    sitemap_url = f"{base_url}/sitemap.xml"
    response = session.get(sitemap_url, timeout=timeout)
    response.raise_for_status()
    return re.findall(r"<loc>([^<]+)</loc>", response.text)


def extract_canonical(html: str) -> str | None:
    match = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    return match.group(1).rstrip("/") if match else None


def extract_og_url(html: str) -> str | None:
    match = re.search(r'<meta property="og:url" content="([^"]+)"', html)
    return match.group(1).rstrip("/") if match else None


def json_content_type(headers: dict[str, str]) -> bool:
    value = headers.get("Content-Type", "")
    return "application/json" in value.lower()


def html_content_type(headers: dict[str, str]) -> bool:
    value = headers.get("Content-Type", "")
    return "text/html" in value.lower()


def run_guard(
    *,
    base_url: str,
    timeout: float,
    sample_size: int,
    seed: int,
    check_aliases: bool,
) -> dict[str, Any]:
    session = requests.Session()
    session.headers["User-Agent"] = "SLR-Trust-Guard/1.0"

    failures: list[str] = []
    warnings: list[str] = []

    # 1) Critical smoke checks.
    smoke_passed = 0
    for path in DEFAULT_REQUIRED_PATHS:
        url = f"{base_url}{path}"
        try:
            response = session.get(url, timeout=timeout)
        except requests.RequestException as exc:
            failures.append(f"Smoke fetch failed: {url} ({exc})")
            continue

        if response.status_code != 200:
            failures.append(f"Smoke status mismatch: {url} -> {response.status_code}")
            continue

        if path.startswith("/api/"):
            if not json_content_type(dict(response.headers)):
                failures.append(
                    f"Smoke content type mismatch (expected JSON): {url} -> {response.headers.get('Content-Type', '')}"
                )
                continue
            try:
                response.json()
            except json.JSONDecodeError as exc:
                failures.append(f"Smoke JSON parse failed: {url} ({exc})")
                continue
        else:
            if not html_content_type(dict(response.headers)):
                warnings.append(
                    f"Smoke content type unexpected for HTML page: {url} -> {response.headers.get('Content-Type', '')}"
                )
        smoke_passed += 1

    # 2) Canonical regression checks.
    canonical_passed = 0
    for path in DEFAULT_CANONICAL_PATHS:
        url = f"{base_url}{path}"
        try:
            response = session.get(url, timeout=timeout)
        except requests.RequestException as exc:
            failures.append(f"Canonical fetch failed: {url} ({exc})")
            continue

        expected = url.rstrip("/")
        canonical = extract_canonical(response.text)
        og_url = extract_og_url(response.text)

        if canonical != expected:
            failures.append(f"Canonical mismatch: {url} -> {canonical} (expected {expected})")
            continue
        if og_url != expected:
            failures.append(f"og:url mismatch: {url} -> {og_url} (expected {expected})")
            continue

        canonical_passed += 1

    # Discover state and PT pages from sitemap.
    try:
        sitemap_urls = load_sitemap_urls(session, base_url, timeout)
    except requests.RequestException as exc:
        failures.append(f"Sitemap fetch failed: {base_url}/sitemap.xml ({exc})")
        sitemap_urls = []

    state_pages = sorted(
        u for u in sitemap_urls if u.startswith(base_url + "/") and STATE_SLUG_PATTERN.search(u)
    )
    pt_pages = sorted(u for u in state_pages if u.endswith("-pt"))

    # 3) Full PT contradiction phrase sweep.
    pt_checked = 0
    for url in pt_pages:
        try:
            response = session.get(url, timeout=timeout)
        except requests.RequestException as exc:
            failures.append(f"PT fetch failed: {url} ({exc})")
            continue

        body = response.text.lower()
        for phrase in BANNED_PT_PHRASES:
            if phrase.lower() in body:
                failures.append(f"PT banned phrase found: {url} -> '{phrase}'")
        pt_checked += 1

    # 4) HTML/API alignment sample checks.
    sampled = min(sample_size, len(state_pages))
    random.seed(seed)
    sample_pages = random.sample(state_pages, sampled) if sampled else []

    sample_passed = 0
    for state_url in sample_pages:
        slug = state_url.rsplit("/", 1)[-1]
        api_url = f"{base_url}/api/{slug}.json"
        expected_api_path = f"/api/{slug}.json"

        try:
            html_response = session.get(state_url, timeout=timeout)
            api_response = session.get(api_url, timeout=timeout)
        except requests.RequestException as exc:
            failures.append(f"Alignment fetch failed: {state_url} ({exc})")
            continue

        if html_response.status_code != 200:
            failures.append(f"Alignment HTML status mismatch: {state_url} -> {html_response.status_code}")
            continue
        if api_response.status_code != 200:
            failures.append(f"Alignment API status mismatch: {api_url} -> {api_response.status_code}")
            continue
        if not json_content_type(dict(api_response.headers)):
            failures.append(
                f"Alignment API content type mismatch: {api_url} -> {api_response.headers.get('Content-Type', '')}"
            )
            continue

        try:
            payload = api_response.json()
        except json.JSONDecodeError as exc:
            failures.append(f"Alignment API JSON parse failed: {api_url} ({exc})")
            continue

        if payload.get("identifier") != slug:
            failures.append(
                f"Alignment identifier mismatch: {api_url} -> {payload.get('identifier')} (expected {slug})"
            )
            continue
        if payload.get("url") != state_url:
            failures.append(f"Alignment payload.url mismatch: {api_url} -> {payload.get('url')} (expected {state_url})")
            continue
        if payload.get("@id") != state_url:
            failures.append(f"Alignment payload.@id mismatch: {api_url} -> {payload.get('@id')} (expected {state_url})")
            continue
        if expected_api_path not in html_response.text:
            failures.append(f"Alignment HTML missing API alternate link: {state_url} -> {expected_api_path}")
            continue

        canonical = extract_canonical(html_response.text)
        if canonical != state_url:
            failures.append(f"Alignment canonical mismatch: {state_url} -> {canonical}")
            continue

        provider = payload.get("provider")
        provider_name = provider.get("name", "") if isinstance(provider, dict) else ""
        if not provider_name:
            warnings.append(f"Alignment warning: provider.name empty in {api_url}")

        sample_passed += 1

    # 5) Back-compat alias checks.
    alias_passed = 0
    if check_aliases:
        for path in DEFAULT_ALIAS_PATHS:
            url = f"{base_url}{path}"
            try:
                response = session.get(url, timeout=timeout)
            except requests.RequestException as exc:
                failures.append(f"Alias fetch failed: {url} ({exc})")
                continue

            if response.status_code != 200:
                failures.append(f"Alias status mismatch: {url} -> {response.status_code}")
                continue
            if not json_content_type(dict(response.headers)):
                failures.append(
                    f"Alias content type mismatch: {url} -> {response.headers.get('Content-Type', '')}"
                )
                continue
            final_path = requests.utils.urlparse(response.url).path
            if not final_path.startswith("/api/"):
                failures.append(f"Alias did not resolve to /api/* path: {url} -> {response.url}")
                continue
            alias_passed += 1

    session.close()
    return {
        "base_url": base_url,
        "checks": {
            "smoke_passed": smoke_passed,
            "smoke_total": len(DEFAULT_REQUIRED_PATHS),
            "canonical_passed": canonical_passed,
            "canonical_total": len(DEFAULT_CANONICAL_PATHS),
            "pt_pages_checked": pt_checked,
            "pt_pages_total": len(pt_pages),
            "alignment_sample_passed": sample_passed,
            "alignment_sample_total": sampled,
            "alias_passed": alias_passed,
            "alias_total": len(DEFAULT_ALIAS_PATHS) if check_aliases else 0,
        },
        "failures": failures,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live trust guard checks.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base site URL to test.")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout seconds.")
    parser.add_argument("--sample-size", type=int, default=20, help="Sample size for HTML/API alignment checks.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic sampling.")
    parser.add_argument(
        "--skip-alias-checks",
        action="store_true",
        help="Skip legacy alias checks (/api/v1 and /<vertical>-pseo/api).",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        default=None,
        help="Optional path to write JSON results.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_url = normalize_base_url(args.base_url)

    result = run_guard(
        base_url=base_url,
        timeout=args.timeout,
        sample_size=max(1, args.sample_size),
        seed=args.seed,
        check_aliases=not args.skip_alias_checks,
    )

    checks = result["checks"]
    failures = result["failures"]
    warnings = result["warnings"]

    print("=" * 72)
    print("  LIVE TRUST GUARD")
    print("=" * 72)
    print(f"Base URL: {result['base_url']}")
    print(f"Smoke:            {checks['smoke_passed']}/{checks['smoke_total']}")
    print(f"Canonical:        {checks['canonical_passed']}/{checks['canonical_total']}")
    print(f"PT sweep:         {checks['pt_pages_checked']}/{checks['pt_pages_total']}")
    print(
        f"HTML/API sample:  {checks['alignment_sample_passed']}/{checks['alignment_sample_total']}"
    )
    if checks["alias_total"]:
        print(f"Alias checks:     {checks['alias_passed']}/{checks['alias_total']}")
    print(f"Failures:         {len(failures)}")
    print(f"Warnings:         {len(warnings)}")

    if failures:
        print("\nFAILURES")
        for item in failures:
            print(f" - {item}")
    if warnings:
        print("\nWARNINGS")
        for item in warnings:
            print(f" - {item}")

    if args.json_report is not None:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nJSON report written: {args.json_report}")

    if failures:
        sys.exit(1)
    print("\nPASS: no trust regressions detected")


if __name__ == "__main__":
    main()
