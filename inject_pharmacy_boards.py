#!/usr/bin/env python3
"""
Inject real Board of Pharmacy contact data from NABP directory
into pharmacist-pseo and pharm-pseo JSON files.
Both verticals share the same state Board of Pharmacy.
Source: https://nabp.pharmacy/boards-of-pharmacy/ (retrieved 2026-02-25)
"""

import json
from pathlib import Path

SCRATCH = Path("/Users/k.far.88/.gemini/antigravity/scratch")

# NABP directory data: state_slug -> {phone, url}
PHARMACY_BOARDS = {
    "alabama":        {"phone": "(205) 981-2280", "url": "https://www.albop.com/", "name": "Alabama Board of Pharmacy"},
    "alaska":         {"phone": "(907) 465-2550", "url": "https://www.commerce.alaska.gov/web/cbpl/ProfessionalLicensing/BoardofPharmacy.aspx", "name": "Alaska Board of Pharmacy"},
    "arizona":        {"phone": "(602) 771-2727", "url": "https://pharmacy.az.gov/", "name": "Arizona Board of Pharmacy"},
    "arkansas":       {"phone": "(501) 682-0190", "url": "https://www.pharmacyboard.arkansas.gov/", "name": "Arkansas Board of Pharmacy"},
    "california":     {"phone": "(916) 518-3100", "url": "https://www.pharmacy.ca.gov", "name": "California Board of Pharmacy"},
    "colorado":       {"phone": "(303) 894-7800", "url": "https://www.colorado.gov/pacific/dora/Pharmacy", "name": "Colorado Board of Pharmacy"},
    "connecticut":    {"phone": "(860) 713-6070", "url": "https://portal.ct.gov/DCP/Drug-Control-Division/Commission-of-Pharmacy/The-Commission-of-Pharmacy", "name": "Connecticut Commission of Pharmacy"},
    "dc":             {"phone": "(202) 724-8800", "url": "https://dchealth.dc.gov/bop", "name": "District of Columbia Board of Pharmacy"},
    "delaware":       {"phone": "(302) 744-4500", "url": "https://dpr.delaware.gov/boards/pharmacy/", "name": "Delaware Board of Pharmacy"},
    "florida":        {"phone": "(850) 245-4474", "url": "https://www.floridaspharmacy.gov/", "name": "Florida Board of Pharmacy"},
    "georgia":        {"phone": "(404) 651-8000", "url": "https://gbp.georgia.gov", "name": "Georgia Board of Pharmacy"},
    "hawaii":         {"phone": "(808) 586-2708", "url": "https://cca.hawaii.gov/pvl/boards/pharmacy/", "name": "Hawaii Board of Pharmacy"},
    "idaho":          {"phone": "(208) 334-3233", "url": "https://dopl.idaho.gov/bop/", "name": "Idaho Board of Pharmacy"},
    "illinois":       {"phone": "(800) 560-6420", "url": "http://idfpr.illinois.gov/profs/pharm.asp", "name": "Illinois Board of Pharmacy"},
    "indiana":        {"phone": "(317) 234-2067", "url": "http://www.bop.in.gov/", "name": "Indiana Board of Pharmacy"},
    "iowa":           {"phone": "(515) 281-5944", "url": "https://pharmacy.iowa.gov/", "name": "Iowa Board of Pharmacy"},
    "kansas":         {"phone": "(785) 296-4056", "url": "https://www.pharmacy.ks.gov/", "name": "Kansas Board of Pharmacy"},
    "kentucky":       {"phone": "(502) 564-7910", "url": "https://pharmacy.ky.gov/", "name": "Kentucky Board of Pharmacy"},
    "louisiana":      {"phone": "(225) 925-6496", "url": "http://www.pharmacy.la.gov/", "name": "Louisiana Board of Pharmacy"},
    "maine":          {"phone": "(207) 624-8686", "url": "https://www.maine.gov/pfr/professionallicensing/professions/board-pharmacy", "name": "Maine Board of Pharmacy"},
    "maryland":       {"phone": "(410) 764-4755", "url": "http://dhmh.maryland.gov/pharmacy/Pages/index.aspx", "name": "Maryland Board of Pharmacy"},
    "massachusetts":  {"phone": "(800) 414-0168", "url": "https://www.mass.gov/dph/boards/pharmacy", "name": "Massachusetts Board of Pharmacy"},
    "michigan":       {"phone": "(517) 241-0199", "url": "https://www.michigan.gov/lara/0,4601,7-154-72600---,00.html", "name": "Michigan Board of Pharmacy"},
    "minnesota":      {"phone": "(651) 201-2825", "url": "https://mn.gov/boards/pharmacy/", "name": "Minnesota Board of Pharmacy"},
    "mississippi":    {"phone": "(601) 899-8880", "url": "http://www.mbp.state.ms.us/", "name": "Mississippi Board of Pharmacy"},
    "missouri":       {"phone": "(573) 751-0091", "url": "https://www.pr.mo.gov/pharmacists.asp", "name": "Missouri Board of Pharmacy"},
    "montana":        {"phone": "(406) 841-2371", "url": "https://boards.bsd.dli.mt.gov/pharmacy/", "name": "Montana Board of Pharmacy"},
    "nebraska":       {"phone": "(402) 471-2115", "url": "http://dhhs.ne.gov/licensure/Pages/Licensing-Home-Page.aspx", "name": "Nebraska Board of Pharmacy"},
    "nevada":         {"phone": "(775) 850-1440", "url": "https://bop.nv.gov/", "name": "Nevada Board of Pharmacy"},
    "new-hampshire":  {"phone": "(603) 271-2152", "url": "https://www.oplc.nh.gov/board-pharmacy", "name": "New Hampshire Board of Pharmacy"},
    "new-jersey":     {"phone": "(973) 504-6450", "url": "https://www.njconsumeraffairs.gov/phar", "name": "New Jersey Board of Pharmacy"},
    "new-mexico":     {"phone": "(505) 222-9830", "url": "https://www.rld.nm.gov/", "name": "New Mexico Board of Pharmacy"},
    "new-york":       {"phone": "(518) 474-3817", "url": "https://www.op.nysed.gov/professions-index/pharmacy", "name": "New York Board of Pharmacy"},
    "north-carolina": {"phone": "(919) 246-1050", "url": "http://www.ncbop.org/", "name": "North Carolina Board of Pharmacy"},
    "north-dakota":   {"phone": "(701) 877-2404", "url": "https://www.nodakpharmacy.com/", "name": "North Dakota Board of Pharmacy"},
    "ohio":           {"phone": "(614) 466-4143", "url": "https://www.pharmacy.ohio.gov", "name": "Ohio Board of Pharmacy"},
    "oklahoma":       {"phone": "(405) 521-3815", "url": "http://www.pharmacy.ok.gov/", "name": "Oklahoma Board of Pharmacy"},
    "oregon":         {"phone": "(971) 673-0001", "url": "https://www.oregon.gov/pharmacy/Pages/index.aspx", "name": "Oregon Board of Pharmacy"},
    "pennsylvania":   {"phone": "(833) 367-2762", "url": "https://www.dos.pa.gov/ProfessionalLicensing/BoardsCommissions/Pharmacy/Pages/default.aspx", "name": "Pennsylvania Board of Pharmacy"},
    "rhode-island":   {"phone": "(401) 222-5960", "url": "https://health.ri.gov/licenses/", "name": "Rhode Island Board of Pharmacy"},
    "south-carolina": {"phone": "(803) 896-4700", "url": "https://llr.sc.gov/bop/", "name": "South Carolina Board of Pharmacy"},
    "south-dakota":   {"phone": "(605) 362-2737", "url": "https://doh.sd.gov/licensing-and-records/boards/pharmacy/", "name": "South Dakota Board of Pharmacy"},
    "tennessee":      {"phone": "(615) 253-1299", "url": "https://www.tn.gov/health/health-program-areas/health-professional-boards/pharmacy-board.html", "name": "Tennessee Board of Pharmacy"},
    "texas":          {"phone": "(512) 305-8000", "url": "https://www.pharmacy.texas.gov/", "name": "Texas State Board of Pharmacy"},
    "utah":           {"phone": "(801) 530-6628", "url": "https://dopl.utah.gov/pharm/index.html", "name": "Utah Board of Pharmacy"},
    "vermont":        {"phone": "(802) 828-2373", "url": "https://sos.vermont.gov/pharmacy/", "name": "Vermont Board of Pharmacy"},
    "virginia":       {"phone": "(804) 367-4456", "url": "https://www.dhp.virginia.gov/pharmacy", "name": "Virginia Board of Pharmacy"},
    "washington":     {"phone": "(360) 236-4946", "url": "https://doh.wa.gov/licenses-permits-and-certificates/facilities-z/pharmacies-and-pharmaceutical-firms/commission-information", "name": "Washington Pharmacy Quality Assurance Commission"},
    "west-virginia":  {"phone": "(304) 558-0558", "url": "https://www.wvbop.com/", "name": "West Virginia Board of Pharmacy"},
    "wisconsin":      {"phone": "(608) 266-2112", "url": "https://dsps.wi.gov/", "name": "Wisconsin Pharmacy Examining Board"},
    "wyoming":        {"phone": "(307) 634-9636", "url": "https://pharmacyboard.wyo.gov", "name": "Wyoming Board of Pharmacy"},
}

# Apply to both pharmacist-pseo and pharm-pseo
for vertical in ["pharmacist-pseo", "pharm-pseo"]:
    json_dir = SCRATCH / vertical / "database" / "json"
    suffix = "pharmacist" if vertical == "pharmacist-pseo" else "pharm"
    updated = 0

    for state_slug, board_info in PHARMACY_BOARDS.items():
        json_file = json_dir / f"{state_slug}-{suffix}.json"
        if not json_file.exists():
            continue

        data = json.loads(json_file.read_text(encoding="utf-8"))
        board = data.get("board", {})

        board["name"] = board_info["name"]
        board["phone"] = board_info["phone"]
        board["url"] = board_info["url"]
        # Set fax and email to N/A since NABP doesn't list them
        if board.get("fax") == "PENDING":
            board["fax"] = "N/A (contact by phone)"
        if board.get("email") == "PENDING":
            board["email"] = "See board website"
        if board.get("mailing_address") == "PENDING":
            board["mailing_address"] = "See board website"
        if board.get("physical_address") == "PENDING":
            board["physical_address"] = "See board website"

        data["board"] = board
        data["board_source_url"] = board_info["url"]

        json_file.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        updated += 1

    print(f"  {vertical}: Updated {updated} files with NABP board data")

# Final count
print(f"\n{'='*55}")
print(f"  FINAL PENDING COUNTS")
print(f"{'='*55}")

ALL = ["dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo", "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo"]
grand = 0
for v in ALL:
    jd = SCRATCH / v / "database" / "json"
    vt = sum(f.read_text().count('"PENDING"') for f in jd.glob("*.json")) if jd.exists() else 0
    grand += vt
    e = "✅" if vt == 0 else "⚠️"
    print(f"  {v:20s}  {vt:5d}  {e}")
print(f"{'='*55}")
print(f"  GRAND TOTAL:         {grand}")
print(f"{'='*55}")
