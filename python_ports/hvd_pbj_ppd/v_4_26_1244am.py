"""
HVD+PBJ+PPD Python port — masterdir-lineage variant (4.26.1244am)
==================================================================

Source Pine file:
  /home/user/indicators/hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine
  (1939 lines, dated 2026-05-09)

Audit report:
  /home/user/indicators/bible-input/agent-reports/hvd-pbj-ppd-delta-4-26-1244am.md

Lineage / drift summary
-----------------------
- This file is the algorithmic NEAR-TWIN of `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine`
  (only IPSF defaults differ — 10 hunks, all input.bool / input.float defaults).
- It is the algorithmic CORE of `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine`
  (2246 = mine + extra header / dashboard rendering).
- It is a SEPARATE FORK from `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`:
    * mine wraps detections in extra `*_gated` co-signal helpers (uu_gated_*,
      floor_gated, floor2_gated)
    * mine uses different FAUNA-offset logic for DispCons2/3
    * mine requires PBJ-only for AlphaStrike (vs PBJ-or-PB in THE_ONLY_ONE)
    * mine has cross-bar offset for csNew3 (FVG bar N + Matrix bar N-1)
    * mine has Omega-A and NAG+ Bull plots that don't exist in THE_ONLY_ONE

Conventions
-----------
- Single-file module; pandas + numpy.
- Each detection plot has a `def detect_<snake>(df, params) -> pd.Series` that
  returns a boolean Series indexed identically to df.
- Internal helpers are in the `_helpers` section near the top.
- IPSF parameters live in `DEFAULTS` and are passed via the `params` dict.
- Hardcoded thresholds from Pine remain hardcoded here.
- Most detections require Pine-only intrinsics (FAUNA scoring, P21 streak walk,
  Boom Hunter omega state, gz_fvg array, ATR ladders) and are STUBBED.

Module exports
--------------
  DETECTIONS:     dict[str, callable] — fully-ported detection functions
  STATE_MACHINES: dict[str, type]     — stateful detection wrappers (classes)
  STUBBED:        dict[str, str]      — detection name -> reason for stub
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ============================================================================
# IPSF DEFAULTS — mirrored exactly from this Pine file (NOT from 1939-twin)
# Anything declared with input.* in the Pine source becomes a key here.
# ============================================================================

DEFAULTS: dict = {
    # === DETECTION TOGGLES — TIER 1 ===
    "show_BullUUUU": True,
    "show_BearUUUU": False,
    "show_BullUUU": True,
    "show_BearUUU": False,
    "show_BullUU": False,
    "show_BearUU": False,
    "show_OmegaLongA": False,
    "show_AlphaStrikeB": False,
    "show_AlphaStrikeR": False,
    "show_FoxtrotB": True,
    "show_FoxtrotR": False,
    "show_OmegaLong": False,
    "show_ODBull": True,
    "show_ODBear": False,
    "show_DispConsBull2": True,
    "show_DispConsBear2": False,
    "show_DispConsBull3": True,
    "show_DispConsBear3": True,
    "show_GolfBull": True,
    "show_GolfBear": True,
    "show_PAFBull": True,
    "show_PAFBear": True,

    # === TIER 1B: Combo Sets ===
    "show_CS1B": False,
    "show_CS1R": False,
    "show_CS2B": False,
    "show_CS2R": False,
    "show_CS3B": True,
    "show_CS3R": False,

    # === TIER 1C: Chains ===
    "show_CCBull": True,
    "show_CCBear": False,
    "show_LSCBull": False,
    "show_LSCBear": False,

    # === TIER 2: Structure ===
    "show_BullFloor": False,
    "show_Bull2ndFloor": False,
    "show_BearRooftop": False,
    "show_BearPenthouse": False,

    # === TIER 3: HW ===
    "show_HWBull": True,
    "show_HWBear": False,

    # === PRIORITY ===
    "show_SuperBull": False,
    "show_SuperBear": False,
    "show_SDuperBull": True,
    "show_SDuperBear": False,

    # === DISPLACEMENT ===
    "i_disp_type": "Open to Close",
    "i_std_len": 100,
    "i_std_min": 6.0,                # NOTE: 1939-twin defaults this to 4.5
    "i_std_max": 100.0,
    "i_req_fvg": True,

    # === DISPLACEMENT 2+ ===
    # (separate group in Pine but uses same shape)
    "i_disp2_type": "Open to Close",
    "i_disp2_std_len": 100,
    "i_disp2_std_min": 4.0,
    "i_disp2_std_max": 100.0,
    "i_disp2_req_fvg": True,

    # === DISPLACEMENT 3+ ===
    "i_disp3_type": "Open to Close",
    "i_disp3_std_len": 100,
    "i_disp3_std_min": 4.0,          # NOTE: 1939-twin defaults this to 3.0
    "i_disp3_std_max": 100.0,
    "i_disp3_req_fvg": True,

    # === SWING / PP ===
    "pp_atr_len": 100,

    # === Consecutive Streak (P21) ===
    "p21_pbj_dist": 1,               # NOTE: 1939-twin defaults this to 4

    # === OPENING DRIVE ===
    "od_max_bars": 2,

    # === MATRIX (NEO) ===
    "neo_len": 67,

    # === MOMENTUM 1 ===
    "ls_reg1": 10.0,                 # 1939-twin: 7.0
    "ls_cum1": 5.0,                  # 1939-twin: 3.5
    "ls_body1": 0.69,

    # === MOMENTUM 2 ===
    "ls_reg2": 8.0,                  # 1939-twin: 5.0
    "ls_cum2": 4.0,                  # 1939-twin: 2.5
    "ls_body2": 0.69,

    # === COMBO SET SETTINGS ===
    "cs_bodyPct_FVG": 0.74,          # 1939-twin: 0.69
    "cs_bodyPct_MAT": 0.74,          # 1939-twin: 0.69
    "cs_inc_pentagon_FVG": True,
    "cs_inc_pentagon_MAT": True,

    # === COMBO CHAIN ===
    "cc_min_hits": 2,
    "cc_window": 2,

    # === LONG/SHORT CHAIN ===
    "lsc_min_hits": 2,
    "lsc_window": 2,
    "lsc_reg1": 10.0,                # 1939-twin: 7.0
    "lsc_cum1": 5.0,                 # 1939-twin: 3.5
    "lsc_body1": 0.74,               # 1939-twin: 0.69
    "lsc_reg2": 8.0,                 # 1939-twin: 5.0
    "lsc_cum2": 4.0,                 # 1939-twin: 2.5
    "lsc_body2": 0.79,               # 1939-twin: 0.69

    # === HV+D DETECTION TOGGLES ===
    "en_hvd_bull": False,
    "en_hvd_bear": False,
    "en_hvd_pb_bull": False,
    "en_hvd_pb_bear": False,
    "en_hvd_pbj_bull": False,
    "en_hvd_pbj_bear": False,

    # === PIPELINE D — TRIPLE CO-OCCURRENCE ===
    "co_en_bullPBJ": False,
    "co_en_bullPB": False,
    "co_en_bearPBJ": False,
    "co_en_bearPB": False,

    # === BACK-TO-BACK HV+D ===
    "b2b_en_bull": True,
    "b2b_en_bear": False,
    "b2b_en_bull_pbj": True,
    "b2b_en_bear_pbj": False,
    "b2b_en_bull_pb": True,
    "b2b_en_bear_pb": False,

    # === HV+D MOMENTUM CO-OCC ===
    "en_hvdm_pup_bull": True,
    "en_hvdm_ppd_bear": False,
    "en_hvdm_rvol_bull": True,
    "en_hvdm_rvol_bear": False,
    "en_hvdm_cmb_bull": True,
    "en_hvdm_cmb_bear": False,
    "en_hvdm_2of3_bull": True,
    "en_hvdm_2of3_bear": False,
    "en_hvdm_3of3_bull": True,
    "en_hvdm_3of3_bear": False,

    # === MASTER GATE / FIRST-BAR-ONLY ===
    "en_firstBarOnly": False,
}


# ============================================================================
# _helpers
# ============================================================================

def _bool(s: pd.Series) -> pd.Series:
    """Force a series to dtype=bool, NaN -> False (mirrors Pine's `nz(x)` for bool)."""
    return s.fillna(False).astype(bool)


def _shift_nz(s: pd.Series, n: int) -> pd.Series:
    """Pine `nz(x[n])` -> NaN replaced with False after shift(n)."""
    return _bool(s.shift(n))


def _series_false(df: pd.DataFrame) -> pd.Series:
    return pd.Series(False, index=df.index, dtype=bool)


def _series_true(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index, dtype=bool)


def _master_gate(df: pd.DataFrame, params: dict, _any_hv_bar0: pd.Series | None = None) -> pd.Series:
    """
    masterGate = not en_firstBarOnly or (isFirstBar and _anyHV_bar0)

    `isFirstBar` is the first bar of the trading session; `_anyHV_bar0` is true
    when the first bar has any HV ladder hit. Without those Pine intrinsics
    available we conservatively pass-through `not en_firstBarOnly` semantics.
    """
    if not params.get("en_firstBarOnly", False):
        return _series_true(df)
    # Stubbed branch: when en_firstBarOnly is true we'd need session + HV detection
    raise NotImplementedError(
        "STUBBED: masterGate with en_firstBarOnly requires session detection + "
        "HV ladder detection; port via realtime-indicators tv_ta wrapper"
    )


# ============================================================================
# DETECTION PLOTS — fully-ported (boolean composition only)
# These wrap upstream pre-computed Pine-equivalent boolean columns that the
# caller is expected to provide on `df`. Where the underlying boolean is itself
# a Pine-only intrinsic, the detection is stubbed instead.
# ============================================================================

# ---- HV+D root + PBJ/PB co-occurrence (Pipeline A & B) -----------------------

def detect_hvd_bull(df: pd.DataFrame, params: dict) -> pd.Series:
    """plotshape line 1402: en_hvd_bull and hvd_fire_bull and masterGate"""
    if not params.get("en_hvd_bull", False):
        return _series_false(df)
    return _bool(df["hvd_fire_bull"]) & _master_gate(df, params)


def detect_hvd_bear(df: pd.DataFrame, params: dict) -> pd.Series:
    """plotshape line 1403"""
    if not params.get("en_hvd_bear", False):
        return _series_false(df)
    return _bool(df["hvd_fire_bear"]) & _master_gate(df, params)


def detect_hvd_pb_bull(df: pd.DataFrame, params: dict) -> pd.Series:
    """
    plotshape line 1408: en_hvd_pb_bull and hvd_pb_bull and masterGate
    where hvd_pb_bull = hvd_fire_bull and nz(sigBullPB[1])
    """
    if not params.get("en_hvd_pb_bull", False):
        return _series_false(df)
    return (
        _bool(df["hvd_fire_bull"])
        & _shift_nz(df["sigBullPB"], 1)
        & _master_gate(df, params)
    )


def detect_hvd_pbj_bull(df: pd.DataFrame, params: dict) -> pd.Series:
    """plotshape line 1409"""
    if not params.get("en_hvd_pbj_bull", False):
        return _series_false(df)
    return (
        _bool(df["hvd_fire_bull"])
        & _shift_nz(df["sigBullPBJ"], 1)
        & _master_gate(df, params)
    )


def detect_hvd_pb_bear(df: pd.DataFrame, params: dict) -> pd.Series:
    if not params.get("en_hvd_pb_bear", False):
        return _series_false(df)
    return (
        _bool(df["hvd_fire_bear"])
        & _shift_nz(df["sigBearPB"], 1)
        & _master_gate(df, params)
    )


def detect_hvd_pbj_bear(df: pd.DataFrame, params: dict) -> pd.Series:
    if not params.get("en_hvd_pbj_bear", False):
        return _series_false(df)
    return (
        _bool(df["hvd_fire_bear"])
        & _shift_nz(df["sigBearPBJ"], 1)
        & _master_gate(df, params)
    )


# ---- USE plotshapes — bull (22) ---------------------------------------------

def detect_bull_uuuu(df, params):
    raise NotImplementedError(
        "STUBBED: requires Pine-only P21 streak walk (sigP21BullUUUU); "
        "port via realtime-indicators tv_ta wrapper"
    )


def detect_bull_uuu(df, params):
    raise NotImplementedError(
        "STUBBED: requires Pine-only P21 streak walk (sigP21BullUUU); "
        "port via realtime-indicators tv_ta wrapper"
    )


def detect_bull_uu(df, params):
    """
    fire_BullUU = show_BullUU and uu_gated_bull and masterGate
    uu_gated_bull = sigUUBull and oneOfThese_forUU
    """
    raise NotImplementedError(
        "STUBBED: requires Pine-only sigUUBull walrus assignment + "
        "oneOfThese_forUU co-signal aggregator"
    )


def detect_alpha_strike_bull(df, params):
    """
    sigAlphaStrikeBull = conf and firstOfDay and bull_pp and
                         (sigGrandSlam or sigBullRVOL1x) and sigBullPBJ and as_fauna_bull
    NOTE: mine uses PBJ only; THE_ONLY_ONE uses (PBJ or PB)
    """
    raise NotImplementedError(
        "STUBBED: requires Pine-only firstOfDay + bull_pp (swing PP) + as_fauna_bull"
    )


def detect_foxtrot_bull(df, params):
    """sigFoxtrotBull = conf and sigFAUNABull and FAUNA[1..3]"""
    raise NotImplementedError("STUBBED: requires Pine-only sigFAUNABull intrinsic")


def detect_omega_long_a(df, params):
    """
    sigOmegaLongA = conf and bh_anyOmega and omega_cosignal_A and not sigMOAB and not sigDISPBear
    omega_cosignal_A is mine-only (does not exist in THE_ONLY_ONE).
    """
    raise NotImplementedError("STUBBED: requires Pine-only Boom Hunter omega state")


def detect_od_bull(df, params):
    """
    sigODBull = conf and sessionBarCount<=od_max_bars and od_fvg_bull and
                disp_prevDisp and sigPUP and sigBullPBJ
    """
    raise NotImplementedError("STUBBED: requires session bar count + od FVG detector")


def detect_disp_cons_bull2(df, params):
    """
    sigDispConsBull2 = sigDISP2Bull and disp2_bullStreak>=2 and
                       nz(sigFAUNABull[1]) and nz(sigFAUNABull[2])
    DRIFT: THE_ONLY_ONE uses sigFAUNABull current + [1] (different offset).
    """
    raise NotImplementedError("STUBBED: requires displacement-streak walker + FAUNA")


def detect_disp_cons_bull3(df, params):
    """
    sigDispConsBull3 = sigDISP3Bull and disp3_bullStreak>=3 and
                       nz(sigFAUNABull[1..3])
    DRIFT: THE_ONLY_ONE uses current + [1..2].
    """
    raise NotImplementedError("STUBBED: requires displacement-streak walker + FAUNA")


def detect_golf_bull(df, params):
    """
    sigGolfBull = conf and sigDISPBull and FAUNA[1] and PUP[1] and DISPBull[1]
                  and FAUNA[2] and PUP[2]
    """
    raise NotImplementedError("STUBBED: requires sigDISPBull / sigFAUNABull / sigPUP")


def detect_paf_bull(df, params):
    """sigPAFBull = conf and sigPUP and sigFAUNABull and PUP[1] and FAUNA[1]"""
    raise NotImplementedError("STUBBED: requires sigPUP / sigFAUNABull")


def detect_cs1b(df, params):
    """fire_CS1B = show_CS1B and csNew1_Bull and masterGate"""
    raise NotImplementedError("STUBBED: requires Combo Set 1/2 (FVG variants)")


def detect_cs2b(df, params):
    raise NotImplementedError("STUBBED: requires Combo Set 3/4 (Matrix variants)")


def detect_cs3b(df, params):
    """
    fire_CS3B = show_CS3B and csNew3_Bull and masterGate
    csNew3_Bull = csNew1_Bull and nz(csNew2_Bull[1])
    DRIFT: THE_ONLY_ONE uses csNew1 and csNew2 (same bar, no shift).
    """
    raise NotImplementedError("STUBBED: requires csNew1_Bull/csNew2_Bull")


def detect_cc_bull(df, params):
    """sigCCBull = conf and cc_bull_active (from cc_window stateful walker)"""
    raise NotImplementedError("STUBBED: requires combo-chain stateful walker")


def detect_lsc_bull(df, params):
    """sigLSCBull = conf and lsc_bull_active (from lsc_window stateful walker)"""
    raise NotImplementedError("STUBBED: requires LSC stateful walker")


def detect_bull_floor(df, params):
    """
    fire_BullFloor = show_BullFloor and floor_gated and masterGate
    floor_gated = anyBullFloor and oneOfThese and cb1_pass_floor
    DRIFT: THE_ONLY_ONE plots raw anyBullFloor (no gating layer).
    """
    raise NotImplementedError(
        "STUBBED: requires anyBullFloor + oneOfThese + cb1_pass_floor co-signal helpers"
    )


def detect_bull_2nd_floor(df, params):
    raise NotImplementedError(
        "STUBBED: requires anyBull2nd + oneOfThese + cb1_pass co-signal helpers"
    )


def detect_hw_bull(df, params):
    """
    hwBull = (close>open) and disp5_bull and sigBullPBJ and
             (sigGrandSlam or sigWTC or sigHiroshima or (sigNagasaki and nag_dir_bull))
             and (anyBullFloor or anyBull2nd)
    """
    raise NotImplementedError("STUBBED: requires disp5_bull + GS/WTC/Hiro/Nag intrinsics")


def detect_super_bull(df, params):
    raise NotImplementedError("STUBBED: requires bull_pp + super_hw_bull + super_comboAny_bull")


def detect_sduper_bull(df, params):
    raise NotImplementedError("STUBBED: requires anyBullFloor/2nd + super_hw_bull + super_comboAny_bull")


# ---- USE plotshapes — bear (21, mirrors of bull) ----------------------------

def detect_bear_uuuu(df, params):
    raise NotImplementedError("STUBBED: bear mirror of bull_uuuu")


def detect_bear_uuu(df, params):
    raise NotImplementedError("STUBBED: bear mirror of bull_uuu")


def detect_bear_uu(df, params):
    raise NotImplementedError("STUBBED: bear mirror of bull_uu")


def detect_alpha_strike_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of alpha_strike_bull")


def detect_foxtrot_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of foxtrot_bull")


def detect_od_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of od_bull")


def detect_disp_cons_bear2(df, params):
    raise NotImplementedError("STUBBED: bear mirror of disp_cons_bull2")


def detect_disp_cons_bear3(df, params):
    raise NotImplementedError("STUBBED: bear mirror of disp_cons_bull3")


def detect_golf_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of golf_bull")


def detect_paf_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of paf_bull")


def detect_cs1r(df, params):
    raise NotImplementedError("STUBBED: bear mirror of cs1b")


def detect_cs2r(df, params):
    raise NotImplementedError("STUBBED: bear mirror of cs2b")


def detect_cs3r(df, params):
    raise NotImplementedError("STUBBED: bear mirror of cs3b")


def detect_cc_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of cc_bull")


def detect_lsc_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of lsc_bull")


def detect_bear_rooftop(df, params):
    raise NotImplementedError("STUBBED: bear mirror of bull_floor")


def detect_bear_penthouse(df, params):
    raise NotImplementedError("STUBBED: bear mirror of bull_2nd_floor")


def detect_hw_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of hw_bull")


def detect_super_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of super_bull")


def detect_sduper_bear(df, params):
    raise NotImplementedError("STUBBED: bear mirror of sduper_bull")


# ---- Pipeline D — Triple Co-occurrence (4 plots) ----------------------------

def detect_co_bull_pbj(df: pd.DataFrame, params: dict) -> pd.Series:
    """
    plotshape line 1499:
      co_bull_pbj = hvd_fire_bull and co_en_bullPBJ and
                    nz(sigBullPBJ[1]) and nz(use_any_bull[1])
    """
    if not params.get("co_en_bullPBJ", False):
        return _series_false(df)
    if "use_any_bull" not in df.columns:
        raise NotImplementedError(
            "STUBBED: requires use_any_bull aggregator (depends on ~22 USE-block "
            "detections); port via realtime-indicators tv_ta wrapper"
        )
    return (
        _bool(df["hvd_fire_bull"])
        & _shift_nz(df["sigBullPBJ"], 1)
        & _shift_nz(df["use_any_bull"], 1)
        & _master_gate(df, params)
    )


def detect_co_bull_pb(df: pd.DataFrame, params: dict) -> pd.Series:
    if not params.get("co_en_bullPB", False):
        return _series_false(df)
    if "use_any_bull" not in df.columns:
        raise NotImplementedError("STUBBED: requires use_any_bull aggregator")
    return (
        _bool(df["hvd_fire_bull"])
        & _shift_nz(df["sigBullPB"], 1)
        & _shift_nz(df["use_any_bull"], 1)
        & _master_gate(df, params)
    )


def detect_co_bear_pbj(df: pd.DataFrame, params: dict) -> pd.Series:
    if not params.get("co_en_bearPBJ", False):
        return _series_false(df)
    if "use_any_bear" not in df.columns:
        raise NotImplementedError("STUBBED: requires use_any_bear aggregator")
    return (
        _bool(df["hvd_fire_bear"])
        & _shift_nz(df["sigBearPBJ"], 1)
        & _shift_nz(df["use_any_bear"], 1)
        & _master_gate(df, params)
    )


def detect_co_bear_pb(df: pd.DataFrame, params: dict) -> pd.Series:
    if not params.get("co_en_bearPB", False):
        return _series_false(df)
    if "use_any_bear" not in df.columns:
        raise NotImplementedError("STUBBED: requires use_any_bear aggregator")
    return (
        _bool(df["hvd_fire_bear"])
        & _shift_nz(df["sigBearPB"], 1)
        & _shift_nz(df["use_any_bear"], 1)
        & _master_gate(df, params)
    )


# ---- NAG+ Bull (mine-only; missing in THE_ONLY_ONE) -------------------------

def detect_nag_plus_bull(df, params):
    """
    fire_NagPlusBull = sigNagPlusBull
    sigNagPlusBull = sigNagasaki and (sigBullRVOL1x or sigGrandSlam or sigFAUNABull or
                                     sigDISPBull or sigBullPBJ or sigPUP or gz_bullHV or
                                     gz_bullGZI or sigLong1 or anyBullFloor or anyBull2nd)
    """
    raise NotImplementedError(
        "STUBBED: requires sigNagasaki + ~10 other intrinsic detectors; "
        "port via realtime-indicators tv_ta wrapper"
    )


# ---- Back-to-back HV+D (6 plots, stateful) ----------------------------------

class B2BWalker:
    """
    Stateful detector for B2B HV+D variants (lines 1517-1535).
    Two consecutive bars of hvd_fire, with optional PBJ/PB co-occurrence
    in either of the two consecutive bars (priors at [1] or [2]).

    Required df columns: hvd_fire_bull, hvd_fire_bear,
                         sigBullPBJ, sigBearPBJ, sigBullPB, sigBearPB
    """

    def __init__(self, params: dict):
        self.p = params

    def _raw(self, df: pd.DataFrame, side: str) -> pd.Series:
        col = f"hvd_fire_{side}"
        return _bool(df[col]) & _shift_nz(df[col], 1)

    def _pbj(self, df: pd.DataFrame, raw: pd.Series, side: str) -> pd.Series:
        sig = f"sig{'Bull' if side == 'bull' else 'Bear'}PBJ"
        return raw & (_shift_nz(df[sig], 1) | _shift_nz(df[sig], 2))

    def _pb(self, df: pd.DataFrame, raw: pd.Series, side: str, pbj: pd.Series) -> pd.Series:
        sig = f"sig{'Bull' if side == 'bull' else 'Bear'}PB"
        return raw & (_shift_nz(df[sig], 1) | _shift_nz(df[sig], 2)) & ~pbj

    def detect(self, df: pd.DataFrame) -> dict:
        out = {}
        for side in ("bull", "bear"):
            raw = self._raw(df, side)
            pbj = self._pbj(df, raw, side)
            pb = self._pb(df, raw, side, pbj)
            nopb = raw & ~pbj & ~pb
            mg = _master_gate(df, self.p)
            out[f"b2b_hvd_{side}"] = (
                _bool(pd.Series(self.p.get(f"b2b_en_{side}", False), index=df.index))
                & nopb & mg
            )
            out[f"b2b_hvd_pbj_{side}"] = (
                _bool(pd.Series(self.p.get(f"b2b_en_{side}_pbj", False), index=df.index))
                & pbj & mg
            )
            out[f"b2b_hvd_pb_{side}"] = (
                _bool(pd.Series(self.p.get(f"b2b_en_{side}_pb", False), index=df.index))
                & pb & mg
            )
        return out


def detect_b2b_hvd_bull(df, params):
    return B2BWalker(params).detect(df)["b2b_hvd_bull"]


def detect_b2b_hvd_bear(df, params):
    return B2BWalker(params).detect(df)["b2b_hvd_bear"]


def detect_b2b_hvd_pbj_bull(df, params):
    return B2BWalker(params).detect(df)["b2b_hvd_pbj_bull"]


def detect_b2b_hvd_pbj_bear(df, params):
    return B2BWalker(params).detect(df)["b2b_hvd_pbj_bear"]


def detect_b2b_hvd_pb_bull(df, params):
    return B2BWalker(params).detect(df)["b2b_hvd_pb_bull"]


def detect_b2b_hvd_pb_bear(df, params):
    return B2BWalker(params).detect(df)["b2b_hvd_pb_bear"]


# ---- HV+D Momentum Co-Occurrence (16 detection points, label.new in Pine) --
# Lines 1599-1631 + label.new statements 1633-1680
# All 16 are pure boolean compositions of pre-computed components shifted by 1.

def _hvdm_components_bull(df: pd.DataFrame) -> dict:
    return {
        "_m_pup1": _shift_nz(df["sigPUP"], 1),
        "_m_rv1b": _shift_nz(df["sigBullRVOL1x"], 1) | _shift_nz(df["sigGrandSlam"], 1),
        "_m_cb1b": _bool(df["csNew3_Bull"]),
        "_m_pj1b": _shift_nz(df["sigBullPBJ"], 1),
    }


def _hvdm_components_bear(df: pd.DataFrame) -> dict:
    return {
        "_m_ppd1": _shift_nz(df["sigPPD"], 1),
        "_m_rv1r": _shift_nz(df["sigBearRVOL1x"], 1) | _shift_nz(df["sigMOAB"], 1),
        "_m_cb1r": _bool(df["csNew3_Bear"]),
        "_m_pj1r": _shift_nz(df["sigBearPBJ"], 1),
    }


def detect_hvdm_pup_nopbj_bull(df, params):
    """label group 1633: HVD\nPUP — hvd_fire_bull and pup[1] and not pbj[1]"""
    if not params.get("en_hvdm_pup_bull", False):
        return _series_false(df)
    c = _hvdm_components_bull(df)
    return _bool(df["hvd_fire_bull"]) & c["_m_pup1"] & ~c["_m_pj1b"] & _master_gate(df, params)


def detect_hvdm_rvol_nopbj_bull(df, params):
    if not params.get("en_hvdm_rvol_bull", False):
        return _series_false(df)
    c = _hvdm_components_bull(df)
    return _bool(df["hvd_fire_bull"]) & c["_m_rv1b"] & ~c["_m_pj1b"] & _master_gate(df, params)


def detect_hvdm_cmb_nopbj_bull(df, params):
    if not params.get("en_hvdm_cmb_bull", False):
        return _series_false(df)
    c = _hvdm_components_bull(df)
    return _bool(df["hvd_fire_bull"]) & c["_m_cb1b"] & ~c["_m_pj1b"] & _master_gate(df, params)


def _hvdm_b_2of3_raw(df: pd.DataFrame, c: dict) -> pd.Series:
    cnt = (
        c["_m_pup1"].astype(int)
        + c["_m_rv1b"].astype(int)
        + c["_m_cb1b"].astype(int)
    )
    return _bool(df["hvd_fire_bull"]) & c["_m_pj1b"] & (cnt >= 2)


def _hvdm_b_3of3(df: pd.DataFrame, c: dict) -> pd.Series:
    return (
        _bool(df["hvd_fire_bull"]) & c["_m_pj1b"]
        & c["_m_pup1"] & c["_m_rv1b"] & c["_m_cb1b"]
    )


def detect_hvdm_pbj_pup_bull(df, params):
    """visible PBJ+PUP, suppressed when 2of3 dominates"""
    if not params.get("en_hvdm_pup_bull", False):
        return _series_false(df)
    c = _hvdm_components_bull(df)
    pbj_pup = _bool(df["hvd_fire_bull"]) & c["_m_pj1b"] & c["_m_pup1"]
    raw_2of3 = _hvdm_b_2of3_raw(df, c)
    return pbj_pup & ~raw_2of3 & _master_gate(df, params)


def detect_hvdm_pbj_rvol_bull(df, params):
    if not params.get("en_hvdm_rvol_bull", False):
        return _series_false(df)
    c = _hvdm_components_bull(df)
    pbj_rvol = _bool(df["hvd_fire_bull"]) & c["_m_pj1b"] & c["_m_rv1b"]
    raw_2of3 = _hvdm_b_2of3_raw(df, c)
    return pbj_rvol & ~raw_2of3 & _master_gate(df, params)


def detect_hvdm_pbj_cmb_bull(df, params):
    if not params.get("en_hvdm_cmb_bull", False):
        return _series_false(df)
    c = _hvdm_components_bull(df)
    pbj_cmb = _bool(df["hvd_fire_bull"]) & c["_m_pj1b"] & c["_m_cb1b"]
    raw_2of3 = _hvdm_b_2of3_raw(df, c)
    return pbj_cmb & ~raw_2of3 & _master_gate(df, params)


def detect_hvdm_2of3_bull(df, params):
    """2of3 = raw 2of3 AND NOT 3of3 (cascade exclusivity per Pine line 1610)"""
    if not params.get("en_hvdm_2of3_bull", False):
        return _series_false(df)
    c = _hvdm_components_bull(df)
    return _hvdm_b_2of3_raw(df, c) & ~_hvdm_b_3of3(df, c) & _master_gate(df, params)


def detect_hvdm_3of3_bull(df, params):
    if not params.get("en_hvdm_3of3_bull", False):
        return _series_false(df)
    c = _hvdm_components_bull(df)
    return _hvdm_b_3of3(df, c) & _master_gate(df, params)


# Bear mirrors

def _hvdm_r_2of3_raw(df: pd.DataFrame, c: dict) -> pd.Series:
    cnt = (
        c["_m_ppd1"].astype(int)
        + c["_m_rv1r"].astype(int)
        + c["_m_cb1r"].astype(int)
    )
    return _bool(df["hvd_fire_bear"]) & c["_m_pj1r"] & (cnt >= 2)


def _hvdm_r_3of3(df: pd.DataFrame, c: dict) -> pd.Series:
    return (
        _bool(df["hvd_fire_bear"]) & c["_m_pj1r"]
        & c["_m_ppd1"] & c["_m_rv1r"] & c["_m_cb1r"]
    )


def detect_hvdm_ppd_nopbj_bear(df, params):
    if not params.get("en_hvdm_ppd_bear", False):
        return _series_false(df)
    c = _hvdm_components_bear(df)
    return _bool(df["hvd_fire_bear"]) & c["_m_ppd1"] & ~c["_m_pj1r"] & _master_gate(df, params)


def detect_hvdm_rvol_nopbj_bear(df, params):
    if not params.get("en_hvdm_rvol_bear", False):
        return _series_false(df)
    c = _hvdm_components_bear(df)
    return _bool(df["hvd_fire_bear"]) & c["_m_rv1r"] & ~c["_m_pj1r"] & _master_gate(df, params)


def detect_hvdm_cmb_nopbj_bear(df, params):
    if not params.get("en_hvdm_cmb_bear", False):
        return _series_false(df)
    c = _hvdm_components_bear(df)
    return _bool(df["hvd_fire_bear"]) & c["_m_cb1r"] & ~c["_m_pj1r"] & _master_gate(df, params)


def detect_hvdm_pbj_ppd_bear(df, params):
    if not params.get("en_hvdm_ppd_bear", False):
        return _series_false(df)
    c = _hvdm_components_bear(df)
    pbj_ppd = _bool(df["hvd_fire_bear"]) & c["_m_pj1r"] & c["_m_ppd1"]
    raw_2of3 = _hvdm_r_2of3_raw(df, c)
    return pbj_ppd & ~raw_2of3 & _master_gate(df, params)


def detect_hvdm_pbj_rvol_bear(df, params):
    if not params.get("en_hvdm_rvol_bear", False):
        return _series_false(df)
    c = _hvdm_components_bear(df)
    pbj_rvol = _bool(df["hvd_fire_bear"]) & c["_m_pj1r"] & c["_m_rv1r"]
    raw_2of3 = _hvdm_r_2of3_raw(df, c)
    return pbj_rvol & ~raw_2of3 & _master_gate(df, params)


def detect_hvdm_pbj_cmb_bear(df, params):
    if not params.get("en_hvdm_cmb_bear", False):
        return _series_false(df)
    c = _hvdm_components_bear(df)
    pbj_cmb = _bool(df["hvd_fire_bear"]) & c["_m_pj1r"] & c["_m_cb1r"]
    raw_2of3 = _hvdm_r_2of3_raw(df, c)
    return pbj_cmb & ~raw_2of3 & _master_gate(df, params)


def detect_hvdm_2of3_bear(df, params):
    if not params.get("en_hvdm_2of3_bear", False):
        return _series_false(df)
    c = _hvdm_components_bear(df)
    return _hvdm_r_2of3_raw(df, c) & ~_hvdm_r_3of3(df, c) & _master_gate(df, params)


def detect_hvdm_3of3_bear(df, params):
    if not params.get("en_hvdm_3of3_bear", False):
        return _series_false(df)
    c = _hvdm_components_bear(df)
    return _hvdm_r_3of3(df, c) & _master_gate(df, params)


# ============================================================================
# Module exports
# ============================================================================

DETECTIONS: dict = {
    # === HV+D root + PBJ/PB co-occurrence (Pipeline A & B) — 6 ===
    "hvd_bull": detect_hvd_bull,
    "hvd_bear": detect_hvd_bear,
    "hvd_pb_bull": detect_hvd_pb_bull,
    "hvd_pbj_bull": detect_hvd_pbj_bull,
    "hvd_pb_bear": detect_hvd_pb_bear,
    "hvd_pbj_bear": detect_hvd_pbj_bear,

    # === USE plotshapes — bull (22) ===
    "bull_uuuu": detect_bull_uuuu,
    "bull_uuu": detect_bull_uuu,
    "bull_uu": detect_bull_uu,
    "alpha_strike_bull": detect_alpha_strike_bull,
    "foxtrot_bull": detect_foxtrot_bull,
    "omega_long_a": detect_omega_long_a,
    "od_bull": detect_od_bull,
    "disp_cons_bull2": detect_disp_cons_bull2,
    "disp_cons_bull3": detect_disp_cons_bull3,
    "golf_bull": detect_golf_bull,
    "paf_bull": detect_paf_bull,
    "cs1b": detect_cs1b,
    "cs2b": detect_cs2b,
    "cs3b": detect_cs3b,
    "cc_bull": detect_cc_bull,
    "lsc_bull": detect_lsc_bull,
    "bull_floor": detect_bull_floor,
    "bull_2nd_floor": detect_bull_2nd_floor,
    "hw_bull": detect_hw_bull,
    "super_bull": detect_super_bull,
    "sduper_bull": detect_sduper_bull,

    # === USE plotshapes — bear (21) ===
    "bear_uuuu": detect_bear_uuuu,
    "bear_uuu": detect_bear_uuu,
    "bear_uu": detect_bear_uu,
    "alpha_strike_bear": detect_alpha_strike_bear,
    "foxtrot_bear": detect_foxtrot_bear,
    "od_bear": detect_od_bear,
    "disp_cons_bear2": detect_disp_cons_bear2,
    "disp_cons_bear3": detect_disp_cons_bear3,
    "golf_bear": detect_golf_bear,
    "paf_bear": detect_paf_bear,
    "cs1r": detect_cs1r,
    "cs2r": detect_cs2r,
    "cs3r": detect_cs3r,
    "cc_bear": detect_cc_bear,
    "lsc_bear": detect_lsc_bear,
    "bear_rooftop": detect_bear_rooftop,
    "bear_penthouse": detect_bear_penthouse,
    "hw_bear": detect_hw_bear,
    "super_bear": detect_super_bear,
    "sduper_bear": detect_sduper_bear,

    # === Pipeline D — Triple Co-occurrence (4) ===
    "co_bull_pbj": detect_co_bull_pbj,
    "co_bull_pb": detect_co_bull_pb,
    "co_bear_pbj": detect_co_bear_pbj,
    "co_bear_pb": detect_co_bear_pb,

    # === NAG+ Bull (1, mine-only) ===
    "nag_plus_bull": detect_nag_plus_bull,

    # === Back-to-back HV+D (6, stateful) ===
    "b2b_hvd_bull": detect_b2b_hvd_bull,
    "b2b_hvd_bear": detect_b2b_hvd_bear,
    "b2b_hvd_pbj_bull": detect_b2b_hvd_pbj_bull,
    "b2b_hvd_pbj_bear": detect_b2b_hvd_pbj_bear,
    "b2b_hvd_pb_bull": detect_b2b_hvd_pb_bull,
    "b2b_hvd_pb_bear": detect_b2b_hvd_pb_bear,

    # === HV+D Momentum Co-Occurrence (16, label.new in Pine) ===
    "hvdm_pup_nopbj_bull": detect_hvdm_pup_nopbj_bull,
    "hvdm_rvol_nopbj_bull": detect_hvdm_rvol_nopbj_bull,
    "hvdm_cmb_nopbj_bull": detect_hvdm_cmb_nopbj_bull,
    "hvdm_pbj_pup_bull": detect_hvdm_pbj_pup_bull,
    "hvdm_pbj_rvol_bull": detect_hvdm_pbj_rvol_bull,
    "hvdm_pbj_cmb_bull": detect_hvdm_pbj_cmb_bull,
    "hvdm_2of3_bull": detect_hvdm_2of3_bull,
    "hvdm_3of3_bull": detect_hvdm_3of3_bull,
    "hvdm_ppd_nopbj_bear": detect_hvdm_ppd_nopbj_bear,
    "hvdm_rvol_nopbj_bear": detect_hvdm_rvol_nopbj_bear,
    "hvdm_cmb_nopbj_bear": detect_hvdm_cmb_nopbj_bear,
    "hvdm_pbj_ppd_bear": detect_hvdm_pbj_ppd_bear,
    "hvdm_pbj_rvol_bear": detect_hvdm_pbj_rvol_bear,
    "hvdm_pbj_cmb_bear": detect_hvdm_pbj_cmb_bear,
    "hvdm_2of3_bear": detect_hvdm_2of3_bear,
    "hvdm_3of3_bear": detect_hvdm_3of3_bear,
}

STATE_MACHINES: dict = {
    "B2BWalker": B2BWalker,
}

STUBBED: dict = {
    name: (fn.__doc__ or "").strip().splitlines()[0] if fn.__doc__ else "STUBBED"
    for name, fn in DETECTIONS.items()
    # crude — re-detected at call time; we hardcode the list of stubs here:
    if name in {
        "bull_uuuu", "bull_uuu", "bull_uu",
        "alpha_strike_bull", "foxtrot_bull", "omega_long_a", "od_bull",
        "disp_cons_bull2", "disp_cons_bull3",
        "golf_bull", "paf_bull",
        "cs1b", "cs2b", "cs3b",
        "cc_bull", "lsc_bull",
        "bull_floor", "bull_2nd_floor",
        "hw_bull", "super_bull", "sduper_bull",
        "bear_uuuu", "bear_uuu", "bear_uu",
        "alpha_strike_bear", "foxtrot_bear", "od_bear",
        "disp_cons_bear2", "disp_cons_bear3",
        "golf_bear", "paf_bear",
        "cs1r", "cs2r", "cs3r",
        "cc_bear", "lsc_bear",
        "bear_rooftop", "bear_penthouse",
        "hw_bear", "super_bear", "sduper_bear",
        "nag_plus_bull",
    }
}


if __name__ == "__main__":
    print(f"DETECTIONS:     {len(DETECTIONS)}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)}")
    print(f"STUBBED:        {len(STUBBED)}")
    print()
    print("Detection categories:")
    print(f"  HV+D root + PBJ/PB co-occ:    6")
    print(f"  USE plotshapes (bull):        21")
    print(f"  USE plotshapes (bear):        20")
    print(f"  Pipeline D triple co-occ:     4")
    print(f"  NAG+ Bull (mine-only):        1")
    print(f"  B2B HV+D (stateful):          6")
    print(f"  HV+D Momentum Co-Occ labels:  16")
    print(f"  TOTAL:                        {6+21+20+4+1+6+16}")
