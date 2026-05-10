# Roots Catalog — master across all indicators

Every named primitive that the indicator suite refers to by name. The bible STOPS at this level — internal mechanics (Supertrend, Zoo MA, EMA crosses, ATR/σ multipliers, raw `highest()`/`lowest()`, `barstate.*`, `request.security`, raw FVG geometry) are deliberately hidden inside root names and never decomposed here. See `docs/glossary.md` for cross-cutting terms.

Schema-of-record: `data/indicators.yaml`. This file is the human-readable view.

---

## Family: Push (Pocket Pivot)

### `pocket-pivot::PUP`

- **Plain English:** Bullish Pocket Pivot — a bar with body % up-move ≥ `pp_barSize` AND volume exceeds the highest red-candle volume over the last `pp_lookback` bars.
- **Parameters:** `pp_barSize=3.0%`, `pp_lookback=10`.
- **Canonical owner:** `anish-50-1st-combo` (oldest in-repo definition site).
- **Aliases:** `sPPBull` (anish-50-1st-combo, ultra-combo), `det_PUP` (b2b-pup), `sigPUP` (hvdpbjppd, squarify), `u5_PUP` (tnt-od).
- **Plot offset:** 0.
- **Lifecycle stage:** 2 (independent root calculation).
- **Decoupling:** single-bar boolean; no other named signals.
- **Used by composites:** `anish::ALL_THREE_BULL`, `SUPER_PUP`, `TB_SELL`, `FOSTER_BUY`; `b2b-pup::B2B_PUP`, every `S1`-`S20` numbered composite; `hvdpbjppd::USE_ANY_BULL` (via composites); `squarify::S1`-`S46` (via PUP-using composites); `tnt-od::CATALYST`, `CONT_BULL`; `ultra-combo::THREE_BAR_BULL`, `OPENER_BULL`, `MEGA_BULL`, `SUPER_B2B_DAYS_BULL`.

### `pocket-pivot::PPD`

Symmetric bear mirror of PUP. Same parameters. Aliases: `sPPBear`, `det_PPD`, `sigPPD`, `u5_PPD`. Used by all `*_BEAR` mirrors of composites listed above.

---

## Family: Regime (Anish Stage 2/4)

### `anish-stage::BULL_PASS`

- **Plain English:** Stage 2 uptrend regime: price stacked above ordered 50/150/200 EMA cascade with 200 EMA rising vs ~1 month ago AND price within band of 52-week range. Treated as a single named root (despite EMA-stack internals) because humans refer to "Anish Bull Pass" as one named thing.
- **Parameters:** EMA 50/150/200 hardcoded, 21-bar slope lookback, 252-bar 52w H/L, bull-band high 1.30 / low 0.75.
- **Canonical owner:** `anish-50-1st-combo` (a dedicated Anish-Stage indicator may exist outside the repo; if so, reclassify provenance).
- **Aliases:** `bullPass`.
- **Plot offset:** 0.
- **Used by:** `anish::ALL_THREE_BULL`, `SUPER_PUP`, `TB_SELL`, `FOSTER_BUY`; `ultra-combo::OPENER_BULL` (via 1stPUP path), `THREE_BAR_BULL` (via TB/Foster gating), `MEGA_BULL` (via Super), `SUPER_B2B_DAYS_BULL`.
- **Classification note:** TENTATIVE root. Stage-1 review may reclassify to composite-of-EMA-crosses if a canonical Anish-Stage indicator surfaces.

### `anish-stage::BEAR_PASS`

Symmetric mirror. Bear bands 0.70/1.25.

---

## Family: Zoo Pipeline (PBJ / PB)

### `hvdpbjppd::PBJ_BULL`

- **Plain English:** Bullish landing zone — Zoo MA + Supertrend cross confirmed by PB&J wick filter (price wick beyond `EMA(close, MA_period) ± ATR × ATR_mult` band at lookback extreme with above-avg volume).
- **Parameters:** `zoo_ma_type=VWMA`, `zoo_ma_len=5`, MA period=20, ATR period=14, HH/LL=25, ATR mult=3.0, vol period=20, vol mult=0.1, ST period=10, ST mult=2.0.
- **Canonical owner:** `hvdpbjppd` (`HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`).
- **Aliases:** `det_PBJBull`, `sigBullPBJ`, `u5_PBJBull`.
- **Plot offset:** 0.
- **Used by:** `hvdpbjppd::FLOOR_BULL`, `2F`, `HW_BULL`, `SUPER_BULL`, `SDUPER_BULL`, `B2B_HVD_PBJ_BULL`, `CO_BULL_PBJ`, `LSC_BULL`, `Combo Chain`, `Alpha Strike`, `OD_BULL`; `b2b-pup::S6_BULL` (PBJ leg); `squarify::S3_HW_BULL`, `S14_PBJ_F2_E3`, `S15_PBJ_CL`, `S22_NPM_PLUS`, `S27_CO_BULL`, `S28_HVD_PBJ`, `S32_GRAIL_BULL`, `S34_NPM_PBJ_PUP`; `tnt-od::PBJ+NPM`, `PBJ+TNT`, `PBJ+RET ENR`; `ultra-combo::comboPBJ_F2`, `comboPBJ_E3`, `comboPBJ_CLUSTER`, `THREE_BAR_BULL`, `MEGA_BULL` (via Super), TB transition (PBJ-leg).
- **Internal mechanics warning:** Supertrend / VWMA / EMA crosses inside PBJ may have drifted across indicators. Stage 6 byte-diff required.

### `hvdpbjppd::PBJ_BEAR`

Symmetric mirror.

### `hvdpbjppd::PB_BULL`

- **Plain English:** Pullback (non-PBJ Zoo branch) — cross-after-approach of bull-lander level created by the PBJ engine; only fires if PBJ did not fire on the same Zoo cross.
- **Mutex with:** `PBJ_BULL` on the same Zoo cross.
- **Aliases:** `det_PBBull`, `sigBullPB`.
- **Used by:** `hvdpbjppd::2F`, `Penthouse` (bear), `Alpha Strike`, `OD_BULL` variant, `LSC_BULL`; `squarify::S5_2F`, `S29_B2BHVD_PBJ` (via b2b_bull_pb); `tnt-od::PB+ENRICHED` family.

### `hvdpbjppd::PB_BEAR`

Symmetric mirror.

---

## Family: Volume + Displacement (HV+D)

### `hvdpbjppd::HVD_BULL`

- **Plain English:** Volume-rank hit (any of 50/75/100/150/250/500/1000-bar volume highest, OR HEV all-time-high, OR HTF1/HTF2 ranks) co-occurring with stdev-displacement candle that opens a bull FVG.
- **Parameters:** `d1_type="Open to Close"`, `d1_len=100`, `d1_mult=5.0`, `d2_mult=2.5` (HTF1, was 4.0 in predecessor), `d3_mult=1.5` (HTF2, was 2.5), `h1On=false` (was true), `h2On=false` (was true). Lookback enables ub50/75/100/150/250/500/1000 default true; useHEV default true.
- **Canonical owner:** `hvdpbjppd::THE_ONLY_ONE`.
- **Aliases:** `det_HVDBull`, `hvd_fire_bull`.
- **Plot offset:** -1.
- **Used by:** `hvdpbjppd::HVD_PB_BULL`, `HVD_PBJ_BULL`, `B2B_HVD_BULL`, `B2B_HVD_PBJ_BULL`, `B2B_HVD_PB_BULL`, `CO_BULL_PBJ`, `CO_BULL_PB`; `squarify::S27_CO_BULL`, `S28_HVD_PBJ`, `S29_B2BHVD_PBJ`, `S30_B2BHVD`, `S36_UU_HVD`; `b2b-pup::S3_BULL` (HVD leg).

### `hvdpbjppd::HVD_BEAR`

Symmetric mirror.

---

## Family: Displacement (USE)

### `hvdpbjppd::DISP_BULL`

- **Plain English:** USE-Displacement — range > N×stdev in `[i_std_min, i_std_max]` band, with bull FVG when Require FVG ON.
- **Parameters:** `i_disp_type="Open to Close"`, `i_std_len=100`, `i_std_min=3.0` (was 6.0 in predecessor), `i_std_max=100.0`, `i_req_fvg=true`.
- **Canonical owner:** `hvdpbjppd::THE_ONLY_ONE`.
- **Aliases:** `det_DISPBull`, `sigDISPBull`, `u5_DISPBull` (USE V5 variant).
- **Plot offset:** -1.
- **Used by:** `hvdpbjppd::DispCons2/3`, `Golf`, `Alpha Strike`, `OD_BULL`, `WBUSH_BULL`, `tnt-od::DYNAMITE`, `WBUSH+TNTOD-ANY`, `squarify::S22-S46` (DISP-using), `ultra-combo::MEGA_BULL`.
- **Drift warning:** σ-multiplier defaults vary across indicators (3.0 / 5.0 / 6.0). Reconcile in Stage 6.

### `hvdpbjppd::DISP_BEAR`, `hvdpbjppd::DISP2_BULL/BEAR`, `hvdpbjppd::DISP3_BULL/BEAR`

Variants for streak gating. DISP2 uses `i_disp2_std_min=3.0` (was 5.0); DISP3 uses `i_disp3_std_min=3.0` (was 4.0).

---

## Family: FVG / GZI / HV-FVG

### `hv-fvg-gz1-og::FVG_BULL_RAW`

- **Plain English:** Bullish FVG — bar 0 low > bar 2 high, bar 1 close > bar 2 high, gap-size relative to bar 2 high exceeds threshold.
- **Parameters:** `thresholdPer=1.0`, `auto=true` (auto threshold = cumulative `((high-low)/low)/bar_index`), `tf=""`.
- **Canonical owner:** `hv-fvg-gz1-og` (`HV_FVG_GZ1_OG_v1.pine`).
- **Aliases:** `bull_fvg_raw`, `gz_bullFVG` (b2b-pup, hvdpbjppd, squarify, ultra-combo re-implementations).
- **Plot offset:** not plotted directly; drives `box.new`.

### `hv-fvg-gz1-og::FVG_BEAR_RAW`

Symmetric mirror.

### `hv-fvg-gz1-og::GZI_BULL`

- **Plain English:** Fires on creation of a new bullish FVG that price-overlaps a prior bullish FVG within `gziProximity` bars; adjacent-touch counts when both are HV.
- **Parameters:** `showGZI=true`, `gziProximity=6` (CANONICAL — but B2B PUP / HVDPBJPPD / Squarify use `gz1_dist=7`; reconcile in Stage 6).
- **Canonical owner:** `hv-fvg-gz1-og`.
- **Aliases:** `bullGZI_trigger`, `gz_bullGZI`, `bullGZI`.
- **Plot offset:** **-1**.
- **Used by:** `b2b-pup::CS1_BULL_FVG_COMBO`, `CS3_UNIFIED_COMBO_BULL` (via CS1); `hvdpbjppd::comboSet1`, `csNew1`, `csNew3` (Unified Combo); `squarify::S35_NAG_PLUS`, `S36_UU_HVD`, S37, S40, S44, S45, T1 OPENING CONFLU, WBUSH; `tnt-od::CATALYST` (via u5_CS1_Bull); `ultra-combo::OPENER_BULL`, `MEGA_BULL`, `comboGZ_AnyBull`, `comboGZHV_AnyBull`.

### `hv-fvg-gz1-og::GZI_BEAR`, `HV_BULL`, `HV_BEAR`

GZI_BEAR mirrors GZI_BULL (`gz_bearGZI`).

`hv-fvg-gz1-og::HV_BULL`: fires on creation of new bull FVG whose formation-bar volume = highest of 5000/252/63 lookbacks. `showHV=true`. Plot offset **-1**. Aliases: `bullHV_trigger`, `gz_bullHV`, `bullHV`. Used by all CS1/CS2/Mega/WBUSH composites.

`hv-fvg-gz1-og::HV_BEAR`: symmetric mirror.

---

## Family: Matrix Number

### `hvdpbjppd::MATRIX_NUMBER`

- **Plain English:** Volume on the current bar equals the highest volume over `neo_len` bars.
- **Parameters:** `neo_len=67`.
- **Canonical owner:** `hvdpbjppd`.
- **Aliases:** `is_matrix_number`.
- **Used by:** `hvdpbjppd::Neo` (`is_matrix_number AND FAUNA(direction)`), `Trinity` (`is_matrix_number AND NOT FAUNA AND directional bar`), `MATRIX_COMBO_BULL` (`csNew2`); `b2b-pup::Matrix Neo`/`Trinity`; `squarify::sigNeoBull`/`sigTrinityBull`.

**Note on Matrix family resolution (CONFIRMED from `hvdpbjppd::THE_ONLY_ONE` line 1052):**
- `Neo = MATRIX_NUMBER AND FAUNA(direction)` (Tier 1 composite).
- `Trinity = MATRIX_NUMBER AND NOT FAUNA(direction) AND directional bar` (Tier 1 composite, mutex with Neo).
- `MATRIX_COMBO (csNew2) = comboSet3 OR comboSet4` — wraps BOTH Neo AND Trinity (and aligned variants), gated by body% AND RVOL/Pentagon-slot.
- `FVG_COMBO (csNew1) = comboSet1 OR comboSet2`.
- `UNIFIED_COMBO (csNew3) = csNew1 AND csNew2` **same-bar AND** in canonical (predecessor + Squarify use 1-bar lagged AND — drift candidate).

---

## Family: Momentum tier (Long/Short)

### `hvdpbjppd::LONG1`, `SHORT1`, `LONG2`, `SHORT2`

LONG1: regular & cumulative RVOL ratios both exceed floors AND body ratio ≥ floor AND directional close. `ls_reg1=7.0` (was 10), `ls_cum1=3.5` (was 5), `ls_body1=0.60` (was 0.69). Aliases: `det_Long1`, `sigLong1`. Used by Neo-aligned/Trinity-aligned, LSC chain, Alpha Strike, Omega cosignal, S39 Foster+PUP+1x.

LONG2: lower thresholds, stricter body. `ls_reg2=5.0` (was 8), `ls_cum2=2.5` (was 4), `ls_body2=0.75` (was 0.69).

SHORT1, SHORT2: symmetric mirrors.

---

## Family: HV-rank lookback

### `hvdpbjppd::HV75`, `HV150`, `HV500`, `HV1000`

- **Plain English:** Volume ≥ highest in 75/150/500/1000-bar lookback (using volume[1]).
- **Parameters:** `hv150_len=150` (input); 75/500/1000 hardcoded.
- **Aliases:** `sigHV75`, `sigHV150`, `sigHV500`, `sigHV1000`, `u5_HV1000`.
- **Used by:** Omega cosignal, TF Gate counter, S22 NPM+ (via sigWMD path), TNT-OD enrichment.

---

## Family: RVOL (Heavy Pentagon)

### `heavy-pentagon::SAAB`

- **Plain English:** Bullish RVOL spike whose normalised price magnitude sits in the SAAB/Kratos band ([`th_saab_kratos`, `th_1x`)) on a green candle.
- **Parameters:** `bb_avgLength=30`, `bb_smaLength=20`. Threshold = `f_rvol_1x_threshold(tfSec) * 0.56`.
- **Canonical owner:** `heavy-pentagon`.
- **Aliases:** `sigSAAB`, `sig_SAAB`, `u5_SAAB`.
- **Plot offset:** 0.
- **Used by:** `heavy-pentagon::HEAVY_YIN_YANG_*` (groupA via OR), 5 base combos via groupA_Bull = `BULL_RVOL_1X OR GRAND_SLAM`; **NOTE: SAAB and Kratos are explicitly EXCLUDED from groupA in Heavy Pentagon Stage-5 doctrine** — they're computed but orphaned downstream. `b2b-pup::S5_BULL` (B2B+SAAB), `csNew1_Bull` slot. `hvdpbjppd::HW_BULL` (via HW-slot), `Floor`, `2F`, `Alpha Strike`. `squarify::S9_ALPHA_STRIKE`, etc.
- **Drift warning:** RVOL ladder threshold tables vary across indicators. B2B PUP comment "Pre Mythos thresholds" suggests divergence. Stage 6 byte-diff.

### `heavy-pentagon::KRATOS`, `BULL_RVOL_1X`, `BEAR_RVOL_1X`, `GRAND_SLAM`, `MOAB`, `PENTAGON`, `WTC`, `HIROSHIMA`, `NAGASAKI`

KRATOS: bear mirror of SAAB. Orphaned downstream like SAAB.

BULL_RVOL_1X: bullish base in [`th_1x`, `th_gs_moab`) band. `sigBullRVOL1x`, `u5_RVOL1xB`. Used in groupA_Bull, HW-slot, Alpha Strike, T1 OPENING CONFLU.

BEAR_RVOL_1X: mirror.

GRAND_SLAM: bullish base ≥ `th_gs_moab`. `sigGrandSlam`, `u5_GS`. Top-tier bull. Used in groupA_Bull, HW-slot, Alpha Strike.

MOAB: bear mirror.

PENTAGON (Reg@Time): `relVolRatio` in [`th_1x`, `th_wtc`]. Reg parameters: `reg_anchorTimeframe=""`, `reg_length=30`, `reg_calculationMode="Cumulative"`, `reg_adjustRealtime=true`. **Namespace collision warning:** HVDPBJPPD also has `anyBearPent` (Penthouse, bear-PB-mirror of Floor) — distinct concept. Stage 6 should rename Penthouse to `anyBear2F`.

WTC: `relVolRatio` in (`th_wtc`, `th_hiroshima`].

HIROSHIMA: `relVolRatio` > `th_hiroshima`.

NAGASAKI: raw bar volume sets new ATH vs running `maxVol` since `bar_index 0`. Plot title includes "(HEV)". Used by HEAVY_NAGASAKI/HEAVY_NAGASAKI_VOL/HEAVY_TRIDENT composites; `hvdpbjppd::nag_dir_bull/bear` directional filter; `squarify::S35_NAG_PLUS`, S45/S46 UC NAGASAKI; `tnt-od` standalone alert; `vob-asym::Nagasaki` (re-implemented in VOB).

---

## Family: Confluence Engine (TNT)

### `tnt-od::TNT_RAW_BULL`, `TNT_RAW_BEAR`

- **Plain English:** TNT 1.0 confluence — VOB ema-cross OB + ANISH swing-OB cross + FLUX pullback all confirm in same window AND zones overlap AND volume/EMA-slope/RSI synergy gate AND min-bar-gap cooldown elapsed.
- **Parameters:** `SENS=100`, `SWING_LEN=10`, `EMA_FAST=SENS`, `EMA_SLOW=SENS+13`, `ATR_VAL=ATR(200)`, `ATR_MULT=3.5`, `ATR_MIN=0.5`, `MIN_SIG_GAP=EMA_SLOW`, `CONF_WINDOW=EMA_SLOW*2`.
- **Canonical owner:** `tnt-od` (canonical = `TNT_OD_v3.pine`; date-stamped `_2026-05-04` is internally v2).
- **Aliases:** `raw_bullTNT`, `det_bullTNTraw`, `det_bullTNT`.
- **Note:** Composite by construction (VOB+ANISH+FLUX) but per Anish "TNT" is the human-named primitive — treat as root.
- **Used by:** TNT-family composites (Napalm/Charge/Return/CONT/TNT2/Super-TNT), CATALYST (via u5_CS1), FUSE, IGNITE, S15 TNT+B2B, NPM+TNT.

### `tnt-od::OD`

Anemic — session-first-bar gate only. `u5_od_max_bars=1` input declared but unused. OD-ness comes via `firstStatus_N`/`alertOK_N` gating elsewhere.

### `tnt-od::NAPALM_BULL`, `NAPALM_BEAR`

Bullish: directional FVG-confirmed displacement bar that pierces an active opposing TNT zone level. Aliases: `raw_napalmBull`, `det_bullNapalm`. Used in B2B Napalm, RC NPM+TNT, FUSE, CATALYST, PBJ+NPM, IGNITE-NC, S25, S26, S33, S34.

### `tnt-od::CHARGE_BULL`, `CHARGE_BEAR`

Displacement violating stored ChargeLevel; pushes new same-direction ChargeLevel (v4.32 fix). Aliases: `raw_bullCharge`, `det_bullCharge`. Used inside `det_bullNapalmCons = raw_napalmBull OR raw_bullCharge`, CONT.

### `tnt-od::RET_BULL_TNT`, `RET_BEAR_TNT`

First retrace into still-active TNT zone after breakout. `RET_TNT_PCT=100.0`, `RET_SUPER_PCT=50.0`. Single-fire per zone via `returnFired` flag. Used in CONT, RC TNT+RET.

---

## Family: VOB Engine

### `vob-asym::VOB_CROSS`, `BULL_ZONE_PUSH`, `BEAR_ZONE_PUSH`, `ZONE_INVALIDATION`

VOB_CROSS: EMA fast/slow crossover trigger (`ta.crossover(ema(close, len1), ema(close, len1+13))`). `len2 = len1 + 13` hardcoded. Per tier {2500, 2250, 2000, 1500, 1250, 1000} for A-F.

BULL_ZONE_PUSH: on bull cross, find lowest low in lookback, accumulate volume swing-low → cross bar, push to `lower_X` array with bounds.

BEAR_ZONE_PUSH: symmetric (push to `upper_X`).

ZONE_INVALIDATION: bull invalidated on `close < lower`; bear on `close > upper`. Plus dedup-nuke when `mid` within `atr_proximity = ATR(200,200)*3` of previous. Array hard-cap 15 zones per tier per direction.

### `vob-asym::T3_SUPER_BUY`, `T3_SUPER_SELL`

T3 buy: exactly ONE active bull zone AND opposing bear pool > 0 AND bull zone volume > bear pool × `super_mult` AND close inside dominant bull zone. `super_mult=1.5`, `cooldown_bars=100`. Per-tier independent — 6 instances A-F. Aliases: `t3_buy_a..f`, `t3_sell_a..f`.

### `vob-ladder::Z_A` through `Z_F`

Per-tier highest-priced active VOB bull zone midpoint extracted from `lower_X` arrays. Mirror of `vob-asym::BULL_ZONE_PUSH` per-tier (cross-ref). Z_F is the ladder anchor — must exist for any `ladder_depth > 0`.

---

## Family: Cluster (F2/E3/FC)

### `ultra-combo::F2`

- **Plain English:** F2-bar setup — session bar #2 with two consecutive same-direction MB candles.
- **Composition:** `sessBar==2 AND MB[0] AND MB[1]`.
- **Canonical owner:** `ultra-combo` (per CHANGELOG, member of "F2/E3/FC cluster" vocabulary).
- **Aliases:** `sBullF2`, `sBearF2`.
- **Used by:** `squarify::S14_PBJ_F2_E3`, `S15_PBJ_CL`, `S16_F2CL_E3`, `S18_F2_2D`, `S20_F2E3_SEQ`; `ultra-combo::comboPBJ_F2`, `comboB2B_F2`, `comboF2_B2BDays`, `comboF2_CLUSTER_E3`, `comboF2ClusterB2B`.
- **Note:** F2 internally references MB (`fauna::MB`) — treated as root per Anish naming convention even though structurally a tier-1 composite.

### `ultra-combo::E3`

- **Plain English:** E3 cluster — session bar #3 with three consecutive MB|RE|TA bars in same direction.
- **Composition:** `sessBar==3 AND ev[0] AND ev[1] AND ev[2]` where `ev = MB OR RE OR TA`.
- **Aliases:** `sBullE3`, `sBearE3`.
- **Used by:** `squarify::S14`, `S16`, `S17_E3_2of3PP`, `S19_E3_2D`, `S20_F2E3_SEQ`; `ultra-combo::comboPBJ_E3`, `comboE3_2of3PUP`, `comboE3_B2BDays`, `comboF2_CLUSTER_E3`.

### `ultra-combo::FC`

- **Plain English:** F2/E3 Cluster overlap — 2-of-3 cluster indicators align with overlapping price ranges between threshold-bar and sequential-bar zones inside a 20-bar window.
- **Parameters:** window=20, bull_seq_sum_min=0.1, bear_seq_sum_min=0.5, rvol-price spike > 2.9.
- **Aliases:** `sBullFC`, `sBearFC`.
- **Used by:** `squarify::S15_PBJ_CL`, `S16_F2CL_E3`, `S21_CL_2D`; `ultra-combo::comboPBJ_CLUSTER`, `comboCluster_B2BDays`, `comboF2_CLUSTER_E3`, `comboF2ClusterB2B`.

---

## Family: Transition (TB / Foster)

### `ultra-combo::TB` (TB Sell)

- **Plain English:** After ≥`minAnishBars=5` consecutive `bullPass` days, a `window=2`-bar window opens; first bear-direction trigger (`sPPBear` / PBJ-sell / PB-sell) fires TB / TB-PBJ / TB-PB.
- **Aliases:** "TB Sell", `tbSignal`.
- **Note:** Cross-ref candidate — TNT-OD line 367 comment "EXACT COPY FROM ANISH TB FOSTER v6" implies a separate `anish-tb-foster` indicator may exist outside the repo.
- **Used by:** `ultra-combo::tbHeavyBear`, `fosterHeavyBull`; `squarify::S39_FOS_PUP_1X` (via fosterPBJSignal); state-machine in `anish-50-1st-combo::TB_SELL`.

### `ultra-combo::FOSTER` (Foster Buy)

Symmetric mirror. Used by `ultra-combo::fosterHeavyBull`, `squarify::S39_FOS_PUP_1X`.

---

## Family: Oscillator (ROC, Boom Hunter Omega)

### `ultra-combo::ROC`

- **Plain English:** ROC + LazyBear WaveTrend — PBJ aligned with ROC-EMA + LazyBear WaveTrend conditions AND HW-hit AND directional close. Per CHANGELOG treated as a single named "ROC" root despite composite-of-mechanics structure.
- **Parameters:** `roc_pN=close[5]`, `roc_ar=SMA(|Δroc|,100)`, `roc_ema=EMA(roc/roc_ar,5)`, WaveTrend ESA=EMA(hlc3,8), CI/(ATR100), wt1=EMA(ci,21), wt2=SMA(wt1,4).
- **Aliases:** `sigROCBull`, `sigROCBear`.
- **Used by:** `ultra-combo::OPENER_BULL`, `comboHW_AnyBull`, `fosterHeavyBull`, `gzHvHeavyBull`.
- **Note:** LazyBear WaveTrend is INTERNAL_MECHANIC of ROC (EMA cross primitives) — NOT a separate root.

### `hvdpbjppd::BOOM_HUNTER_OMEGA`

- **Plain English:** Ehlers HP+Filt+Peak quotient stack entry events: `enter3 ∧ enter5 ∧ enter7`, lone-lime, or `wt2` oversold/overbought bounces.
- **Parameters:** Hardcoded — `bh_LPPeriod=6/27/11`, `bh_n1=9, bh_n2=6, bh_n3=3, bh_n4=21`, `bh_K1=0`, `bh_K12=0.8`.
- **Aliases:** `bh_anyOmega`.
- **Used by:** `hvdpbjppd::sigOmegaLong`, `sigShortPlusPress`; `squarify::sigOmegaLong`, `S10_OMEGA_A`.

---

## Family: Structural (Ping Pong)

### `hvdpbjppd::PING_PONG_BULL`, `PING_PONG_BEAR`

- **Plain English:** Pivot-based S/R level engine; counts pivots/regimes/bounces/breaks; declares bull/bear regime by counted state ≥ `pp_min_count` with floor/ceiling gravity flag.
- **Parameters:** `sw_leftBars=3` (was 5), `sw_rightBars=2` (was 1), `sw_useAtr=true`, `sw_atrMult=2.0`, `pp_atr_len=100`, `pp_min_count=3`, `pp_max_levels=50`, `pp_min_candles=2`, `pp_buffer_ticks=10`, `pp_atr_mult=2.0`, `pp_trend_cnt=1`.
- **Aliases:** `bull_pp`, `bear_pp`.
- **Used by:** `hvdpbjppd::FLOOR_BULL` (= `bull_pp AND PBJ AND HW-slot`), `2F`, `ROOF_BEAR`, `Penthouse`, `Alpha Strike`; `squarify::S4_FLOOR`, `S5_2F`, `S9_ALPHA_STRIKE`.

---

## Family: FAUNA atomic sub-roots (distributed)

These are FAUNA's seven internal cores and exclusions. The same definition appears verbatim in heavy-pentagon's USE V5 block, hvdpbjppd, squarify, ultra-combo, tnt-od (USE V5), b2b-pup. Stage 6 should designate one canonical owner.

### `fauna::MB` (Marubozu / Massive Body)

Directional body, body-size > 1.6×ATR(14), body/range > 0.7, vol > 1.8×SMA(volume, 20). Aliases: `bull_MB`/`bear_MB`/`fMB_b`/`fMB_r`.

### `fauna::RE` (Range Expansion)

Directional, range > 2.2×ATR, opposite-side wick < 0.15×range, vol > 1.8×avg. Aliases: `bull_RE`/`bear_RE`/`fRE_b`/`fRE_r`.

### `fauna::TA` (Trend Acceleration)

Rising/falling 50-SMA + close-to-close move > 1.6×SMA(|Δclose|,10) in same direction + vol > 1.8×avg. Aliases: `bull_TA`/`bear_TA`/`fTA_b`/`fTA_r`.

### `fauna::GG` (Gap-Go)

Open-prev-close gap > 0.9×ATR, direction match, low > prev close (or high < prev close for bear), vol > 1.8×avg. Used as FAUNA exclusion. Aliases: `fGG_b`/`fGG_r`.

### `fauna::TR` (Trap)

Prev weak counter-bar (body/range ≤ 0.2) + core fired. FAUNA exclusion.

### `fauna::ES` (Exhaustion)

Prev strong counter-bar (|body| > 1.5×avgBody, vol > 1.5×avgVol) + core fired. FAUNA exclusion.

### `fauna::GDR` (Gap-Down-Reversal)

Prev counter-color + GG. FAUNA exclusion.

**FAUNA composite formula (LOCKED, verified in source):**
`FAUNA_BULL = (MB_b OR RE_b OR TA_b) AND NOT (TR_b OR ES_b OR GDR_b OR GG-excluded)` (line 732 of Ultra Combo; same shape in Squarify line 474-506).

---

## Summary

| Family | Canonical owner | Roots count |
|---|---|---|
| Push | anish-50-1st-combo | 2 (PUP, PPD) |
| Regime | anish-50-1st-combo | 2 (BULL_PASS, BEAR_PASS) |
| Zoo Pipeline | hvdpbjppd | 4 (PBJ_BULL/BEAR, PB_BULL/BEAR) |
| Volume + Displacement | hvdpbjppd | 2 (HVD_BULL, HVD_BEAR) |
| Displacement | hvdpbjppd | 6 (DISP, DISP2, DISP3 × bull/bear) |
| FVG/GZI/HV-FVG | hv-fvg-gz1-og | 6 (FVG_RAW, GZI, HV × bull/bear) |
| Matrix Number | hvdpbjppd | 1 |
| Momentum tier | hvdpbjppd | 4 (LONG/SHORT × 1/2) |
| HV-rank lookback | hvdpbjppd | 4 (75/150/500/1000) |
| RVOL P1/P2/P3 | heavy-pentagon | 10 |
| Confluence Engine | tnt-od | 2 (TNT_RAW × bull/bear) + OD |
| TNT Propulsion | tnt-od | 6 (NAPALM/CHARGE/RET × bull/bear) |
| VOB Engine | vob-asym | 6 + 6 ladder tiers |
| Cluster | ultra-combo | 3 (F2, E3, FC) |
| Transition | ultra-combo | 2 (TB, FOSTER) |
| Oscillator | ultra-combo / hvdpbjppd | 2 (ROC, BOOM_HUNTER_OMEGA) |
| Structural | hvdpbjppd | 2 (PING_PONG × bull/bear) |
| FAUNA atomics | distributed | 7 (MB, RE, TA, GG, TR, ES, GDR) |

**Total: 78 canonical roots** across 12 indicator families.
