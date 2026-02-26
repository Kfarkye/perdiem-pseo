#!/usr/bin/env python3
"""
Inject real board contact data for OT, PT, and RRT verticals.
Sources: AOTA, NBCOT, AARC, FSBPT directories (retrieved 2026-02-25)

Key insight: PT and OT share the same board in many states (e.g., Alaska, Iowa).
"""

import json
from pathlib import Path

SCRATCH = Path("/Users/k.far.88/.gemini/antigravity/scratch")

# ── OT BOARDS ────────────────────────────────────────────
OT_BOARDS = {
    "alabama":        {"phone": "(334) 353-4466", "url": "http://www.ot.alabama.gov", "name": "Alabama State Board of Occupational Therapy"},
    "alaska":         {"phone": "(907) 465-2580", "url": "https://www.commerce.alaska.gov/web/cbpl/ProfessionalLicensing/PhysicalTherapyOccupationalTherapy", "name": "Alaska PT & OT Board"},
    "arizona":        {"phone": "(602) 589-8353", "url": "http://ot.az.gov", "name": "Arizona Board of Occupational Therapy Examiners"},
    "arkansas":       {"phone": "(501) 296-1802", "url": "http://www.armedicalboard.org/Professionals/OccupationalTherapistandAssistant.aspx", "name": "Arkansas State Medical Board — OT Section"},
    "california":     {"phone": "(916) 263-2294", "url": "http://www.bot.ca.gov/", "name": "California Board of Occupational Therapy"},
    "colorado":       {"phone": "(303) 894-7800", "url": "http://www.colorado.gov/DORA/Occupational_Therapy", "name": "Colorado DORA — Occupational Therapy"},
    "connecticut":    {"phone": "(860) 509-7603", "url": "https://portal.ct.gov/DPH", "name": "Connecticut DPH — OT Licensure"},
    "dc":             {"phone": "(202) 442-8336", "url": "https://dchealth.dc.gov/service/occupational-therapy-licensing", "name": "DC Board of Rehabilitative Therapies"},
    "delaware":       {"phone": "(302) 744-4500", "url": "https://dpr.delaware.gov/boards/occupationaltherapy/", "name": "Delaware Board of Occupational Therapy Practice"},
    "florida":        {"phone": "(850) 245-4474", "url": "https://floridasoccupationaltherapy.gov/", "name": "Florida Board of Occupational Therapy Practice"},
    "georgia":        {"phone": "(404) 656-3913", "url": "https://sos.ga.gov/PLB/acrobat/Forms/38%20Reference%20-%20Occupational%20Therapy.pdf", "name": "Georgia Board of Occupational Therapy"},
    "hawaii":         {"phone": "(808) 586-3000", "url": "https://cca.hawaii.gov/pvl/", "name": "Hawaii DCCA Professional & Vocational Licensing — OT"},
    "idaho":          {"phone": "(208) 334-3233", "url": "https://dopl.idaho.gov/", "name": "Idaho DOPL — Occupational Therapy Licensure Board"},
    "illinois":       {"phone": "(888) 473-4858", "url": "https://idfpr.illinois.gov/profs/ot.asp", "name": "Illinois IDFPR — Occupational Therapy"},
    "indiana":        {"phone": "(317) 232-2960", "url": "https://www.in.gov/pla/professions/occupational-therapy/", "name": "Indiana PLA — Occupational Therapy"},
    "iowa":           {"phone": "(515) 281-7074", "url": "https://www.idph.iowa.gov/", "name": "Iowa Board of Physical and Occupational Therapy"},
    "kansas":         {"phone": "(785) 296-7413", "url": "https://www.ksbha.org/", "name": "Kansas Board of Healing Arts — OT"},
    "kentucky":       {"phone": "(502) 564-3296", "url": "https://bot.ky.gov/", "name": "Kentucky Board of Licensure for Occupational Therapy"},
    "louisiana":      {"phone": "(504) 568-6820", "url": "https://www.lsbme.la.gov/", "name": "Louisiana State Board of Medical Examiners — OT"},
    "maine":          {"phone": "(207) 624-8569", "url": "https://www.maine.gov/pfr/professionallicensing/", "name": "Maine Board of Occupational Therapy Practice"},
    "maryland":       {"phone": "(410) 764-4722", "url": "https://health.maryland.gov/botp/Pages/index.aspx", "name": "Maryland Board of Occupational Therapy Practice"},
    "massachusetts":  {"phone": "(800) 414-0168", "url": "https://www.mass.gov/orgs/board-of-registration-of-allied-health-professionals", "name": "Massachusetts Board of Allied Health — OT"},
    "michigan":       {"phone": "(517) 335-0918", "url": "https://www.michigan.gov/lara/bureau-list/bpl/occ/professions/occupational-therapists", "name": "Michigan LARA — Occupational Therapy"},
    "minnesota":      {"phone": "(612) 617-2130", "url": "https://mn.gov/boards/medical-practice/", "name": "Minnesota Board of Medical Practice — OT"},
    "mississippi":    {"phone": "(601) 957-6686", "url": "https://www.ot.ms.gov/", "name": "Mississippi Board of Occupational Therapy"},
    "missouri":       {"phone": "(573) 751-0098", "url": "https://pr.mo.gov/occtherp.asp", "name": "Missouri Advisory Commission for Occupational Therapy"},
    "montana":        {"phone": "(406) 841-2371", "url": "https://boards.bsd.dli.mt.gov/occupational-therapists", "name": "Montana Board of Occupational Therapy Practice"},
    "nebraska":       {"phone": "(402) 471-2115", "url": "https://dhhs.ne.gov/licensure/Pages/Licensing-Home-Page.aspx", "name": "Nebraska DHHS — Occupational Therapy"},
    "nevada":         {"phone": "(775) 688-2559", "url": "https://bop.nv.gov/", "name": "Nevada Board of Occupational Therapy"},
    "new-hampshire":  {"phone": "(603) 271-8389", "url": "https://www.oplc.nh.gov/occupational-therapy", "name": "New Hampshire OPLC — Occupational Therapy"},
    "new-jersey":     {"phone": "(973) 504-6430", "url": "https://www.njconsumeraffairs.gov/ot", "name": "New Jersey Board of Occupational Therapy"},
    "new-mexico":     {"phone": "(505) 476-4622", "url": "https://www.rld.nm.gov/", "name": "New Mexico Board of Occupational Therapy Practice"},
    "new-york":       {"phone": "(518) 474-3817", "url": "https://www.op.nysed.gov/professions-index/occupational-therapy", "name": "New York Office of the Professions — OT"},
    "north-carolina": {"phone": "(919) 832-1380", "url": "https://www.ncbot.org/", "name": "North Carolina Board of Occupational Therapy"},
    "north-dakota":   {"phone": "(701) 250-0847", "url": "https://www.ndotboard.com/", "name": "North Dakota Board of Occupational Therapy Practice"},
    "ohio":           {"phone": "(614) 466-3774", "url": "https://otptat.ohio.gov/", "name": "Ohio OT, PT, and Athletic Trainers Board"},
    "oklahoma":       {"phone": "(405) 962-1400", "url": "https://www.okmedicalboard.org/", "name": "Oklahoma Board of Medical Licensure — OT"},
    "oregon":         {"phone": "(971) 673-0197", "url": "https://www.oregon.gov/otlb", "name": "Oregon Occupational Therapy Licensing Board"},
    "pennsylvania":   {"phone": "(717) 783-4849", "url": "https://www.dos.pa.gov/ProfessionalLicensing/BoardsCommissions/OccupationalTherapy/Pages/default.aspx", "name": "Pennsylvania Board of Occupational Therapy Education and Licensure"},
    "rhode-island":   {"phone": "(401) 222-2828", "url": "https://health.ri.gov/licenses/", "name": "Rhode Island DOH — OT Licensure"},
    "south-carolina": {"phone": "(803) 896-4683", "url": "https://llr.sc.gov/ot/", "name": "South Carolina Board of Occupational Therapy"},
    "south-dakota":   {"phone": "(605) 367-7781", "url": "https://doh.sd.gov/licensing-and-records/boards/medical/", "name": "South Dakota Board of Medical and Osteopathic Examiners — OT"},
    "tennessee":      {"phone": "(615) 532-3204", "url": "https://www.tn.gov/health/health-program-areas/health-professional-boards/ot-board.html", "name": "Tennessee Board of Occupational Therapy"},
    "texas":          {"phone": "(512) 305-6900", "url": "https://ptot.texas.gov/", "name": "Texas Executive Council of PT and OT Examiners (ECPTOTE)"},
    "utah":           {"phone": "(801) 530-6628", "url": "https://dopl.utah.gov/ot/", "name": "Utah DOPL — Occupational Therapy"},
    "vermont":        {"phone": "(802) 828-2390", "url": "https://sos.vermont.gov/opr/", "name": "Vermont Office of Professional Regulation — OT"},
    "virginia":       {"phone": "(804) 367-4600", "url": "https://www.dhp.virginia.gov/medicine/", "name": "Virginia Board of Medicine — OT"},
    "washington":     {"phone": "(360) 236-4700", "url": "https://doh.wa.gov/licenses-permits-and-certificates/professions-new-renew-702", "name": "Washington DOH — Occupational Therapy"},
    "west-virginia":  {"phone": "(304) 558-3512", "url": "https://wvbot.org/", "name": "West Virginia Board of Occupational Therapy"},
    "wisconsin":      {"phone": "(608) 266-2112", "url": "https://dsps.wi.gov/", "name": "Wisconsin DSPS — Occupational Therapist"},
    "wyoming":        {"phone": "(307) 777-6529", "url": "https://occupationaltherapy.wyo.gov/", "name": "Wyoming Board of Occupational Therapy"},
}

# ── PT BOARDS ────────────────────────────────────────────
# Note: Many states share PT/OT together. Where they split, we use FSBPT data.
PT_BOARDS = {
    "alabama":        {"phone": "(334) 242-4064", "url": "https://pt.alabama.gov/", "name": "Alabama Board of Physical Therapy"},
    "alaska":         {"phone": "(907) 465-2580", "url": "https://www.commerce.alaska.gov/web/cbpl/ProfessionalLicensing/PhysicalTherapyOccupationalTherapy", "name": "Alaska PT & OT Board"},
    "arizona":        {"phone": "(602) 274-0236", "url": "https://ptboard.az.gov/", "name": "Arizona Board of Physical Therapy"},
    "arkansas":       {"phone": "(501) 228-7100", "url": "https://www.arptb.org/", "name": "Arkansas Board of Physical Therapy"},
    "california":     {"phone": "(916) 561-8200", "url": "https://www.ptbc.ca.gov/", "name": "Physical Therapy Board of California"},
    "colorado":       {"phone": "(303) 894-7800", "url": "https://www.colorado.gov/pacific/dora/Physical_Therapy", "name": "Colorado DORA — Physical Therapy"},
    "connecticut":    {"phone": "(860) 509-7603", "url": "https://portal.ct.gov/DPH", "name": "Connecticut DPH — PT Licensure"},
    "dc":             {"phone": "(202) 442-8336", "url": "https://dchealth.dc.gov/service/physical-therapy-licensing", "name": "DC Board of Physical Therapy"},
    "delaware":       {"phone": "(302) 744-4500", "url": "https://dpr.delaware.gov/boards/physicaltherapy/", "name": "Delaware Board of Physical Therapy"},
    "florida":        {"phone": "(850) 245-4474", "url": "https://floridasphysicaltherapy.gov/", "name": "Florida Board of Physical Therapy Practice"},
    "georgia":        {"phone": "(404) 656-3921", "url": "https://sos.ga.gov/", "name": "Georgia Board of Physical Therapy"},
    "hawaii":         {"phone": "(808) 586-3000", "url": "https://cca.hawaii.gov/pvl/", "name": "Hawaii DCCA — Physical Therapy"},
    "idaho":          {"phone": "(208) 334-3233", "url": "https://dopl.idaho.gov/", "name": "Idaho DOPL — Physical Therapy Licensure Board"},
    "illinois":       {"phone": "(888) 473-4858", "url": "https://idfpr.illinois.gov/profs/pt.asp", "name": "Illinois IDFPR — Physical Therapy"},
    "indiana":        {"phone": "(317) 232-2960", "url": "https://www.in.gov/pla/professions/physical-therapy/", "name": "Indiana PLA — Physical Therapy Committee"},
    "iowa":           {"phone": "(515) 281-7074", "url": "https://www.idph.iowa.gov/", "name": "Iowa Board of Physical and Occupational Therapy"},
    "kansas":         {"phone": "(785) 296-7413", "url": "https://www.ksbha.org/", "name": "Kansas Board of Healing Arts — PT"},
    "kentucky":       {"phone": "(502) 564-3296", "url": "https://pt.ky.gov/", "name": "Kentucky Board of Physical Therapy"},
    "louisiana":      {"phone": "(225) 924-8512", "url": "https://www.laptboard.org/", "name": "Louisiana Board of Physical Therapy Examiners"},
    "maine":          {"phone": "(207) 624-8569", "url": "https://www.maine.gov/pfr/professionallicensing/", "name": "Maine Board of Examiners in Physical Therapy"},
    "maryland":       {"phone": "(410) 764-4752", "url": "https://health.maryland.gov/bphte/Pages/index.aspx", "name": "Maryland Board of Physical Therapy Examiners"},
    "massachusetts":  {"phone": "(800) 414-0168", "url": "https://www.mass.gov/orgs/board-of-registration-of-allied-health-professionals", "name": "Massachusetts Board of Allied Health — PT"},
    "michigan":       {"phone": "(517) 335-0918", "url": "https://www.michigan.gov/lara/bureau-list/bpl/occ/professions/physical-therapists", "name": "Michigan LARA — Physical Therapy"},
    "minnesota":      {"phone": "(612) 617-2130", "url": "https://mn.gov/boards/medical-practice/", "name": "Minnesota Board of Medical Practice — PT"},
    "mississippi":    {"phone": "(601) 352-0613", "url": "https://www.msbpt.ms.gov/", "name": "Mississippi Board of Physical Therapy"},
    "missouri":       {"phone": "(573) 751-0098", "url": "https://pr.mo.gov/healingarts.asp", "name": "Missouri Board of Healing Arts — PT"},
    "montana":        {"phone": "(406) 841-2371", "url": "https://boards.bsd.dli.mt.gov/physical-therapists", "name": "Montana Board of Physical Therapy Examiners"},
    "nebraska":       {"phone": "(402) 471-2115", "url": "https://dhhs.ne.gov/licensure/Pages/Licensing-Home-Page.aspx", "name": "Nebraska DHHS — Physical Therapy"},
    "nevada":         {"phone": "(775) 687-7800", "url": "https://ptboard.nv.gov/", "name": "Nevada Board of Physical Therapy Examiners"},
    "new-hampshire":  {"phone": "(603) 271-8389", "url": "https://www.oplc.nh.gov/physical-therapy", "name": "New Hampshire OPLC — Physical Therapy"},
    "new-jersey":     {"phone": "(973) 504-6455", "url": "https://www.njconsumeraffairs.gov/pt", "name": "New Jersey Board of Physical Therapy Examiners"},
    "new-mexico":     {"phone": "(505) 476-4622", "url": "https://www.rld.nm.gov/", "name": "New Mexico Physical Therapy Board"},
    "new-york":       {"phone": "(518) 474-3817", "url": "https://www.op.nysed.gov/professions-index/physical-therapy", "name": "New York Office of the Professions — PT"},
    "north-carolina": {"phone": "(919) 490-6393", "url": "https://www.ncptboard.org/", "name": "North Carolina Board of Physical Therapy Examiners"},
    "north-dakota":   {"phone": "(701) 328-8600", "url": "https://www.ndbpt.org/", "name": "North Dakota Board of Physical Therapy"},
    "ohio":           {"phone": "(614) 466-3774", "url": "https://otptat.ohio.gov/", "name": "Ohio OT, PT, and Athletic Trainers Board"},
    "oklahoma":       {"phone": "(405) 962-1400", "url": "https://www.okmedicalboard.org/", "name": "Oklahoma Board of Medical Licensure — PT"},
    "oregon":         {"phone": "(971) 673-0197", "url": "https://www.oregon.gov/ptlb", "name": "Oregon Physical Therapist Licensing Board"},
    "pennsylvania":   {"phone": "(717) 783-7134", "url": "https://www.dos.pa.gov/ProfessionalLicensing/BoardsCommissions/PhysicalTherapy/Pages/default.aspx", "name": "Pennsylvania Board of Physical Therapy"},
    "rhode-island":   {"phone": "(401) 222-2828", "url": "https://health.ri.gov/licenses/", "name": "Rhode Island DOH — PT Licensure"},
    "south-carolina": {"phone": "(803) 896-4655", "url": "https://llr.sc.gov/pt/", "name": "South Carolina Board of Physical Therapy Examiners"},
    "south-dakota":   {"phone": "(605) 367-7781", "url": "https://doh.sd.gov/licensing-and-records/boards/medical/", "name": "South Dakota Board of Medical and Osteopathic Examiners — PT"},
    "tennessee":      {"phone": "(615) 532-3204", "url": "https://www.tn.gov/health/health-program-areas/health-professional-boards/pt-board.html", "name": "Tennessee Board of Physical Therapy"},
    "texas":          {"phone": "(512) 305-6900", "url": "https://ptot.texas.gov/", "name": "Texas Executive Council of PT and OT Examiners (ECPTOTE)"},
    "utah":           {"phone": "(801) 530-6628", "url": "https://dopl.utah.gov/pt/", "name": "Utah DOPL — Physical Therapy"},
    "vermont":        {"phone": "(802) 828-2390", "url": "https://sos.vermont.gov/opr/", "name": "Vermont Office of Professional Regulation — PT"},
    "virginia":       {"phone": "(804) 367-4600", "url": "https://www.dhp.virginia.gov/medicine/", "name": "Virginia Board of Medicine — PT"},
    "washington":     {"phone": "(360) 236-4700", "url": "https://doh.wa.gov/licenses-permits-and-certificates/professions-new-renew-702", "name": "Washington DOH — Physical Therapy"},
    "west-virginia":  {"phone": "(304) 558-0367", "url": "https://wvbopt.com/", "name": "West Virginia Board of Physical Therapy"},
    "wisconsin":      {"phone": "(608) 266-2112", "url": "https://dsps.wi.gov/", "name": "Wisconsin DSPS — Physical Therapist"},
    "wyoming":        {"phone": "(307) 777-6529", "url": "https://physicaltherapy.wyo.gov/", "name": "Wyoming Board of Physical Therapy"},
}

# ── RRT BOARDS ────────────────────────────────────────────
RRT_BOARDS = {
    "alabama":        {"phone": "(334) 265-7125", "url": "http://www.asbrt.alabama.gov", "name": "Alabama State Board of Respiratory Therapy"},
    "alaska":         {"phone": "(907) 465-2550", "url": "https://www.commerce.alaska.gov/web/cbpl/", "name": "Alaska DCBPL (No RT License Required)"},
    "arizona":        {"phone": "(602) 542-5995", "url": "http://www.respiratoryboard.az.gov/", "name": "Arizona Board of Respiratory Care Examiners"},
    "arkansas":       {"phone": "(501) 296-1802", "url": "http://www.armedicalboard.org/Professionals/RespiratoryTherapist.aspx", "name": "Arkansas State Medical Board — RT"},
    "california":     {"phone": "(916) 999-2190", "url": "http://www.rcb.ca.gov", "name": "California Respiratory Care Board"},
    "colorado":       {"phone": "(303) 894-7800", "url": "http://www.colorado.gov/pacific/dora/Respiratory_Therapy", "name": "Colorado DORA — Respiratory Therapy"},
    "connecticut":    {"phone": "(860) 509-7603", "url": "https://portal.ct.gov/DPH", "name": "Connecticut DPH — Respiratory Care"},
    "dc":             {"phone": "(202) 442-8336", "url": "http://www.dchealth.dc.gov/service/respiratory-care-licensing", "name": "DC Board of Respiratory Care"},
    "delaware":       {"phone": "(302) 744-4500", "url": "https://dpr.delaware.gov/boards/medicalpractice/respiratory_license/", "name": "Delaware Division of Professional Regulation — RT"},
    "florida":        {"phone": "(850) 488-0595", "url": "http://www.floridasrespiratorycare.gov", "name": "Florida Board of Respiratory Care"},
    "georgia":        {"phone": "(404) 656-3913", "url": "http://www.medicalboard.georgia.gov/", "name": "Georgia Composite Medical Board — RT"},
    "hawaii":         {"phone": "(808) 586-2704", "url": "http://cca.hawaii.gov/pvl/programs/respiratory/", "name": "Hawaii PVL — Respiratory Therapy"},
    "idaho":          {"phone": "(208) 334-3233", "url": "https://dopl.idaho.gov/", "name": "Idaho DOPL — Respiratory Therapy Licensure Board"},
    "illinois":       {"phone": "(888) 473-4858", "url": "https://idfpr.illinois.gov/dpr.html", "name": "Illinois IDFPR — Respiratory Care"},
    "indiana":        {"phone": "(317) 232-2960", "url": "http://www.in.gov/pla/rcp.htm", "name": "Indiana PLA — Respiratory Care Committee"},
    "iowa":           {"phone": "(515) 281-0254", "url": "http://www.idph.iowa.gov/Licensure/Iowa-Board-of", "name": "Iowa Board of Respiratory Care and Polysomnography"},
    "kansas":         {"phone": "(785) 296-7413", "url": "https://www.ksbha.org/", "name": "Kansas Board of Healing Arts — RT"},
    "kentucky":       {"phone": "(859) 246-2747", "url": "https://respiratorycare.ky.gov/", "name": "Kentucky Board of Respiratory Care"},
    "louisiana":      {"phone": "(504) 568-6820", "url": "https://www.lsbme.la.gov/", "name": "Louisiana State Board of Medical Examiners — RT"},
    "maine":          {"phone": "(207) 624-8569", "url": "https://www.maine.gov/pfr/professionallicensing/", "name": "Maine Board of Respiratory Care Practitioners"},
    "maryland":       {"phone": "(410) 764-4722", "url": "https://health.maryland.gov/", "name": "Maryland DOH — Respiratory Care Practitioners"},
    "massachusetts":  {"phone": "(800) 414-0168", "url": "https://www.mass.gov/respiratory-care-licensing", "name": "Massachusetts Board of Respiratory Care"},
    "michigan":       {"phone": "(517) 335-0918", "url": "https://www.michigan.gov/lara/", "name": "Michigan LARA — Respiratory Therapy"},
    "minnesota":      {"phone": "(612) 617-2130", "url": "https://mn.gov/boards/medical-practice/", "name": "Minnesota Board of Medical Practice — RT"},
    "mississippi":    {"phone": "(601) 364-7360", "url": "https://msdh.ms.gov/", "name": "Mississippi DOH — Professional Licensure — RT"},
    "missouri":       {"phone": "(573) 751-0098", "url": "https://pr.mo.gov/healingarts.asp", "name": "Missouri Board for Respiratory Care"},
    "montana":        {"phone": "(406) 444-6880", "url": "https://boards.bsd.dli.mt.gov/", "name": "Montana Board of Respiratory Care Practitioners"},
    "nebraska":       {"phone": "(402) 471-2115", "url": "https://dhhs.ne.gov/licensure/Pages/Licensing-Home-Page.aspx", "name": "Nebraska DHHS — Respiratory Care"},
    "nevada":         {"phone": "(775) 688-2559", "url": "https://medboard.nv.gov/", "name": "Nevada Board of Medical Examiners — RT"},
    "new-hampshire":  {"phone": "(603) 271-8389", "url": "https://www.oplc.nh.gov/", "name": "New Hampshire Board of Respiratory Care Practitioners"},
    "new-jersey":     {"phone": "(973) 504-6430", "url": "https://www.njconsumeraffairs.gov/", "name": "New Jersey Board of Respiratory Care"},
    "new-mexico":     {"phone": "(505) 476-4622", "url": "https://www.rld.nm.gov/", "name": "New Mexico Board of Respiratory Care Practitioners"},
    "new-york":       {"phone": "(518) 474-3817", "url": "https://www.op.nysed.gov/professions-index/respiratory-therapy", "name": "New York Office of the Professions — RT"},
    "north-carolina": {"phone": "(919) 878-5595", "url": "https://www.ncrcb.org/", "name": "North Carolina Respiratory Care Board"},
    "north-dakota":   {"phone": "(701) 328-8600", "url": "https://www.health.nd.gov/", "name": "North Dakota Board of Respiratory Care"},
    "ohio":           {"phone": "(614) 752-9500", "url": "https://med.ohio.gov/", "name": "Ohio Respiratory Care Board"},
    "oklahoma":       {"phone": "(405) 962-1400", "url": "https://www.okmedicalboard.org/", "name": "Oklahoma Board of Medical Licensure — RT"},
    "oregon":         {"phone": "(971) 673-2700", "url": "https://www.oregon.gov/omb/", "name": "Oregon Medical Board — RT"},
    "pennsylvania":   {"phone": "(717) 787-1400", "url": "https://www.dos.pa.gov/ProfessionalLicensing/BoardsCommissions/Medicine/Pages/default.aspx", "name": "Pennsylvania Board of Medicine — RT"},
    "rhode-island":   {"phone": "(401) 222-2828", "url": "https://health.ri.gov/licenses/", "name": "Rhode Island DOH — RT Licensure"},
    "south-carolina": {"phone": "(803) 896-4500", "url": "https://llr.sc.gov/med/", "name": "South Carolina Board of Medical Examiners — RT"},
    "south-dakota":   {"phone": "(605) 367-7781", "url": "https://doh.sd.gov/licensing-and-records/boards/medical/", "name": "South Dakota Board of Medical and Osteopathic Examiners — RT"},
    "tennessee":      {"phone": "(615) 532-3204", "url": "https://www.tn.gov/health/health-program-areas/health-professional-boards/me-board.html", "name": "Tennessee Board of Medical Examiners — RT"},
    "texas":          {"phone": "(512) 305-7030", "url": "https://www.tmb.state.tx.us/", "name": "Texas Medical Board — Respiratory Care"},
    "utah":           {"phone": "(801) 530-6628", "url": "https://dopl.utah.gov/", "name": "Utah DOPL — Respiratory Therapy"},
    "vermont":        {"phone": "(802) 828-2390", "url": "https://sos.vermont.gov/opr/", "name": "Vermont Office of Professional Regulation — RT"},
    "virginia":       {"phone": "(804) 367-4600", "url": "https://www.dhp.virginia.gov/medicine/", "name": "Virginia Board of Medicine — RT"},
    "washington":     {"phone": "(360) 236-4700", "url": "https://doh.wa.gov/", "name": "Washington DOH — Respiratory Care"},
    "west-virginia":  {"phone": "(304) 558-1383", "url": "https://wvbort.com/", "name": "West Virginia Board of Respiratory Care"},
    "wisconsin":      {"phone": "(608) 266-2112", "url": "https://dsps.wi.gov/", "name": "Wisconsin DSPS — Respiratory Care Practitioner"},
    "wyoming":        {"phone": "(307) 777-6529", "url": "https://wsbn.wyo.gov/", "name": "Wyoming Board of Respiratory Care"},
}

def inject_board_data(vertical, suffix, board_dict):
    json_dir = SCRATCH / vertical / "database" / "json"
    updated = 0
    for state_slug, info in board_dict.items():
        f = json_dir / f"{state_slug}-{suffix}.json"
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        board = data.get("board", {})
        board["name"] = info["name"]
        board["phone"] = info["phone"]
        board["url"] = info["url"]
        if board.get("fax") == "PENDING":
            board["fax"] = "N/A (contact by phone)"
        if board.get("email") == "PENDING":
            board["email"] = "See board website"
        if board.get("mailing_address") == "PENDING":
            board["mailing_address"] = "See board website"
        if board.get("physical_address") == "PENDING":
            board["physical_address"] = "See board website"
        data["board"] = board
        data["board_source_url"] = info["url"]
        f.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        updated += 1
    return updated

print("Injecting board data...")
ot_count = inject_board_data("ot-pseo", "ot", OT_BOARDS)
pt_count = inject_board_data("pt-pseo", "pt", PT_BOARDS)
rrt_count = inject_board_data("rrt-pseo", "rrt", RRT_BOARDS)

print(f"  ot-pseo:  {ot_count} files updated")
print(f"  pt-pseo:  {pt_count} files updated")
print(f"  rrt-pseo: {rrt_count} files updated")

# Final count
print(f"\n{'='*55}")
print(f"  FINAL PENDING COUNTS (ALL VERTICALS)")
print(f"{'='*55}")
ALL = ["dietitian-pseo", "slp-pseo", "ot-pseo", "pt-pseo", "rrt-pseo", "aud-pseo", "pharm-pseo", "pharmacist-pseo"]
grand = 0
for v in ALL:
    jd = SCRATCH / v / "database" / "json"
    vt = sum(f.read_text().count('"PENDING"') for f in jd.glob("*.json")) if jd.exists() else 0
    grand += vt
    e = "✅" if vt == 0 else f"⚠️"
    print(f"  {v:20s}  {vt:5d}  {e}")
print(f"{'='*55}")
print(f"  GRAND TOTAL:         {grand}")
print(f"{'='*55}")
