# HVD+PBJ+PPD — Cross-agent delta table

_Compiled 2026-05-11 from 4 parallel audit agents (one per Pine version).
Source reports in `bible-input/agent-reports/hvd-pbj-ppd-delta-*.md`.
Source ports in `python_ports/hvd_pbj_ppd/`._

## Audit roster (4 parallel agents)

| Pine file | Lines | Agent's delta report | Python port | Detections / Stubbed |
|---|---|---|---|---|
| `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | 1767 | `hvd-pbj-ppd-delta-the-only-one.md` | `the_only_one.py` | **59 / 6** |
| `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | 1939 | `hvd-pbj-ppd-delta-4-26-1244am.md` | `v_4_26_1244am.py` | **74 / 42** |
| `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | 1939 | `hvd-pbj-ppd-delta-1939-masterdir.md` | `v_1939_masterdir.py` | **15 / 104** |
| `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | 2246 | `hvd-pbj-ppd-delta-2246-masterdir.md` | `v_2246_masterdir.py` | **37 / 74** |

Note: detection-vs-stub counts vary because agents used different
boundaries for "what counts as a detection" — counts converge once
identifier sets are aligned. The 1939 agent stubbed aggressively
because it found extensive shared engine code.

## Lineage map

```
THE_ONLY_ONE.pine (1767L) ←─ separate fork; smaller; flat UU body; same-bar csNew3
       │
       ├── (predecessor connection unclear; THE_ONLY_ONE filename
       │     declares it canonical but the body is structurally simpler
       │     than its 1939 contemporaries)

MASTERDIR LINEAGE (near-twin family):
  4.26.1244am.pine (1939L)  ←──┐
                                │  10 diff hunks, ALL IPSF default flips
  1939_FROM_MASTERDIR (1939L) ←─┘  (SD-003: NOT real drift)
                                │
                                │  +307 lines = alert/aggregator wiring only
                                │  + 1 CMB-leg offset drift (HVDM cascade)
                                │  No unique detection plots
                                ↓
  2246_FROM_MASTERDIR (2246L) ─── superset of 1939_FROM_MASTERDIR
```

**Conclusion**: 4 files reduce to 2 distinct semantic lineages —
THE_ONLY_ONE (separate, simpler) and MASTERDIR (4.26 ≡ 1939, with 2246
as the alert-enriched superset).

## REAL drift findings (cross-confirmed by ≥2 agents, NOT IPSF defaults per SD-003)

| # | Detection plot(s) | THE_ONLY_ONE | MASTERDIR (4.26 / 1939 / 2246) | Drift kind | Agents reporting |
|---|---|---|---|---|---|
| 1 | `csNew3_Bull` / `csNew3_Bear` | `csNew1 AND csNew2` (SAME-BAR) | `csNew1 AND nz(csNew2[1])` (LAGGED) | semantic-drift / offset | THE_ONLY_ONE, 4.26, 1939 |
| 2 | `sigDispConsBull2/Bear2` and `Bull3/Bear3` | `current FAUNA AND [1] FAUNA` (and `[2]` for 3-bar) | `[1] FAUNA AND [2] FAUNA` (and `[3]` for 3-bar) | semantic-drift / offset shift | THE_ONLY_ONE, 4.26, 1939, 2246 (4-of-4) |
| 3 | `sigAlphaStrikeBull` / `sigAlphaStrikeBear` | `(sigBullPBJ or sigBullPB)` accepted | `sigBullPBJ` only (4.26 + 1939); 2246 adds `sessionBarCount<=od_max_bars` AND `as_disp_bull` gates | semantic-drift / inclusion + extra gates | THE_ONLY_ONE, 4.26, 1939, 2246 |
| 4 | `as_fauna_bull` / `as_fauna_bear` (helper of AlphaStrike) | OR-set: FAUNA, Long1, DISP, PUP, WTC, Hiroshima, Nagasaki | 4.26+1939: adds `hvd_fire_bull` to OR; 2246: drops `sigDISPBull` (split out as separate AND), adds `sigNagPlusBull` to OR | semantic-drift / inclusion | THE_ONLY_ONE, 4.26, 1939, 2246 |
| 5 | `cc_bull_active` / `cc_bear_active` | Reset/sustain on `comboSet3 OR comboSet4` only | Reset/sustain on `comboSet1 OR comboSet2 OR comboSet3 OR comboSet4` (all 4) | internal-helper drift | 1939, (THE_ONLY_ONE confirmed indirectly) |
| 6 | UU family: `sigP21BullUUUU`/`UUU` + `sigUUBull` (and bear mirrors) | Flat 4-AND/3-AND chain using `u4_*`/`u3_*`/`uu_*` accumulators + `excA`/`excC` | Path-A..F decision body via `f_uu_bull_scan(_n)` 9-tuple + `_ok = tfSec>120 OR (sum>=th_saab_kratos AND (sum>=th_1x OR _p))` gating | semantic-drift / different boolean definition + hardcoded TF + RVOL thresholds | THE_ONLY_ONE, 4.26, 1939 |
| 6b | UU family (further drift inside MASTERDIR) | (n/a) | 4.26+1939: path-A..F. **2246: path-A..H + `_sub2min_pass` and `_gate` filtering.** | semantic-drift inside masterdir lineage | 4.26, 1939, 2246 |
| 7 | `use_any_bull` / `use_any_bear` (Pipeline D consumer) | References strict `sigP21Bull*` / `sigUSubBull` (which exists here) | References `_indep` variants (don't exist in THE_ONLY_ONE) AND `sigOmegaLongA` (doesn't exist in THE_ONLY_ONE) AND drops `sigUSubBull` | semantic-drift / inclusion | THE_ONLY_ONE, 4.26, 1939 |
| 8 | HVDM CMB component (HVDM 2-of-3 / 3-of-3 cascade) | uses `csNew3_Bull` (current bar) | 4.26+1939: uses `csNew3_Bull` (current bar). **2246: uses `nz(csNew3_Bull[1])` (1-bar lag on CMB leg)** | semantic-drift / offset (2246 only) | 2246 |
| 9 | Fire wrappers: `fire_*` plotshape booleans | No `masterGate` wrapper | 4.26+1939: every `fire_*` adds `... and masterGate`; many also add `floor_gated`, `floor2_gated`, `uu_gated_bull` extra AND-of-many gates | semantic-drift / extra gates | 1939, 4.26 |
| 10 | `sigOmegaLongA` (and bear) | DOES NOT EXIST | EXISTS as a tighter Omega variant using `omega_cosignal_A` | feature-presence drift | THE_ONLY_ONE (by absence), 4.26, 1939 |
| 11 | `sigNagPlusBull` / `sigNagPlusBear` | DOES NOT EXIST | EXISTS in 4.26 + 1939 + 2246 | feature-presence drift | THE_ONLY_ONE (by absence), 4.26, 1939, 2246 |
| 12 | `sigUSubBull` / `sigDSubBear` | EXISTS | DOES NOT EXIST | feature-presence drift (THE_ONLY_ONE only) | THE_ONLY_ONE, 4.26 |

## Skipped (per SD-003 — IPSF defaults are not drift)

The 4.26 vs 1939 byte-near-twin check identified 10 diff hunks. Every
single hunk was an IPSF default flip:

- `input.bool` defval `false` → `true` (mostly toggle defaults for
  optional gates)
- `i_std_min` 6.0 → 4.5 (DISP σ-mult default)
- `i_disp3_std_min` 4.0 → 3.0 (DISP 3-bar variant)
- Momentum reg/cum floors lowered
- Body% defaults lowered
- `p21_pbj_dist` 1 → 4

These are NOT drift. They are user-tunable in TradingView settings. The
two files are SEMANTICALLY EQUIVALENT.

## Lineage interpretation

The "MASTERDIR" pair (4.26 + 1939) appears to be the same source
checked in twice with different IPSF defaults — likely an editorial
artifact (one captured with defaults set for one symbol class, the
other with defaults set for another). 2246 is a forward-evolution of
that same source with:

- Additional alert/aggregator wiring (the +307 lines, no new detections)
- One CMB-leg offset drift (HVDM cascade lag added)
- UU family path-G + path-H additions (`_sub2min_pass`, `_gate`
  refinements)

THE_ONLY_ONE filename declares canonicality but its body is
structurally simpler — it has FEWER operands, FEWER gates, FEWER
features (no NagPlus, no OmegaA), and uses SAME-BAR csNew3. This
suggests THE_ONLY_ONE is either:

(a) An intentional simplification — Anish or a prior consolidation pass
    deliberately stripped complexity, OR
(b) A reset that lost features that were in MASTERDIR

Without TV firing on both (THE_ONLY_ONE vs MASTERDIR-2246) on the same
chart, the bible cannot decide which is the "right" canonical. Anish's
domain knowledge resolves.

## Arbitrations queued for `PO::hvd-pbj-ppd::*` (when hired)

When the Plot Owner agents for this family are spun up, they own these
canonical decisions:

1. **csNew3 same-bar vs lagged AND** — already queued at PO::unified-combo
   level (cross-family). If PO::unified-combo decides LAGGED is canonical,
   `THE_ONLY_ONE` needs a same-bar variant Python port preserved alongside.
2. **sigDispCons FAUNA shift** — 1-bar systemic offset across all 4
   files. PO::hvd-pbj-ppd::* decides whether the canonical is current+[1]
   (THE_ONLY_ONE) or [1]+[2] (MASTERDIR). Implications for what bar the
   confluence claims to "fire on."
3. **sigAlphaStrike inclusion** — PBJ-or-PB (THE_ONLY_ONE, more permissive)
   vs PBJ-only (MASTERDIR, stricter). Per SD-001 reasoning ("always
   include"), the more permissive THE_ONLY_ONE form may be the canonical;
   PO::hvd-pbj-ppd::* decides.
4. **as_fauna OR-set** — three-way divergence. PO::hvd-pbj-ppd::* picks
   the canonical OR-set; the other two become acknowledged variants.
5. **cc_bull_active reset breadth** — narrow (THE_ONLY_ONE: comboSet3+4
   only) vs broad (MASTERDIR: all 4 comboSets). Affects how often the
   chain "stays alive" in a session. TV firing required.
6. **UU engine** — 3 distinct semantic groups: flat (THE_ONLY_ONE),
   path-A..F (4.26+1939), path-A..H+gates (2246). PO::hvd-pbj-ppd::*
   decides; non-canonical variants kept as parallel ports.
7. **2246 CMB lag** — single-file outlier. Likely intentional (the +1
   lag on CMB lets HVDM cascade "wait" for csNew3 confirmation). Confirm
   intentional, then either propagate to all files or document as 2246
   variant.

## What this changes in the bible

- `bible-input/MANIFEST.md` should reflect 2 lineages (THE_ONLY_ONE,
  MASTERDIR), not 4 distinct files. (Edit deferred until PO::hvd-pbj-ppd::*
  decides which lineage is canonical.)
- `docs/redundancy.md` (b) gets an HVD+PBJ+PPD entry for the 12 REAL
  drifts above. (Edit deferred until PO::hvd-pbj-ppd::* arbitrates so
  the entry can also state the canonical resolution.)
- `data/indicators.yaml` `hvd-pbj-ppd` family section should mark
  `4.26.1244am` and `1939_masterdir` as SEMANTICALLY EQUIVALENT (same
  body, IPSF default twins). (Edit pending.)

## What this changes in the Python ports

All 4 ports are committed. Each is a FAITHFUL translation of its source
.pine — none has been "canonicalized" yet. When PO::hvd-pbj-ppd::*
arbitrates, a new `hvd_pbj_ppd_canonical_pentagon_included.py` port will
be written that picks per-decision the canonical operand set, preserving
the 4 source-fidelity ports under the new-version-only rule (SD-002).

## Stage-7 followups

- [ ] Run `detection-plot-tv-firing` on a same-chart comparison of
      THE_ONLY_ONE vs MASTERDIR-2246 to surface fire-bar agreement on the
      6 high-impact drifts
- [ ] PO::hvd-pbj-ppd::bull + PO::hvd-pbj-ppd::bear hiring (per
      ARCHITECTURE.md Tier-A roster)
- [ ] Author the canonical port once arbitrations land
- [ ] Update bible YAML to reflect lineage resolution
