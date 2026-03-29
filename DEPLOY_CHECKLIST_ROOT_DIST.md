# Root Dist Deploy Checklist

This checklist is the release contract for `www.statelicensingreference.com`.
Only root `dist/` is deployable output.

## 1) Build

Run:

```bash
python3 build_unified.py
```

Pass when all are true:
- Root `dist/` exists.
- Root `dist/api/` exists.
- Build reports `10 specialty pages` and `510 state pages`.

## 2) Source-of-truth audits

Run:

```bash
python3 pre_deploy_audit.py
python3 final_approval_audit.py
```

Pass when all are true:
- Both scripts exit `0`.
- No deploy-blocking errors.

## 3) Root artifact contract

Verify:
- `dist/index.html` exists (portal root).
- `dist/{vertical}.html` exists for each deployed vertical.
- `dist/{slug}.html` exists for each state-profession slug.
- `dist/api/{slug}.json` exists for each state-profession slug.

## 4) API transition contract

Canonical contract:
- Primary endpoint is `/api/{slug}.json`.

Back-compat aliases required in root `vercel.json`:
- `/api/v1/:slug.json -> /api/:slug.json`
- `/:vertical-pseo/api/:slug.json -> /api/:slug.json`

Rule:
- Existing `/api/{slug}.json` endpoints are stable and cannot be removed during migration.
- New verticals (CNA/DA) are additive under the same canonical path.

## 5) Trust guard smoke checks

Confirm:
- `dist/dc-dietitian.html` canonical is `/dc-dietitian` (not `-license`).
- `dist/new-mexico-dietitian.html` canonical is `/new-mexico-dietitian` (not `-license`).
- PT pages do not contain `varies, often around $100 to $200`.

## 6) Deploy gate

Deploy only if all checks above pass from root repo.
Do not deploy per-vertical `dist/` or legacy `dist-v2/` artifacts.
