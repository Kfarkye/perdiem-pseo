/**
 * perdiem.fyi Cloud Functions — Rate Intelligence Knowledge Base
 *
 * Routes:
 *   GET /                              → Index page with coverage stats
 *   GET /rates/:state/:specialty       → Rate intelligence page (HTML)
 *   GET /api/rates/:state/:specialty.json → Raw JSON API
 *   GET /tax/:state                    → Tax & wage page (HTML)
 *   GET /api/tax/:state.json           → Raw JSON API
 *   GET /sitemap.xml                   → Auto-generated sitemap
 */

const { onRequest } = require("firebase-functions/v2/https");
const { getSupabase, normalizeSpecialty, toLicensingSpecialty, STATE_NAMES, stateAbbr } = require("./supabase");
const { renderRatePage, renderTaxPage, renderIndexPage } = require("./render");

// ── Rate Intelligence Page ──────────────────────────────────────────

async function handleRatePage(state, specialtyRaw, format) {
  const sb = getSupabase();
  const abbr = stateAbbr(state);
  const stateName = STATE_NAMES[abbr] || state;
  const specialty = normalizeSpecialty(specialtyRaw);
  const licensingSpecialty = toLicensingSpecialty(specialty);

  // Parallel queries
  const [travelRes, contractRes, benchmarkRes, licensingRes, taxRes, housingRes] = await Promise.all([
    sb.from("market_travel_rates").select("*").eq("state_abbr", abbr).eq("specialty", specialty),
    sb.from("verified_contract_rates").select("*").eq("state_abbr", abbr).eq("specialty", specialty),
    sb.from("market_rate_benchmarks").select("*").or(`state_abbr.eq.${abbr},scope.eq.national`).eq("profession", specialty),
    sb.from("state_licensing_requirements").select("*").eq("state_abbr", abbr).eq("specialty", licensingSpecialty).limit(1).single(),
    sb.from("state_income_tax").select("*").eq("state_code", abbr).limit(1).single(),
    sb.from("market_housing_by_state").select("*").eq("state_abbr", abbr).limit(1).single(),
  ]);

  const data = {
    state: abbr,
    stateName,
    specialty,
    travelRates: travelRes.data || [],
    contractRates: contractRes.data || [],
    benchmarks: benchmarkRes.data || [],
    licensing: licensingRes.data || null,
    taxInfo: taxRes.data || null,
    housing: housingRes.data || null,
  };

  if (format === "json") {
    return { type: "json", body: data };
  }
  return { type: "html", body: renderRatePage(data) };
}

// ── Tax Page ────────────────────────────────────────────────────────

async function handleTaxPage(state, format) {
  const sb = getSupabase();
  const abbr = stateAbbr(state);
  const stateName = STATE_NAMES[abbr] || state;

  const [taxRes, wageRes] = await Promise.all([
    sb.from("state_income_tax").select("*").eq("state_code", abbr).limit(1).single(),
    sb.from("state_minimum_wage").select("*").eq("state_code", abbr).limit(1).single(),
  ]);

  const data = {
    state: abbr,
    stateName,
    taxInfo: taxRes.data || null,
    minWage: wageRes.data || null,
  };

  if (format === "json") {
    return { type: "json", body: data };
  }
  return { type: "html", body: renderTaxPage(data) };
}

// ── Index Page ──────────────────────────────────────────────────────

async function handleIndex() {
  const sb = getSupabase();

  const statesRes = await sb.from("state_income_tax").select("state_code, state_name").order("state_name");

  // Coverage stats — hardcoded from latest audit; no RPC needed
  const coverage = [
    { source: "state_licensing_requirements", total_rows: 408, states: 51, specialties: 8 },
    { source: "verified_contract_rates", total_rows: 109, states: 26, specialties: 7 },
    { source: "market_travel_rates", total_rows: 67, states: 19, specialties: 12 },
    { source: "market_rate_benchmarks", total_rows: 38, states: 16, specialties: 5 },
    { source: "state_income_tax", total_rows: 51, states: 51, specialties: 0 },
    { source: "gsa_rates", total_rows: 297, states: "all", specialties: 0 },
  ];

  const specialties = ["PT", "OT", "SLP", "RN", "RRT", "LPN", "CNA", "DietSrv", "RAD", "PHLEB"];

  return {
    type: "html",
    body: renderIndexPage({
      states: statesRes.data || [],
      specialties,
      coverage,
    }),
  };
}

// ── Sitemap ─────────────────────────────────────────────────────────

async function handleSitemap() {
  const sb = getSupabase();

  const [statesRes, ratesRes] = await Promise.all([
    sb.from("state_income_tax").select("state_code"),
    sb.from("market_travel_rates").select("state_abbr, specialty"),
  ]);

  const base = "https://perdiem.fyi";
  let urls = [`${base}/`];

  // Tax pages for all states
  for (const s of statesRes.data || []) {
    urls.push(`${base}/tax/${s.state_code.toLowerCase()}`);
  }

  // Rate pages for all state/specialty combos with data
  const seen = new Set();
  for (const r of ratesRes.data || []) {
    const key = `${r.state_abbr.toLowerCase()}/${r.specialty.toLowerCase()}`;
    if (!seen.has(key)) {
      seen.add(key);
      urls.push(`${base}/rates/${key}`);
    }
  }

  // Also add verified contract rate combos
  const contractRes = await sb.from("verified_contract_rates").select("state_abbr, specialty");
  for (const r of contractRes.data || []) {
    const key = `${r.state_abbr.toLowerCase()}/${r.specialty.toLowerCase()}`;
    if (!seen.has(key)) {
      seen.add(key);
      urls.push(`${base}/rates/${key}`);
    }
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(u => `  <url><loc>${u}</loc><changefreq>weekly</changefreq></url>`).join("\n")}
</urlset>`;

  return { type: "xml", body: xml };
}

// ── Route Context Parser ────────────────────────────────────────────
// Architecture: URL → route context → handler → packet → render

function parseRoute(path) {
  const segments = path.replace(/\/$/, "").split("/").filter(Boolean);
  const clean = path.replace(/\/$/, "") || "/";

  // /sitemap.xml
  if (clean === "/sitemap.xml") {
    return { page_type: "sitemap" };
  }
  // /api/rates/:state/:specialty.json
  if (segments[0] === "api" && segments[1] === "rates" && segments.length === 4) {
    return {
      page_type: "rate",
      format: "json",
      state: segments[2],
      specialty: segments[3].replace(/\.json$/, ""),
    };
  }
  // /api/tax/:state.json
  if (segments[0] === "api" && segments[1] === "tax" && segments.length === 3) {
    return {
      page_type: "tax",
      format: "json",
      state: segments[2].replace(/\.json$/, ""),
    };
  }
  // /rates/:state/:specialty
  if (segments[0] === "rates" && segments.length === 3) {
    return {
      page_type: "rate",
      format: "html",
      state: segments[1],
      specialty: segments[2],
    };
  }
  // /tax/:state
  if (segments[0] === "tax" && segments.length === 2) {
    return {
      page_type: "tax",
      format: "html",
      state: segments[1],
    };
  }
  // /
  if (clean === "/") {
    return { page_type: "index" };
  }
  return null;
}

// ── Route Dispatcher ────────────────────────────────────────────────

const HANDLERS = {
  sitemap: () => handleSitemap(),
  rate: (route) => handleRatePage(route.state, route.specialty, route.format),
  tax: (route) => handleTaxPage(route.state, route.format),
  index: () => handleIndex(),
};

exports.app = onRequest(
  { region: "us-central1", memory: "256MiB", timeoutSeconds: 30 },
  async (req, res) => {
    // Handle CORS preflight
    if (req.method === "OPTIONS") {
      res.set("Access-Control-Allow-Origin", "*");
      res.set("Access-Control-Allow-Methods", "GET, OPTIONS");
      res.set("Access-Control-Allow-Headers", "Content-Type");
      res.set("Access-Control-Max-Age", "86400");
      res.status(204).send("");
      return;
    }
    try {
      // 1. Parse route into structured context
      const route = parseRoute(req.path);
      if (!route) {
        res.status(404).send("Not found");
        return;
      }

      // 2. Dispatch to handler
      const handler = HANDLERS[route.page_type];
      const result = await handler(route);

      // Set cache headers (1 hour CDN cache, revalidate)
      res.set("Cache-Control", "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400");
      res.set("Access-Control-Allow-Origin", "*");

      if (result.type === "json") {
        res.set("Content-Type", "application/json");
        res.json(result.body);
      } else if (result.type === "xml") {
        res.set("Content-Type", "application/xml");
        res.send(result.body);
      } else {
        res.send(result.body);
      }
    } catch (err) {
      console.error("perdiem.fyi error:", err);
      res.status(500).send("Internal error");
    }
  }
);
