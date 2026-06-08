"""HV NRA (hv_to_1k) — detection fire-matrix core (Pine v5 -> Python, faithful).

Python is a Python tick  /  Python is a Python time-based  (shared substrate)

SOURCE OF TRUTH:
  "Pine Indicators NOT transformed yet/June 7/hv to 1k_06_07_124pm.txt"
  mirrored corrected tick-friendly copy:
  "sources/pine_studies/plots/hv_to_1k/hv_to_1k.pine"
  indicator("HV(100/200/300/400/500/600/700/800/900/1K/HEV/HS) NRA", overlay=true)

WHY THIS IS A FULL (NON-STUB) PORT:
  Tick-friendliness landmine scan of the source (RE10023 class) found:
    relativeVolume( : 0   timeframe.change( : 0   request.security( : 0
    import TradingView : 0   ta.* : ta.highest ONLY (x12, bar-0 safe).
  Every detection plot is built from pure OHLCV math + the bar's wall-clock date
  (Tier A/B in the import-decoupling tree). There is NO Tier-C/Tier-D surface, so
  there is NOTHING to stub. The whole indicator ports construct-for-construct.
  (No shim needed: the source has zero relativeVolume calls.)

PINE -> PYTHON SEMANTIC MAP (verbatim from the source):
  bool is{N}Bar = volume[1] == ta.highest(volume, N)[1]        # N in 100..1000
  var float maxVolEver = 0.0
  bool isHEV = false ; if volume[1] > maxVolEver: maxVolEver := volume[1]; isHEV := true
  isHotSpot = opEx | qtrEnd | russell | taxLoss | janEff | hfRedeem   # date[1] windows
  Priority ladder (only the single highest active marker paints; HS independent):
    plot_HEV  = useHEV  & isHEV
    plot_1000 = use1000 & is1000Bar & !isHEV
    plot_900  = use900  & is900Bar  & !is1000Bar & !isHEV
    ... (each lower tier suppressed by ALL higher tiers AND isHEV) ...
    plot_100  = use100  & is100Bar  & !is200..!is1000Bar & !isHEV
    plot_HS   = useHS   & isHotSpot
  activeVolSignals = count(is{N}Bar) + isHEV
  signalStates[0..11] = is100..is1000, isHEV, isHotSpot

NON-REPAINTING FIDELITY:
  Pine compares the PRIOR CONFIRMED bar: `volume[1] == ta.highest(volume,N)[1]`.
  In Python (oldest-first, cursor i), that is: compare v[i-1] to
  highest(v,N) evaluated at index i-1. The condition `is{N}Bar` is the boolean
  Pine stores at bar i (alertcondition/aggregation read it at i). Pine then
  PAINTS the marker with offset=-1, i.e. on bar i-1 (the described bar). We keep
  the CONDITION-bar convention (bar i) for the fire matrix because that is the
  exact boolean the alert + aggregation use; the paint offset is cosmetic.

OUTPUT CONTRACT (per-bar, oldest-first, aligned 1:1 with the bar series):
  Detection plots (the deliverable fire matrix), each a 0/1 list:
    plot_HEV, plot_1000, plot_900, ..., plot_100, plot_HS
  Raw conditions (feed the priority ladder + aggregation), each 0/1:
    is100..is1000, isHEV, isHotSpot
  Numeric levels (data-window numerics), each a float|None list:
    lvl_HEV, lvl_1000..lvl_100   -> the triggering volume[1] when the plot fires
    lvl_HS                       -> count of active Hot Spot windows (0..6)
    activeVolSignals             -> int count
  ts : bar OPEN timestamps (epoch ms).

This module is imported by BOTH the tick and time wrappers; identical logic, the
only difference is the runtime GRAIN of the bars fed in.
"""
from __future__ import annotations

import datetime as _dt
import os
import sys
from dataclasses import dataclass
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nine_nines_common import Bar  # noqa: E402

# Pine ta.highest mirror (bar-0 safe: uses the AVAILABLE window before N bars).
from _nn_harness import highest, columns  # noqa: E402


# --- inputs (Pine input.bool defaults; every threshold/toggle a parameter) ---
@dataclass(frozen=True)
class HVInputs:
    use100: bool = True       # input.bool(true, "Show 100-Bar High Vol")
    use200: bool = True
    use300: bool = True
    use400: bool = True
    use500: bool = True
    use600: bool = True
    use700: bool = True
    use800: bool = True
    use900: bool = True
    use1000: bool = True
    useHEV: bool = True       # input.bool(true, "Show All-Time High Vol (HEV)")
    useHS: bool = True        # input.bool(true, "Show Hot Spot Signals")

    def use(self, N: int) -> bool:
        return getattr(self, f"use{N}")


# the ten rolling-window high-volume lengths (Pine ta.highest(volume, N))
LENS = (100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)

# Pine dayofweek constants (sunday=1 .. saturday=7)
_DOW_SUNDAY = 1
_DOW_MONDAY = 2
_DOW_TUESDAY = 3
_DOW_WEDNESDAY = 4
_DOW_THURSDAY = 5
_DOW_FRIDAY = 6
_DOW_SATURDAY = 7


def _pine_date_parts(ts_ms: int) -> tuple[int, int, int]:
    """(month, dayofmonth, dayofweek) for a bar timestamp, in Pine conventions.

    Pine dayofweek: Sunday=1, Monday=2, ... Saturday=7.
    Python datetime.weekday(): Monday=0 ... Sunday=6.
    Map: monday(0)->2 ... saturday(5)->7 ; sunday(6)->1.
    """
    d = _dt.datetime.fromtimestamp(ts_ms / 1000, tz=_dt.timezone.utc)
    wd = d.weekday()                      # Mon=0 .. Sun=6
    pine_dow = _DOW_SUNDAY if wd == 6 else wd + 2
    return d.month, d.day, pine_dow


def _hotspot_windows(month: int, dom: int, dow: int) -> list[bool]:
    """The six calendar windows, each evaluated on the PRIOR bar's date.
    Returned in source order [opEx, qtrEnd, russell, taxLoss, janEff, hfRedeem].
    Verbatim thresholds from the Pine source (kept as constants here)."""
    op_ex = (10 <= dom <= 17) and (_DOW_MONDAY <= dow <= _DOW_WEDNESDAY)
    qtr_end = (month in (3, 6, 9, 12)) and (23 <= dom <= 27)
    russell = (month == 6) and (19 <= dom <= 24)
    tax_loss = (month == 12) and (21 <= dom <= 26)
    jan_eff = (month == 12) and (27 <= dom <= 30)
    hf_redeem = (month in (5, 11)) and (10 <= dom <= 13)
    return [op_ex, qtr_end, russell, tax_loss, jan_eff, hf_redeem]


def compute(bars: Sequence[Bar], inp: HVInputs | None = None) -> dict:
    """Faithful HV NRA detection fire-matrix on an oldest-first bar series.

    Returns the full output contract documented in the module docstring.
    """
    inp = inp or HVInputs()
    o, h, l, c, v, ts = columns(bars)
    n = len(bars)

    # ta.highest(volume, N) per length (vector, oldest-first; None until warm).
    hi = {N: highest(v, N) for N in LENS}

    # ---- raw conditions: is{N}Bar = volume[1] == ta.highest(volume,N)[1] -----
    is_bar = {N: [False] * n for N in LENS}
    for N in LENS:
        hiN = hi[N]
        for i in range(1, n):
            prev_hi = hiN[i - 1]            # ta.highest(volume,N)[1]
            if prev_hi is None:
                continue                     # Pine na -> comparison na -> false
            is_bar[N][i] = (v[i - 1] == prev_hi)

    # ---- isHEV: running max of CONFIRMED (prior) bars; strict new ATH --------
    # Pine: var maxVolEver=0; if volume[1] > maxVolEver: maxVolEver:=volume[1]; isHEV:=true
    is_hev = [False] * n
    max_vol_ever = 0.0
    for i in range(n):
        prev = v[i - 1] if i >= 1 else None
        if prev is not None and prev > max_vol_ever:
            max_vol_ever = prev
            is_hev[i] = True

    # ---- isHotSpot: calendar windows on the PRIOR bar's date -----------------
    hs_window_count = [0] * n               # how many of the 6 windows are active
    is_hotspot = [False] * n
    for i in range(1, n):
        month, dom, dow = _pine_date_parts(ts[i - 1])   # dayofmonth[1], etc.
        wins = _hotspot_windows(month, dom, dow)
        cnt = sum(1 for w in wins if w)
        hs_window_count[i] = cnt
        is_hotspot[i] = cnt > 0

    # ---- priority ladder (the detection plots that actually paint) -----------
    # Priority: HEV > 1000 > 900 > ... > 100. Only the single highest paints.
    # plot_{N} = use{N} & is{N}Bar & !is{higher}Bar... & !isHEV
    # Hot Spot is independent (always paints when active & enabled).
    plot_HEV = [0] * n
    plot_N = {N: [0] * n for N in LENS}
    plot_HS = [0] * n
    # numeric levels
    lvl_HEV: list = [None] * n
    lvl_N: dict = {N: [None] * n for N in LENS}
    lvl_HS: list = [None] * n
    active = [0] * n

    desc = tuple(reversed(LENS))            # 1000, 900, ... 100 (high->low)
    for i in range(n):
        prev_vol = v[i - 1] if i >= 1 else None

        hev = inp.useHEV and is_hev[i]
        plot_HEV[i] = 1 if hev else 0
        if hev:
            lvl_HEV[i] = prev_vol

        # higher-tier suppression: a tier paints only if NO higher tier (or HEV)
        # is the active is{}Bar. Mirror the exact `not isXBar` chain in the source.
        higher_active = is_hev[i]
        for N in desc:
            fires = inp.use(N) and is_bar[N][i] and (not higher_active)
            plot_N[N][i] = 1 if fires else 0
            if fires:
                lvl_N[N][i] = prev_vol
            # once this tier's raw condition is true it suppresses all lower tiers
            if is_bar[N][i]:
                higher_active = True

        hsp = inp.useHS and is_hotspot[i]
        plot_HS[i] = 1 if hsp else 0
        if hsp:
            lvl_HS[i] = hs_window_count[i]

        # activeVolSignals = count(is{N}Bar) + isHEV  (Pine, unfiltered)
        active[i] = sum(1 for N in LENS if is_bar[N][i]) + (1 if is_hev[i] else 0)

    out: dict = {"ts": list(ts)}

    # detection plots (the fire matrix deliverable)
    out["plot_HEV"] = plot_HEV
    for N in LENS:
        out[f"plot_{N}"] = plot_N[N]
    out["plot_HS"] = plot_HS

    # raw conditions (feed ladder + aggregation; exported for combo studies)
    for N in LENS:
        out[f"is{N}"] = [1 if x else 0 for x in is_bar[N]]
    out["isHEV"] = [1 if x else 0 for x in is_hev]
    out["isHotSpot"] = [1 if x else 0 for x in is_hotspot]

    # numeric levels (data-window numerics)
    out["lvl_HEV"] = lvl_HEV
    for N in LENS:
        out[f"lvl_{N}"] = lvl_N[N]
    out["lvl_HS"] = lvl_HS

    # aggregation
    out["activeVolSignals"] = active
    return out


# detection-plot inventory (Stage-2): id -> (descriptor, level key)
DETECTION_PLOTS = {
    "plot_HEV": ("All-Time High Volume (HEV) — highest priority", "lvl_HEV"),
    "plot_1000": ("1000-Bar High Volume", "lvl_1000"),
    "plot_900": ("900-Bar High Volume", "lvl_900"),
    "plot_800": ("800-Bar High Volume", "lvl_800"),
    "plot_700": ("700-Bar High Volume", "lvl_700"),
    "plot_600": ("600-Bar High Volume", "lvl_600"),
    "plot_500": ("500-Bar High Volume", "lvl_500"),
    "plot_400": ("400-Bar High Volume", "lvl_400"),
    "plot_300": ("300-Bar High Volume", "lvl_300"),
    "plot_200": ("200-Bar High Volume", "lvl_200"),
    "plot_100": ("100-Bar High Volume", "lvl_100"),
    "plot_HS": ("Hot Spot — approaching known high-volume date", "lvl_HS"),
}
