# Sources Audit — What's Missing

**Status: IN PROGRESS — 13 of 36 claims verified (36%), 0% when this audit started**

Last update: **2026-08-29** — P1 threat specs verified (see [VERIFIED-2026-08-29.md](VERIFIED-2026-08-29.md))

This audit maps every quantitative claim in the research to the authoritative source(s)
needed to support it. Until a claim is verified, treat it as **hypothesis, not verified analysis**.

---

## Why This Matters

The repo currently makes specific, decision-grade claims (missile specs, unit costs,
intercept rates, system effectiveness) with **no references anywhere** — no URLs, DOIs,
or footnotes. For a topic affecting real procurement and lives, unsourced numbers are
worse than no numbers: they carry the *appearance* of evidence.

This audit is a checklist, not a solved list. Collecting these sources is an open task.

---

## ✅ Verification Progress

| Priority | Status | Claims verified |
|----------|--------|-----------------|
| **P1** threat specs | 🟢 DONE 2026-08-29 | 13/16 (THR-01..15; 3 not verifiable publicly — unit costs, casualties) |
| P2 system cost/effectiveness | ⏳ open | 0 |
| P3 Kinzhal intercepts | ⏳ open | 0 |
| P4 defense economics | ⏳ open | 0 |
| P5 Monte Carlo params | ⏳ open | 0 |

**7 corrections applied to the repo on 2026-08-29** (Kinzhal range/warhead, Iskander
payload, Kalibr speed+warhead, Kh-101 range/warhead, Shahed cost). The headline "133:1"
asymmetry was retired — verified range is ~20:1 to ~80:1 depending on Shahed cost scenario.

---

## Priority 1 — Threat specifications (highest visibility, most cited downstream)

Every number here feeds cost-effectiveness math and the Monte Carlo simulation.

| Claim | Used in | Authoritative source to collect |
|-------|---------|--------------------------------|
| Kinzhal Mach 10, 2,000–2,500 km range, 400–500 kg warhead, ~$10–15M cost | `ukraine-missile-defense-analysis.md §1.1`, `data/threat-profiles.json` | Russian MoD releases; CSIS Missile Threat project (missilethreat.csis.org); IISS *Military Balance*; open-source flight-path reconstructions (resident/OSINT trackers) |
| Iskander Mach 6–7, 500 km, $5–7M, 500 kg | §1.2, `threat-profiles.json` | CSIS Missile Threat; Missile Defense Advocacy Alliance fact sheets; IISS |
| Kalibr Mach 2.5–3, 1,500–2,500 km, $3–5M | §1.3, `threat-profiles.json` | CSIS Missile Threat; Russian Navy doctrine docs; SIPRI arms transfers |
| Kh-101/Kh-555 subsonic, 3,000–5,500 km, $2–3M | §1.4 | CSIS Missile Threat; manufacturer (Raduga) datasheets; IISS |
| Shahed-136 ~185 km/h, 1,000–2,000 km, $20–50K | §1.6, `threat-profiles.json` | HESA/Iranian UAV documentation; Ukrainian General Staff daily reports; conflict-monitoring databases (e.g., Ukraine Weapons Tracker / Artur Rehi) |
| Casualties per unanswered Kinzhal (~100 avg in simulation) | `monte_carlo_defense_analysis.py` | Ukrainian General Staff casualty reporting; UN OHCHR verified-civilian-casualty data; Amnesty/Human Rights Watch field reports — **none of these currently cited** |

**Actions:**
- [ ] Collect one authoritative source per missile family (CSIS Missile Threat page is the fastest, most citable per-system source)
- [ ] Note where open-source estimates *disagree* (e.g., Shahed range varies 1,000–2,500 km by source) — record range of estimates, not single values
- [ ] Link each `threat-profiles.json` entry to its source record

---

## Priority 2 — System cost & effectiveness claims (the $ table)

These are the headline numbers and currently have the **highest risk of stale or wrong values**.

| Claim | Used in | Authoritative source to collect |
|-------|---------|--------------------------------|
| Patriot battery ~$1.5B; PAC-3 MSE interceptor $4M/shot; $400K–1M/engagement | `ukraine-missile-defense-analysis.md §2`, cost tables | US DoD FY budget documents (Missile Defense Agency); Lockheed Martin PAC-3 data; CSIS Missile Defense Project cost pages; US Army solicitations |
| Gepard ~$1,000/engagement, 4 km, bought by Germany for Ukraine | system tables | German MoD press releases (BMVg); donation-trackers; manufacturer (KMW/Flensburger) specs; Oryx procurement data |
| Iron Dome ~$50K/interceptor | system tables | Rafael fact sheets; Israeli Ministry of Defense; CSIS/CRS reports on Iron Dome |
| NASAMS, IRIS-T SLM range/cost | `ukraine-missile-defense-analysis.md` alternatives | KDA (Kongsberg)/Diego Defense datasheets; German MoD; IISS |
| C-RAM $750/engagement, ZU-23-2 $200/engagement, EW $10/engagement | layered-defense tables | US Army C-RAM program docs; Oryx verified supply lists; International Institute for Strategic Studies (IISS) assessments of munitions costs; open-source per-round ammo prices (e.g., 23mm vs Stinger) |
| HELIOS/Iron Beam/PHaL/Ukrainian laser power & cost figures | `open-rocket-defense-systems.md` laser table | US Navy HELIOS program info (PEO IWS); Rafael Iron Beam disclosures; German MBDA PHaL press; Ukrainian MoD announced 50 kW laser claims (2024–2025) |

**Actions:**
- [ ] Add primary-source cost anchor per system (manufacturer, MoD, or budget doc)
- [ ] Split "per-engagement" cost into ammunition + system amortization, each sourced
- [ ] Mark estimates that are informed guesses (no public source exists) explicitly as **[estimate]**

---

## Priority 3 — Kinzhal intercept claims (contested, must be sourced carefully)

| Claim | Used in | Authoritative source to collect |
|-------|---------|--------------------------------|
| "Patriot limited effectiveness vs Kinzhal; only a few confirmed intercepts" | §1.1, Kinzhal deep-dive | Ukrainian Air Force Command postings; US official statements (Pentagon transcriptions); open-source intercept video/VBIED analyses; **note reporting disputes** |
| 30-second engagement window after detection | Kinzhal analysis | System-response-time math (documented derivation), sensor cueing specs (radar detection ranges) — publicly citable from radar datasheets, not a single report |
| Shelters save 90%+ lives with early warning | recommendations | UN OHCHR casualty data; civil-defense effectiveness literature (e.g., Israeli Home Front Command shelter studies); **this claim needs real evacuation/coverage data** |

**Action:** Document the Patron/Air-Force intercept claims with dated public statements — this is the most politically charged number in the repo.

---

## Priority 4 — Defense-economics claims (secondary but still sourceable)

| Claim | Source to collect |
|-------|-------------------|
| Ukraine defense budget ~$40B context | Ukrainian MoD budget law; SIPRI military expenditure database |
| 133:1 cost asymmetry (Patriot $4M vs Shahed $30K) | Derived from sourced unit costs (P1/P2) — not a standalone source |
| 82% savings vs Patriot-only | **Derivation must cite** the Patriot-only cost model (P2) + system costs; it is internally computed, not an external fact |

---

## Priority 5 — Monte Carlo simulation parameters (currently ALL unsourced)

Every distribution in `scripts/monte_carlo_defense_analysis.py` is a judgment call.
The dashboard headlines depend on them, so they must be traceable:

| Parameter | Value(s) | Needs source |
|-----------|----------|--------------|
| Sensor node cost $100K–1M | Triangular | Commercial radar/EO-IR/EW pricing catalogs; comparable deployed sensor programs |
| Interceptor node $2M–10M | Triangular | Missile/launcher unit costs from P2 |
| AI dev $50M–300M | Triangular | Comparable defense-software programs (e.g., Maven, AFRL autonomy budgets) |
| Daily Kinzhal rate (median 50) | Log-normal | Ukrainian Air Force daily intercept summaries; strike-frequency dashboards |
| Network availability beta(8,2) ≈ 72–80% | Beta | Comms-resilience literature; similar mesh-network field studies — **currently an assumption** |
| Patriot baseline 0.4 hit rate | Constant | P3 intercept claims |

**Action:** Add a `sources/REFERENCES.csv` with columns: claim_id, claim, value, source_url/doi, source_org, date, confidence. Reference it from the simulation script header.

---

## Recommended source inventory (organizations & publication types to draw from)

These are the real, verifiable institutions whose publications should populate the audit.
**Do not treat this list as a citation list itself — it is a hunt list.**

- **CSIS Missile Threat** — per-system fact pages (Kinzhal, Iskander, Kalibr, Shahed)
- **IISS — The Military Balance** — annual force/equipment data
- **SIPRI** — military expenditure & arms transfer databases
- **Ukrainian General Staff / Air Force Command** — daily threat & intercept reports
- **UN OHCHR** — verified civilian casualty figures (Ukraine)
- **Oryx / open-source trackers** — verified equipment supply/loss lists
- **US DoD / MDA budget documents** — Patriot & interceptor costs
- **Manufacturer datasheets** — KMW (Gepard), Rafael (Iron Dome/Iron Beam), Kongsberg (NASAMS), Diehl (IRIS-T), Lockheed (PAC-3)
- **German BMVg (MoD)** — Ukraine support package lists with system values
- **CSIS Missile Defense Project** — cost-per-shot & battery cost analyses

---

## Process going forward

1. Each claim gets an ID like `THR-01`, `COST-07`, `PERF-03`.
2. Claim IDs are quoted next to the claim in the prose (e.g., `(THR-01)`).
3. Claim details live in `sources/REFERENCES.csv` (one row per claim-source pair).
4. The Monte Carlo script prints which claim IDs back its assumptions.
5. Only 100%-verified claims show in the dashboard as "data"; unverified stay labeled [estimate].

**Current state:** 13/36 claims verified (36%). P1 threat specs complete — every missile-range/warhead/speed figure in the repo now carries a CSIS or Wikipedia/primary-URL citation with retrieval date. First milestone of P1 achieved 2026-08-29; next milestone is P2 (system costs).
