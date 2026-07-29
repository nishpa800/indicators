# BEDROCK — CHANGELOG

Two separate studies, always (operator order 2026-07-27): **BEDROCK BULL** (BDRB) and
**BEDROCK BEAR** (BDRR). Hardcore forks of FABLE_BULL/BEAR_LTF_v1.5. Registries:
`contracts/bedrock_bull_dp_registry.json` · `contracts/bedrock_bear_dp_registry.json`.
VP spec: `contracts/bedrock_vp_spec.json`. Decisions ledger (CLOSED items are law):
`contracts/bedrock_build_decisions.json`.

## v1.2 — 2026-07-29 — FIRST BAR MASTER BECOMES AN ALERT GATE (BEDROCK BULL v1.2 + BEDROCK BEAR v1.2)

Operator law: *"we need to see the visual plots but if we check the first bar checkbox,
then and only then we ONLY want the alert if the definition of first bar criteria is met
and there will be no other alert fired beyond that first bar definition. its important bc
low time intervals would fire crazily if we dont have this ability."*

**The defect v1.2 closes.** BEDROCK v1.1 *did* carry `★ FIRST BAR MASTER ★` (inherited
from FIRST BAR FABLE), but it gated the **detection** layer — `sig_L = D_L and c(L)` — and
`sig_L` feeds both `fire_L` (the plot) and `alf_L` (the alert). ON therefore erased the
visual plots off the first bar as well as the alerts. There was no way to keep the chart
fully drawn while quieting the alerts, which is exactly what low intervals need.

**The transform** (per lane L, `c(L)` = its reference-bar class ∈ {fb0, fb1, fb01, fbs,
fbm, fb12}; 55 BULL lanes, 54 BEAR lanes):

| | v1.1 | v1.2 |
|---|---|---|
| detection | `sig_L = D_L and c(L)` | `sig_L = D_L` |
| **plot** | `fire_L = en_L and sig_L` | `fire_L = en_L and sig_L` — **ungated** |
| gate | — | `aok_L = sig_L and c(L)` |
| **alert** | `alf_L = al_L and sig_L` | `alf_L = al_L and aok_L` — **gated** |
| alert count | `qn` term `fire_L` | `((en_L and aok_L) ? 1 : 0)` ≡ old `fire_L` |

- **T-A alert invariance** — `alf_new = al ∧ (D ∧ hc) ∧ c = al ∧ (D ∧ c ∧ hc) = alf_old`.
  Alert firing and alert text are bit-identical to v1.1 with the master ON.
- **T-B qn invariance** — `en ∧ aok = en ∧ sig_old = fire_old`, so the `SIDE n` count in
  every alert string is unchanged.
- **T-C plot unconditionality** — `fire_L` carries no `c(L)` term ⇒ ∂fire/∂master = 0.
- **T-D master-OFF identity** — OFF ⇒ `c ≡ true` ⇒ the study is identical to v1.1.
- **T-E alert totality** — every `alf_L` carries a `c(L)` factor. **Closures:** v1.1 left
  four lanes alert-ungated — `qS20`/`qS21` (b2bFC, a two-bar back-to-back → assigned
  `fb01`, the FBF law "the pair touches the first bar") and `qS32`/`qS33` (OPEN1 →
  assigned `fb0`, a provable no-op since `det_open1*` already requires `is_new_sess`).
  With the master ON, no alert of any kind now fires outside the first-bar definition.

**First-bar definition — unchanged, and NOT redefined here.** BEDROCK keeps the
estate-canonical `bool is_new_day = ta.change(time("D")) != 0` / `is_new_sess =
is_new_day`, byte-identical to FIRST BAR FABLE v3 / EXT v6 and SECONDS v1 (B2B PUP's
`session.isfirstbar` is the same boundary).

**Master input** retitled `★ FIRST BAR MASTER — ALERTS ONLY ★`, default **ON** (unchanged
default: alert behaviour matches today; the plots are what newly appear on every bar).

**Plot budget unchanged** — not one `plotshape` line was touched; each already read
`fire_L`, which is now first-bar-independent. Graphic-object disclosure (L-61): **zero**
`label.new`/`line.new`/`box.new`/`table.*`/`polyline.new` sites added; every VP remains a
real plot.

Gates: `validation/wrappers/bedrock_firstbar_alert_gate.py` → **D_bdrfb = 0 PROVED**,
anti-fixture battery **5/5 CAUGHT**; W-INDSTUDY manifests
`validation/indstudy/manifest_bedrock-{bull,bear}_v1.2.json` (declared-edits-only,
rebuild byte-compare D=0).

## v1.1 — 2026-07-28 — THE ERROR-WAVE FIX (BEDROCK BEAR v1.1 + BEDROCK BULL v1.1)

Operator witnessed ~20 TradingView errors per study on v1.0 ("I cannot take all the
pictures"). Root causes, fixed in both files via W-INDSTUDY manifests
(`validation/indstudy/manifest_bedrock-{bear,bull}_v1.1.json`, gate PROVED):

- **R1 (the error wall):** the HARDCORE-GATE engine block moved from :159 to after
  `det_PBJRSRC` — v1.0 inserted it before its dependencies (`d9_*` :292, `sigPBJ/PB`
  :452, `sigFAUNA*` :561, `det_kcRS/RC` :2306), so TradingView reported an
  undeclared-identifier per reference (gate measured 15-17 order violations per file).
- **R2:** killed lanes per operator decisions D-04/D-13/D-14 (CO: HV+D+PB+USE,
  CO: HV+D+PBJ+USE, ENR Same-Bar/TNT-1st) fully excised — v1.0 removed only the sig_
  definitions and left dangling `fire_/alf_` defs, `qn` terms, inputs and alert rows
  (25 residue sites per file). Every removal is a visible `CUT##` comment.
- **R3:** back-pocket lanes (D-05 `qB2BP`, D-06 `qPBR`) + `qPJR` keep their sig_
  definitions but lose every input/alert surface (slim-alert law: nothing alert-only).
- **R4 (BEAR):** BDRR-21 plot text wore the BULL literal `1X/GS` — the L-63
  founding-exhibit defect re-imported — now `1X/MOAB`.
- **R5 (BULL):** BDRB-24 Whale+PUP Bull wore Musashi's gold `c_mu_bull` — new
  `c_wh_bull` (#1E88E5).
- **R6:** `en_aggAlerts` tooltip made honest (per-lane OFF mode for inherited lanes no
  longer exists; BEDROCK lanes 01-18 always alert per-lane).
- Registry hygiene: BEAR registry lane ids carried the BULL prefix (BDRB-*) — corrected
  to BDRR-*; BDRR-21 text + BDRB-24 color corrected in `bedrock_vp_spec.json`.

Acceptance: `validation/wrappers/bedrock_v11_gate.py` D_bdr=0 both sides (9 axes:
declaration-order, kill-residue, back-pocket, alert↔plot cross-ref, spec parity,
budget, block integrity, L-63 string ban, stamping) · anti-fixture battery 6/6
(`validation/anti_fixtures/af_bedrock_v11_gate.py`) · `pane_label_gate` D_cs1=0 both ·
`indicator_study_gate` PROVED both. Budget: BEAR 54/64 · BULL 55/64 · alertcondition 0.
Graphic-object disclosure: 2 inherited GZ-FVG `line.new` decoration sites per study,
zero `label.new`, zero pane labels.

Adversarial verification wave (6 independent skeptics, 2 files × 3 lenses — compile /
decisions / render-truth; compile lens CLEAN both files) surfaced and the same wave fixed:

- **R8 (D-16, behavioral):** the NAKED lanes (BDRR/BDRB-09/10) omitted the mandatory
  directional conjunct — `BDR_DIR` added; no lane anywhere in either study can fire on a
  non-directional bar.
- **R9 (D-11):** the banned word appeared in the header comment and an operator-visible
  tooltip ("Bearish mirror.") — both reworded, zero occurrences remain.
- **R10 (D-04/D-13/D-14 doctrine):** zero-dependent dead layers excised — `co_*_v7` ×4,
  `coQ_bull/bear`, `det_S26/det_S27` ("otherwise the engine goes too").
- **R11 (D-09):** `kc_*ThrEff` ternaries collapsed — the ATR-x path is the only path.
- **R12 (D-15/side-truth):** BULL `en_/al_qS15` rows retitled "Nagasaki (any bar)" (the
  settings pane still claimed FIRST BAR after the constraint was removed); the
  "Grand Slam (MOAB)" tooltip gloss made side-correct in both files; stale S26/S27
  tooltip reference replaced.
- **Adjudicated, retained, disclosed:** `co_*`/`enrB2B_*` base engines stay inside the
  `any_BULL/any_BEAR` baskets — those baskets are definitionally "ANY FABLE" and the
  nine "+ANY FABLE" composite lanes would lie about their own names if FABLE detections
  were removed from them. The FIRST BAR master toggle (default ON, inherited) still
  gates all lanes including Nagasaki; D-15's baked per-lane constraint is gone — the
  master is a user switch, not a baked conjunct.

Tick-friendly twins: dated pair debt (due 2026-07-30) in `INDSTUDY_DEBTS.json` (L-49.1).

## v1.0 — 2026-07-28 — first build (SUPERSEDED by v1.1)

Generated by `scripts/ind/build_bedrock_v1_1.py`'s predecessor (`build_bedrock_v1.py`)
from FABLE_BULL/BEAR_LTF_v1.5: hardcore gate (ANCHOR · R-C · R-S · DIRECTIONAL ·
FAUNA|DISPLACEMENT), 18 BEDROCK lanes + gated inherited lanes, BAND LAW v2 plots,
per-lane dynamic alerts. Shipped with the error wave fixed by v1.1 — do not paste v1.0.
