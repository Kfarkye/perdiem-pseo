---
description: Audit sportsync-api for production readiness and resolve all 6 blockers
---

# Sportsync → Production Workflow

## Context
- **Project:** sportsync-api (`hylnixnuabtnmjcdnujm`)
- **Verdict DB:** verdict-protocol (`wbamehtzurzxqnwkhgnc`)
- **Source DB:** Boltsks (`qffzvrnbzabcokqqrwbv`)
- **Production prompt:** `brain/.../sportsync_production_prompt.md` (full audit with diagnostic SQL)
- **ID spec:** `id_constants.py` — use DRIP namespace for all new objects/events

## Pre-flight
1. Read the full production prompt artifact for diagnostic queries and context
2. Confirm sportsync-api project status is ACTIVE_HEALTHY

## Blockers (execute in order)

### Blocker 1: RLS Policy Audit (SEC — gate)
// turbo
3. Run: `SELECT schemaname, tablename, policyname, permissive, cmd, qual FROM pg_policies WHERE schemaname = 'public' ORDER BY tablename;`
4. For every table: verify policy references `auth.uid()` or API key — not `USING (true)` on write paths
5. Fix any open policies. Log verdict to verdict-protocol with domain='sports', tags=['sec','rls','sportsync']

### Blocker 2: Rate Limiting (SEC)
6. Read the `api` edge function: `get_edge_function(project_id, 'api')`
7. Check if rate limiting logic exists and writes to `rate_limit_buckets`
8. If missing: implement token bucket (100 req/min per key, 1000 req/day free tier)
9. Log verdict

### Blocker 3: Sync Monitoring (INFRA)
10. Run staleness diagnostic:
```sql
SELECT sync_type, MAX(created_at) as last_run,
       NOW() - MAX(created_at) as staleness
FROM sync_runs
GROUP BY sync_type
HAVING NOW() - MAX(created_at) > INTERVAL '15 minutes';
```
11. If any pipeline is stale > 15 min, investigate and fix
12. Create `sync-health` edge function that runs this query and alerts on gaps
13. Log verdict

### Blocker 4: Entity Mapping Coverage (ID)
14. Run coverage check:
```sql
SELECT source, COUNT(*) as total,
       COUNT(*) FILTER (WHERE confidence < 0.8) as low_confidence
FROM entity_mappings
GROUP BY source;
```
15. Target: >95% high-confidence per source
16. Fix any low-confidence mappings in active use
17. Log verdict

### Blocker 5: Empty Table Triage (SHAPE)
18. For each of the 12 empty tables, classify as ACTIVE, DEFERRED, or SUPERSEDED
19. Add COMMENT ON TABLE with status
20. Drop or archive any SUPERSEDED tables
21. Log verdict

### Blocker 6: Stripe Wiring (MONEY)
22. Verify Stripe webhook secret is set: check edge function env vars
23. Verify `plan_entitlements` (7 rows) maps to Stripe price IDs
24. Send test checkout event, confirm `stripe_events` populates
25. Wire `customers` creation on successful payment
26. Log verdict

## Post-flight
27. Run full table audit again to confirm no regressions
28. Write final verdict to verdict-protocol: topic='sportsync-api production readiness', domain='sports'
29. Update the production prompt artifact with results

## Verdict Format
Every verdict logged must include:
- `model`: the model executing the workflow
- `session_id`: current conversation ID
- `domain`: 'sports'
- `tags`: ['sportsync', '<blocker-category>']
- `verdict`: proceed | revise | abort
- `evidence`: what was found + what was fixed
- `gaps`: what remains
