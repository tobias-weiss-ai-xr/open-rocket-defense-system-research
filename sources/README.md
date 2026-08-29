# Source Materials

> ⚠️ **Audit status: CRITICAL** — the research currently contains ~60 quantitative claims
> with **zero citations**. See [**AUDIT.md**](AUDIT.md) and the claim registry
> [**REFERENCES.csv**](REFERENCES.csv) for what's missing and how we track it.

## Structure

| File | Purpose |
|------|---------|
| `AUDIT.md` | Priority-ordered audit of every claim category and the authoritative sources needed to support it |
| `REFERENCES.csv` | Machine-readable claim registry (claim ID, value, source, status, confidence) — the single tracking point |
| `README.md` | This overview |

## Source Types We Collect

**Primary**
- Government reports (Ukrainian General Staff, US DoD/MDA, German BMVg, Russian MoD)
- Manufacturer specifications (KMW, Rafael, Kongsberg, Diehl, Lockheed, MBDA)
- Military doctrine documents
- Budget documents (US MDA, Ukrainian MoD law)

**Secondary**
- Think tank analyses (CSIS Missile Threat/Defense Project, IISS Military Balance, SIPRI)
- Academic research (journals, RAND, RUSI)
- Expert commentary

**Open Source Intelligence**
- Verified loss/supply trackers (Oryx)
- OSINT flight-path reconstructions
- Ukrainian Air Force daily intercept reports
- Commercial satellite imagery

## Citation Format
APA or Chicago style for all sources. Each claim in `REFERENCES.csv` carries its
source URL + retrieval date once collected.

## Verification Cadence

1. **Start with P1** (threat specs — 11 claims, fastest wins)
2. Each verified claim flips `status` from `UNVERIFIED` → `VERIFIED <date>`
3. Unverifiable estimates stay marked `[estimate]` in the prose
4. The dashboard only labels sourced numbers as "data"
