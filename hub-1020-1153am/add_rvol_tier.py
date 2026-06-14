#!/usr/bin/env python3
"""
Add the interval-adaptive RVOL TIER LADDER to the HUB bull + bear.

Ports the proven mechanism from Heavy Weapons NRA (tick-friendly build):
  - tfSec from timeframe.in_seconds(); tick charts fall back to 10s bucket
    (tickOverride input to pin a different bucket) — Anish's own convention.
  - f_rvt_1x / f_rvt_gs: per-interval threshold tables (verbatim, his tuned values).
  - tier fire tolerance (default 0.90 = 10% below nominal) as an input.
  - RVOL measure = abs(close-open)/avgSpike (same engine the HUB already uses).
Tiers: 1x band [th_1x, th_gs) + Grand Slam(bull, >=th_gs) / MOAB(bear, >=th_gs).
Bull file gets bull tiers; bear file gets bear tiers (differentiated: Bear names,
flipped location vs the bull, warm colors, Bear alerts).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
BULL = ROOT / "tick_friendly" / "HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine"
BEAR = ROOT / "bearish" / "HUB_1020_1153am_BEAR_Hub1020-Bear_v20260613_bearish_mirror.pine"
MARKER = "plotshape(sRVOL_Window_raw"   # insert the subsystem right after the RVOL Window plot

SUBSYSTEM = '''
// #############################################################################
// ###  RVOL TIER LADDER - interval-adaptive (ported from Heavy Weapons NRA)  ###
// ###  Threshold auto-picks per chart interval; TICK charts fall back to the  ###
// ###  10s bucket (rvt_tickOverride pins another). 1x band + Grand Slam/MOAB. ###
// #############################################################################
grp_rvt = "RVOL TIER LADDER (interval-adaptive)"
rvt_tickOverride = input.int(0, "Tick threshold-bucket seconds (0=auto 10s)", minval=0, group=grp_rvt, tooltip="On tick charts timeframe.in_seconds()=0. Set >0 to PIN the per-interval RVOL bucket (e.g. 10/30/60). 0 = auto fallback to tightest sub-minute bucket.")
rvt_tol = input.float(0.90, "Tier fire tolerance (x per-interval threshold)", minval=0.1, step=0.01, group=grp_rvt, tooltip="Fire a tier when RVOL >= this x the per-interval threshold. 0.90 = 10% below nominal.")
rvt_avgLength = input.int(30, "RVOL Look-back", minval=1, group=grp_rvt)
rvt_smaLength = input.int(20, "RVOL SMA Length", minval=1, group=grp_rvt)
int RVT_TICK_FALLBACK_SEC = 10
float rvt_tfSecRaw = timeframe.in_seconds(timeframe.period)
bool rvt_isTick = na(rvt_tfSecRaw) or rvt_tfSecRaw <= 0
rvt_tfSec = rvt_tickOverride > 0 ? rvt_tickOverride : (rvt_isTick ? RVT_TICK_FALLBACK_SEC : int(rvt_tfSecRaw))
f_rvt_1x(_s) =>
\tfloat th = _s <= 10 ? 38.0 : _s <= 15 ? 33.0 : _s <= 30 ? 28.0 : _s <= 45 ? 23.0 : _s <= 60 ? 20.0 : _s <= 120 ? 19.0 : _s <= 180 ? 17.0 : _s <= 240 ? 16.0 : _s <= 300 ? 15.0 : _s <= 360 ? 14.0 : _s <= 420 ? 12.0 : _s <= 480 ? 11.0 : _s <= 540 ? 10.0 : _s <= 600 ? 10.0 : _s <= 900 ? 8.4 : _s <= 1800 ? 6.9 : _s <= 3600 ? 5.9 : _s <= 7200 ? 3.0 : 1.8
\tth
f_rvt_gs(_s) =>
\tfloat th = _s <= 10 ? 114.0 : _s <= 15 ? 99.0 : _s <= 30 ? 84.0 : _s <= 45 ? 69.0 : _s <= 60 ? 35.0 : _s <= 300 ? 35.0 : _s <= 600 ? 25.0 : _s <= 900 ? 20.0 : _s <= 3600 ? 10.0 : 8.0
\tth
float rvt_th_1x = f_rvt_1x(rvt_tfSec) * rvt_tol
float rvt_th_gs = f_rvt_gs(rvt_tfSec) * rvt_tol
rvt_spike = math.abs(close - open)
rvt_normPrice = rvt_spike / nz(ta.sma(rvt_spike, rvt_avgLength)[1], 1.0)
rvt_normVol = volume / nz(ta.sma(volume, rvt_avgLength)[1], 1.0)
rvt_diff = rvt_normPrice - rvt_normVol
rvt_pos = rvt_diff > 0 ? rvt_diff : na
rvt_smaDiff = ta.sma(rvt_pos, rvt_smaLength)
rvt_baseBull = close > open and nz(rvt_pos) > nz(rvt_smaDiff)
rvt_baseBear = close < open and nz(rvt_pos) > nz(rvt_smaDiff)
'''

BULL_TAIL = '''show_rvt_1x_plots = input.bool(true, "RVOL Window 1x Bull", group=grp_rvt)
show_rvt_gs_plots = input.bool(true, "RVOL Window Grand Slam", group=grp_rvt)
bool sRVOL_Win_1x_raw = barstate.isconfirmed and rvt_baseBull and rvt_normPrice >= rvt_th_1x and rvt_normPrice < rvt_th_gs
bool sRVOL_Win_GS_raw = barstate.isconfirmed and rvt_baseBull and rvt_normPrice >= rvt_th_gs
plotshape(sRVOL_Win_1x_raw and show_rvt_1x_plots, "RVOL Window 1x Bull", location=location.belowbar, style=shape.cross, size=size.small, color=color.new(color.lime, 0), text="1x")
plotshape(sRVOL_Win_GS_raw and show_rvt_gs_plots, "RVOL Window Grand Slam", location=location.belowbar, style=shape.triangleup, size=size.large, color=color.new(color.aqua, 0), text="GS")
alertcondition(sRVOL_Win_1x_raw, "RVOL Window 1x Bull", "RVOL Window 1x Bull on {{ticker}}")
alertcondition(sRVOL_Win_GS_raw, "RVOL Window Grand Slam", "RVOL Window Grand Slam on {{ticker}}")
'''

BEAR_TAIL = '''show_rvt_1x_plots = input.bool(true, "RVOL Window 1x Bear", group=grp_rvt)
show_rvt_moab_plots = input.bool(true, "RVOL Window MOAB", group=grp_rvt)
bool sRVOL_Win_1x_raw = barstate.isconfirmed and rvt_baseBear and rvt_normPrice >= rvt_th_1x and rvt_normPrice < rvt_th_gs
bool sRVOL_Win_MOAB_raw = barstate.isconfirmed and rvt_baseBear and rvt_normPrice >= rvt_th_gs
plotshape(sRVOL_Win_1x_raw and show_rvt_1x_plots, "RVOL Window 1x Bear", location=location.abovebar, style=shape.cross, size=size.small, color=color.new(color.rgb(255, 87, 34), 0), text="1x")
plotshape(sRVOL_Win_MOAB_raw and show_rvt_moab_plots, "RVOL Window MOAB", location=location.abovebar, style=shape.triangledown, size=size.large, color=color.new(color.rgb(199, 0, 57), 0), text="MOAB")
alertcondition(sRVOL_Win_1x_raw, "RVOL Window 1x Bear", "RVOL Window 1x Bear on {{ticker}}")
alertcondition(sRVOL_Win_MOAB_raw, "RVOL Window MOAB", "RVOL Window MOAB on {{ticker}}")
'''


def insert(path, tail):
    text = path.read_text()
    if "grp_rvt" in text:
        print(f"SKIP (already has RVOL tier ladder): {path.name}")
        return
    lines = text.split("\n")
    idx = next((i for i, ln in enumerate(lines) if MARKER in ln), None)
    if idx is None:
        raise SystemExit(f"MARKER not found in {path.name}")
    block = (SUBSYSTEM + tail).split("\n")
    lines[idx + 1:idx + 1] = block
    path.write_text("\n".join(lines))
    print(f"INSERTED after line {idx + 1} ({MARKER}) in {path.name}: +{len(block)} lines")


insert(BULL, BULL_TAIL)
insert(BEAR, BEAR_TAIL)
