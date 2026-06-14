#!/usr/bin/env python3
"""
Convert the HUB RVOL tiers to TRUE ROLLING (sliding) windows + remove the fixed/anchored
'RVOL Window' (constitutional violation: anchored window that waits N bars).

For each file (bull + bear):
  1. DELETE the old INDICATOR 9 rw_ block (anchored window: var windowStart + bar_index-start>=len).
  2. REPLACE the wrong single-bar rvt tiers with sliding windows using f_sum_true(event, N):
     - per-tier adjustable Rolling Window Bars (N) + Min Events (M).
     - event gated on barstate.isconfirmed -> NON-REPAINTING (closed bar only).
     - fire = leading edge of (sliding trailing-N count >= M); resets next bar automatically.
     - alias sRVOL_Window_raw := the new sliding 1x so composites/alerts keep working.
  3. Every plot title + alert name/message carries explicit Bull (bull file) / Bear (bear file).
Keeps the rvt_ interval-adaptive threshold subsystem (tfSec + tick fallback + tables) untouched.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
BULL = ROOT / "tick_friendly" / "HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine"
BEAR = ROOT / "bearish" / "HUB_1020_1153am_BEAR_Hub1020-Bear_v20260613_bearish_mirror.pine"

BULL_TAIL = '''// --- TRUE ROLLING (sliding) windows: fire when M events at the tier threshold land in trailing N bars ---
rvt_1x_winBars = input.int(20, "1x Rolling Window Bars", minval=1, group=grp_rvt)
rvt_1x_minEv = input.int(1, "1x Min Events in Rolling Window", minval=1, group=grp_rvt)
rvt_gs_winBars = input.int(20, "Grand Slam Rolling Window Bars", minval=1, group=grp_rvt)
rvt_gs_minEv = input.int(1, "Grand Slam Min Events in Rolling Window", minval=1, group=grp_rvt)
show_rvt_1x_plots = input.bool(true, "RVOL Window 1x Bull", group=grp_rvt)
show_rvt_gs_plots = input.bool(true, "RVOL Window Grand Slam Bull", group=grp_rvt)
rvt_evt_1x = barstate.isconfirmed and rvt_baseBull and rvt_normPrice >= rvt_th_1x and rvt_normPrice < rvt_th_gs
rvt_evt_gs = barstate.isconfirmed and rvt_baseBull and rvt_normPrice >= rvt_th_gs
rvt_cond_1x = f_sum_true(rvt_evt_1x, rvt_1x_winBars) >= rvt_1x_minEv
rvt_cond_gs = f_sum_true(rvt_evt_gs, rvt_gs_winBars) >= rvt_gs_minEv
bool sRVOL_Win_1x_raw = rvt_cond_1x and not rvt_cond_1x[1]
bool sRVOL_Win_GS_raw = rvt_cond_gs and not rvt_cond_gs[1]
bool sRVOL_Window_raw = sRVOL_Win_1x_raw
plotshape(sRVOL_Win_1x_raw and show_rvt_1x_plots, "RVOL Window 1x Bull", location=location.belowbar, style=shape.cross, size=size.small, color=color.new(color.lime, 0), text="1x")
plotshape(sRVOL_Win_GS_raw and show_rvt_gs_plots, "RVOL Window Grand Slam Bull", location=location.belowbar, style=shape.triangleup, size=size.large, color=color.new(color.aqua, 0), text="GS")
alertcondition(sRVOL_Win_1x_raw, "RVOL Window 1x Bull", "RVOL Window 1x Bull on {{ticker}}")
alertcondition(sRVOL_Win_GS_raw, "RVOL Window Grand Slam Bull", "RVOL Window Grand Slam Bull on {{ticker}}")'''

BEAR_TAIL = '''// --- TRUE ROLLING (sliding) windows: fire when M events at the tier threshold land in trailing N bars ---
rvt_1x_winBars = input.int(20, "1x Rolling Window Bars", minval=1, group=grp_rvt)
rvt_1x_minEv = input.int(1, "1x Min Events in Rolling Window", minval=1, group=grp_rvt)
rvt_moab_winBars = input.int(20, "MOAB Rolling Window Bars", minval=1, group=grp_rvt)
rvt_moab_minEv = input.int(1, "MOAB Min Events in Rolling Window", minval=1, group=grp_rvt)
show_rvt_1x_plots = input.bool(true, "RVOL Window 1x Bear", group=grp_rvt)
show_rvt_moab_plots = input.bool(true, "RVOL Window MOAB Bear", group=grp_rvt)
rvt_evt_1x = barstate.isconfirmed and rvt_baseBear and rvt_normPrice >= rvt_th_1x and rvt_normPrice < rvt_th_gs
rvt_evt_moab = barstate.isconfirmed and rvt_baseBear and rvt_normPrice >= rvt_th_gs
rvt_cond_1x = f_sum_true(rvt_evt_1x, rvt_1x_winBars) >= rvt_1x_minEv
rvt_cond_moab = f_sum_true(rvt_evt_moab, rvt_moab_winBars) >= rvt_moab_minEv
bool sRVOL_Win_1x_raw = rvt_cond_1x and not rvt_cond_1x[1]
bool sRVOL_Win_MOAB_raw = rvt_cond_moab and not rvt_cond_moab[1]
bool sRVOL_Window_raw = sRVOL_Win_1x_raw
plotshape(sRVOL_Win_1x_raw and show_rvt_1x_plots, "RVOL Window 1x Bear", location=location.abovebar, style=shape.cross, size=size.small, color=color.new(color.rgb(255, 87, 34), 0), text="1x")
plotshape(sRVOL_Win_MOAB_raw and show_rvt_moab_plots, "RVOL Window MOAB Bear", location=location.abovebar, style=shape.triangledown, size=size.large, color=color.new(color.rgb(199, 0, 57), 0), text="MOAB")
alertcondition(sRVOL_Win_1x_raw, "RVOL Window 1x Bear", "RVOL Window 1x Bear on {{ticker}}")
alertcondition(sRVOL_Win_MOAB_raw, "RVOL Window MOAB Bear", "RVOL Window MOAB Bear on {{ticker}}")'''


def process(path, tail, end_token):
    lines = path.read_text().split("\n")
    # 1. delete the anchored rw_ block: box-header (INDICATOR 9) through the WIN plot (show_rw_plots)
    i_hdr = next(i for i, l in enumerate(lines) if "INDICATOR 9: RVOL ROLLING WINDOW" in l)
    i_win = next(i for i, l in enumerate(lines) if "and show_rw_plots" in l)
    del lines[i_hdr - 1: i_win + 1]
    # 2. replace the wrong single-bar tail (show_rvt_1x_plots ... last tier alertcondition)
    i_ts = next(i for i, l in enumerate(lines) if l.startswith("show_rvt_1x_plots = input.bool"))
    i_te = next(i for i, l in enumerate(lines) if l.startswith(end_token))
    lines[i_ts: i_te + 1] = tail.split("\n")
    out = "\n".join(lines)
    bad = [(i + 1, repr(c)) for i, ln in enumerate(out.split("\n")) for c in ln if ord(c) > 0x7F and c not in "—×³≥ΔΣ★"]
    path.write_text(out)
    print(f"{path.name}: removed rw_ block [{i_hdr-1}..{i_win}], replaced tail -> sliding windows")


process(BULL, BULL_TAIL, "alertcondition(sRVOL_Win_GS_raw")
process(BEAR, BEAR_TAIL, "alertcondition(sRVOL_Win_MOAB_raw")
