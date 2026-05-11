# Heavy Weapons Uncapped (heavy-uncap)

Pine v5, overlay. Comprehensive RVOL toolkit that bundles every heavy-pentagon
RVOL primitive into a single indicator AND adds new functionality not
available elsewhere in the suite:

- **Hybrid RVOL momentum regimes** (5 Long + 2 Short) — pre-configured combo
  of bar-RVOL (Reg @ Time, non-cumulative) × session-RVOL (Cumulative) gated
  by a body-ratio conviction filter. NOT the same as WTC / Hiroshima's
  RVOL @ Reg time calculations.
- **RVOL bar sequences** UU / UUU / UUUU / DD / DDD / DDDD with IPSF per-pair
  thresholds (bar minimum, sequence sum minimum).
- **Back-to-Back RVOL composites** 2x SAAB, 2x Kratos, 2x Bull 1x, 2x Bear 1x,
  plus the mixed B2B Mid Bull / B2B Mid Bear (SAAB+1x / Kratos+1x).
- **Consecutive Displacement streaks** 2+ and 3+ for both directions.
- **HV ladder tiers** 75 / 150 / 250 / 500 / 1000 (mutex — highest tier wins).
- **Hot Spot calendar windows** (OpEx, Quarter-End, Russell rebal, Tax-Loss,
  January Effect, HF Redemption).
- **FAUNA** with full hierarchical label text.

Locally re-implements every heavy-pentagon RVOL root (SAAB / Kratos /
RVOL1x bull/bear / Grand Slam / MOAB / WTC / Hiroshima / Nagasaki) plus the
hvd-pbj-ppd Displacement primitive. **IPSF-asymmetry status**: these local
copies share the same threshold ladders as heavy-pentagon (verified by
inline source inspection of `f_rvol_1x_threshold`, `f_saab_kratos_threshold`,
`f_gs_moab_threshold`, `f_wtc_threshold`, `f_hiroshima_threshold` — same
constants byte-for-byte). Stage 7 byte-diff confirms no drift in the RVOL
ladder; the local copies exist for self-containment, not redefinition.

## Roots (14 truly new)

All `lifecycle_stage=2`. Most `offset=0`; Consec Disp + HV roots use
`offset=-1` per their canonical convention.

### Hybrid Momentum (7)
| Canonical | Default thresholds | Plot |
|---|---|---|
| `heavy-uncap::LONG_1`  | reg≥5.0, cum≥3.0, body≥0.65, bull | labelup belowbar, blue |
| `heavy-uncap::SHORT_1` | same as LONG_1, bear              | labeldown abovebar, red |
| `heavy-uncap::LONG_2`  | reg≥5.0, cum≥3.0, body≥0.65, bull | labelup belowbar, teal |
| `heavy-uncap::SHORT_2` | same as LONG_2, bear              | labeldown abovebar, maroon |
| `heavy-uncap::LONG_3`  | reg≥5.0, cum≥3.0, body≥0.65, bull, long-only | labelup belowbar, purple |
| `heavy-uncap::LONG_4`  | same as LONG_3, long-only         | labelup belowbar, orange |
| `heavy-uncap::LONG_5`  | same as LONG_3, long-only         | labelup belowbar, fuchsia |

All IPSF: `hyb_addReg<n>`, `hyb_addCum<n>`, `hyb_bodyRat<n>` are Anish-tunable
per momentum tier.

### RVOL Sequences (6)
| Canonical | Bars | IPSF defaults |
|---|---|---|
| `heavy-uncap::UU`   | 2 consecutive bullish | bar ≥1.0, sum ≥0.1 |
| `heavy-uncap::UUU`  | 3 consecutive bullish | same defaults |
| `heavy-uncap::UUUU` | 4 consecutive bullish | same defaults |
| `heavy-uncap::DD`   | 2 consecutive bearish | bar ≥1.0, sum ≥0.1 |
| `heavy-uncap::DDD`  | 3 consecutive bearish | same defaults |
| `heavy-uncap::DDDD` | 4 consecutive bearish | same defaults |

Shared upper-cap `seq_th_high=50.0` filters out extreme outliers.

### Calendar (1)
| Canonical | Definition |
|---|---|
| `heavy-uncap::HOT_SPOT` | Bar falls in any of: OpEx (10-17 Mon-Wed), Qtr-end (23-27 of Mar/Jun/Sep/Dec), Russell rebal (Jun 19-24), Tax-loss (Dec 21-26), Jan Effect (Dec 27-30), HF Redemption (May 10-13 or Nov 10-13) |

## Composites (12 new)

### Back-to-Back composites (6)
| Canonical | Composition |
|---|---|
| `heavy-uncap::B2B_2X_SAAB`   | `sigSAAB[1] AND sigSAAB` |
| `heavy-uncap::B2B_2X_KRATOS` | `sigKratos[1] AND sigKratos` |
| `heavy-uncap::B2B_2X_BULL_1X` | `sigBullRVOL1x[1] AND sigBullRVOL1x` |
| `heavy-uncap::B2B_2X_BEAR_1X` | `sigBearRVOL1x[1] AND sigBearRVOL1x` |
| `heavy-uncap::B2B_MID_BULL`  | Mixed SAAB↔BullRVOL1x B2B (with mutual-exclusion guard against 2X variants) |
| `heavy-uncap::B2B_MID_BEAR`  | Mixed Kratos↔BearRVOL1x B2B (with mutual-exclusion guard) |

### Consecutive Displacement (4)
| Canonical | Composition |
|---|---|
| `heavy-uncap::CONSEC_DISP_BULL_2` | `sigDispBull AND streak ≥ 2` |
| `heavy-uncap::CONSEC_DISP_BEAR_2` | `sigDispBear AND streak ≥ 2` |
| `heavy-uncap::CONSEC_DISP_BULL_3` | `sigDispBull AND streak ≥ 3` |
| `heavy-uncap::CONSEC_DISP_BEAR_3` | `sigDispBear AND streak ≥ 3` |

### FAUNA label-based (2)
| Canonical | Composition |
|---|---|
| `heavy-uncap::FAUNA_BULL` | Hierarchical OR over MB/RE/TA + GG/TR/ES/GDR — full label text written to the bar (see ultra-combo for the canonical FAUNA formula; this variant uses different label-text resolution but the same MB/RE/TA/GG/TR/ES/GDR primitives) |
| `heavy-uncap::FAUNA_BEAR` | Mirror |

## Local re-implementations (NOT new roots)

The indicator also locally re-implements every heavy-pentagon RVOL root
(SAAB, Kratos, Bull/Bear RVOL 1x, Grand Slam, MOAB, WTC, Hiroshima, Nagasaki)
and hvd-pbj-ppd's Disp Bull/Bear. These are documented as
`local_reimplementation_of:` notes in the extract YAML so the bible can
warn when a future drift creeps in.

## Why this indicator exists

Per Anish: "this one gives us access to five different long settings, and
it also has the unique, pre-configured relative volume. Not the RVOL at
REG time, so not like the same calculations we do for Hiroshima and WTC,
but it gives us the combinations of the various RVOL, one X, SAAB, and
Grand Slam kind of stuff in one."

The Hybrid RVOL (`bar-RVOL × cumulative-RVOL × body-ratio`) is the unique
ingredient — heavy-pentagon doesn't expose this combination. The 5 Long
tiers let Anish tune 5 independent momentum-pattern detectors against
different conviction levels simultaneously.

## Files

- `versions/HEAVY_UNCAP_v1.pine` — canonical (Pine v5, overlay)

## Bible

- `bible-input/extract-heavy-uncap.yaml` — full extraction (14 roots + 12 composites)
- `docs/lineage/heavy-uncap__*.md` — lineage cards for the composites
- `docs/redundancy.md` — local re-implementations of heavy-pentagon RVOL roots noted

## Branch provenance

Added to `claude/organize-indicators-hierarchy-8JDw1` in Stage 7 alongside
`pb-pbj` and `disp-4x`.
