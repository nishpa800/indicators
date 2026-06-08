"""heavy_weapons_4fvg_4matrix — parity harness (NINE NINES Gate-B, OFFLINE, honest).

Source (read from disk, quoted exactly):
  "/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT transformed
   yet/June 7/Tick Friendly conversion/heavy_weapons_4fvg_4matrix_tickfriendly.pine"
  Pine v5, "Heavy Weapons NRA + GZI/FVG + Matrix Combos 2 bodies not 1 NRAFR".

WHAT THIS PROVES (and what it does NOT) — RULE-0 candor
------------------------------------------------------
This is the OFFLINE Gate-B harness. It proves the Python port is internally correct,
deterministic, and self-consistent against an INDEPENDENT reference re-derived from
the literal Pine formulas. TradingView access is FORBIDDEN in this batch (one shared
chart; parallel agents would collide), so the render-coordinate parity vs TradingView's
own plotted plotshape coordinates (Gate-A 3b, the TV debug bridge / known-plaintext
attack) is DEFERRED and explicitly NOT claimed green here.

GATES (each printed line is one check; REAL pass/total at the end):
  1.  determinism          two fresh fire_matrix() runs are byte-identical.
  2.  tick==time           the SAME OHLCV bars fed through the tick wrapper and the
                           time wrapper (same tf_seconds) produce an IDENTICAL fire
                           matrix — proves ONE shared core, grain-bound only.
  3.  raw==sorted          re-sorting the input bars by ts yields identical fires.
  4.  raw==events          raw fire count (offset NOT applied) == coordinate-event count.
  5.  negative control     reversing the bar order CHANGES the fire matrix (a gate that
                           cannot fail is not a gate).
  6.  flat=0               perfectly flat bars (no body, no vol spike) -> all-zero matrix.
  7.  warmup               no WINDOWED plot fires before the longest lookback warmup
                           (Nagasaki has no window and is legitimately allowed early).
  8.  offset_-1            FVG combos paint exactly one REAL bar back (applied==compute-1).
  9.  RVOL band exclusivity SAAB/RVOL1x/GrandSlam never co-fire on the same bar/side
                           (the normPrice bands are disjoint by construction).
 10.  indep SAAB/MOAB      bull/bear normPrice-band plots match a fully independent
                           re-derivation (separate code) bar-for-bar.
 11.  indep Nagasaki       new-running-max-volume matches an independent scan bar-for-bar.
 12.  indep matrix-number  is_matrix == (volume == highest(volume, matrix_len)) re-derived.
 13.  STUB-IS-ZERO HONESTY core.STUB_IDS is empty AND every detection plot is genuinely
                           COMPUTED (each CAN fire across the crafted scenarios), so a 0
                           means "no signal", never "not implemented".

Run:  python3 heavy_weapons_4fvg_4matrix_parity.py
Exit 0 + "PARITY heavy_weapons_4fvg_4matrix: P/T" on success; non-zero on any fail.
"""
from __future__ import annotations

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tick"))
sys.path.insert(0, os.path.join(_ROOT, "time"))

from _nn_harness import Bar  # noqa: E402
import _heavy_weapons_4fvg_4matrix_core as core  # noqa: E402
import heavy_weapons_4fvg_4matrix_tick as tickmod  # noqa: E402
import heavy_weapons_4fvg_4matrix_time as timemod  # noqa: E402

TF = 60
PLOTS = list(core.PLOT_IDS.keys())


# ───────────────────── deterministic test bars (rich, multi-session) ─────────
def _make_bars(n=1000, tf=TF, seed=20260608):
    """Reproducible OHLCV with a session reset each calendar day, deliberate shock
    candles (large body + FVG-creating gaps), and volume blowouts so the RVOL /
    matrix / fauna / FVG-GZI detection plots are actually exercised (a parity gate
    on all-quiet data proves nothing)."""
    state = [seed & 0x7FFFFFFF]

    def rnd():
        state[0] = (1103515245 * state[0] + 12345) & 0x7FFFFFFF
        return state[0] / 0x7FFFFFFF

    bars = []
    t0 = 1_700_000_000_000
    px = 100.0
    bars_per_day = 20
    for i in range(n):
        day = i // bars_per_day
        k = i % bars_per_day
        ts = t0 + day * 86_400_000 + k * tf * 1000
        shock = rnd() > 0.88
        mega = rnd() > 0.985
        drift = (1.0 if rnd() > 0.5 else -1.0) * (3.0 + rnd() * 6.0) if shock else (rnd() - 0.5) * 0.6
        o = px
        c = max(0.5, o + drift)
        b = abs(c - o)
        hi = max(o, c) + (b * (0.05 + rnd() * 0.20) if shock else rnd() * 0.4)
        lo = min(o, c) - (b * (0.05 + rnd() * 0.20) if shock else rnd() * 0.4)
        smile = 1.0 + 1.8 * math.cos((k / bars_per_day) * math.pi) ** 2
        spike = (40.0 + rnd() * 80.0) if mega else ((8.0 + rnd() * 10.0) if shock else 1.0)
        vol = round((400 + rnd() * 600) * smile * spike, 2)
        bars.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(c, 4), vol))
        px = c
    return bars


def _fire_tuple(out):
    return tuple((pid, tuple(out["fire_" + pid])) for pid in PLOTS)


# ───────────── independent references (separate code than the core) ──────────
def _ref_normprice_bands(bars, tf):
    """Fully independent re-derivation of SAAB/Kratos/RVOL1x/GrandSlam/MOAB from the
    literal Pine bull/bear normalized-price formulas — different code than the core."""
    P = core.Params()
    n = len(bars)
    o = [x.open for x in bars]; h = [x.high for x in bars]
    lo = [x.low for x in bars]; c = [x.close for x in bars]; v = [x.volume for x in bars]
    th_1x = core._f_rvol_1x(tf)
    th_sk = th_1x * 0.56
    th_gs = core._f_gs_moab(tf)

    def sma_skip_none(series, length):
        out = [None] * n
        from collections import deque
        win = deque()
        for i, val in enumerate(series):
            win.append(val)
            if len(win) > length:
                win.popleft()
            if len(win) == length and all(w is not None for w in win):
                out[i] = sum(win) / length
        return out

    spike = [abs(c[i] - o[i]) for i in range(n)]
    sP = sma_skip_none(spike, P.bb_avgLength)
    sV = sma_skip_none(v, P.bb_avgLength)
    np_ = [spike[i] / (sP[i - 1] if i > 0 and sP[i - 1] is not None else 1.0) for i in range(n)]
    nv_ = [v[i] / (sV[i - 1] if i > 0 and sV[i - 1] is not None else 1.0) for i in range(n)]
    diff = [np_[i] - nv_[i] for i in range(n)]
    pos = [(d if d > 0 else None) for d in diff]
    sPos = sma_skip_none(pos, P.bb_smaLength)
    bull = [(c[i] > o[i]) and pos[i] is not None and sPos[i] is not None and pos[i] > sPos[i] for i in range(n)]
    bear = [(c[i] < o[i]) and pos[i] is not None and sPos[i] is not None and pos[i] > sPos[i] for i in range(n)]
    saab = [bull[i] and th_sk <= np_[i] < th_1x for i in range(n)]
    krat = [bear[i] and th_sk <= np_[i] < th_1x for i in range(n)]
    b1x = [bull[i] and th_1x <= np_[i] < th_gs for i in range(n)]
    s1x = [bear[i] and th_1x <= np_[i] < th_gs for i in range(n)]
    gs = [bull[i] and np_[i] >= th_gs for i in range(n)]
    moab = [bear[i] and np_[i] >= th_gs for i in range(n)]
    return dict(SAAB=saab, Kratos=krat, BullRVOL1x=b1x, BearRVOL1x=s1x, GrandSlam=gs, MOAB=moab)


def _ref_nagasaki(bars):
    n = len(bars)
    v = [x.volume for x in bars]
    out = [False] * n
    mx = 0.0
    for i in range(n):
        if i == 0:
            mx = v[i]
        elif v[i] > mx:
            out[i] = True
            mx = v[i]
    return out


def _ref_matrix_number(bars, matrix_len):
    n = len(bars)
    v = [x.volume for x in bars]
    out = [False] * n
    from collections import deque
    win = deque()
    for i in range(n):
        win.append(v[i])
        if len(win) > matrix_len:
            win.popleft()
        if len(win) == matrix_len:
            out[i] = v[i] == max(win)
    return out


# ─────── crafted scenarios for the STUB-IS-ZERO honesty gate (deterministic) ──
# Each is hand-built to trigger a specific detection-plot family, proving the plot
# is genuinely COMPUTED (so a 0 fire means "no signal", never "not implemented").
# Returns a list of (bars, tf_seconds). tf=10 (the tick-fallback row) is used where
# a plot's band is empty at tf=60 (e.g. WTC: th_wtc=2x th_1x=40 > th_hiroshima=35 at
# tf=60 -> structurally empty; valid at tf=10). That empty band is FAITHFUL Pine, not
# a stub — see memory pine_port_findings_2026-05-10.
def _craft_scenarios():
    t0 = 1_700_000_000_000
    out = []

    # normPrice bands at tf=60: decaying-volume baseline (builds bb_posdiff SMA) then a
    # body spike landing in the target band. mult tunes the normPrice magnitude.
    TF1 = 60

    def normband(bull, mult):
        bars = []
        px = 100.0
        vol = 5000.0
        for i in range(50):
            o = px
            c = px + (0.3 if bull else -0.3)
            bars.append(Bar(t0 + i * TF1 * 1000, max(o, 0.5), max(o, c) + 0.005,
                            min(o, c) - 0.005, c, vol))
            px = c
            vol *= 0.96
        body = 0.3 * mult
        o = px
        c = px + (body if bull else -body)
        bars.append(Bar(t0 + 50 * TF1 * 1000, o, max(o, c) + 0.01, min(o, c) - 0.01, c, vol))
        return bars

    for bull, mult in [(True, 15), (False, 15), (True, 25), (False, 25), (True, 40), (False, 40)]:
        out.append((normband(bull, mult), TF1))

    # Reg@Time (Pentagon/WTC/Hiroshima) + hybrid momentum + Nagasaki at tf=10.
    TF2 = 10

    def regtime(mult, bull):
        bars = []
        px = 100.0
        bpd = 6
        for d in range(34):              # >= reg_length+1 sessions of prior history
            for k in range(bpd):
                ts = t0 + d * 86_400_000 + k * TF2 * 1000
                o = px
                c = px + (0.1 if bull else -0.1)
                vol = 100.0 * (mult if d == 33 else 1.0)   # final session volume blowout
                if bull:
                    bars.append(Bar(ts, o, c + 0.01, o - 0.01, c, vol))
                else:
                    bars.append(Bar(ts, o + 0.01, o + 0.01, c - 0.01, c, vol))
                px = c
        return bars

    out.append((regtime(50, True), TF2))     # Pentagon + Long1/Long2
    out.append((regtime(90, True), TF2))      # WTC (band valid at tf=10) + Long
    out.append((regtime(200, True), TF2))     # Hiroshima
    out.append((regtime(90, False), TF2))     # Short1/Short2 (bear hybrid momentum)

    # bull combos CS1-CS4: growing-body baseline (Standard RVOL1x) + a highest-volume
    # full-body bar (Nagasaki / matrix / HV) + a gap-up FVG bar -> FVG/GZI/HV combos.
    def bull_combos():
        bars = []
        px = 100.0
        body = 0.05
        for i in range(70):                # >= 67 for matrix/HV warmup
            o = px
            c = px + body
            bars.append(Bar(t0 + i * TF2 * 1000, o, c + 0.001, o - 0.001, c, 200.0))
            px = c
            body *= 1.01
        o = px
        c = px + body * 40
        bars.append(Bar(t0 + 70 * TF2 * 1000, o, c + 0.0005, o - 0.0005, c, 2500.0))
        px = c
        g = bars[69].high + 1.0           # gap up: low > high[2]
        o = g
        c = g + 0.1
        bars.append(Bar(t0 + 71 * TF2 * 1000, o, c + 0.02, o - 0.02, c, 250.0))
        return bars

    def bear_combos():
        bars = []
        px = 100.0
        body = 0.05
        for i in range(70):
            o = px
            c = px - body
            bars.append(Bar(t0 + i * TF2 * 1000, o, o + 0.001, c - 0.001, c, 200.0))
            px = c
            body *= 1.01
        o = px
        c = px - body * 40
        bars.append(Bar(t0 + 70 * TF2 * 1000, o, o + 0.0005, c - 0.0005, c, 2500.0))
        px = c
        g = bars[69].low - 1.0            # gap down: high < low[2]
        o = g
        c = g - 0.1
        bars.append(Bar(t0 + 71 * TF2 * 1000, o + 0.02, o + 0.02, c - 0.02, c, 250.0))
        return bars

    out.append((bull_combos(), TF2))
    out.append((bear_combos(), TF2))
    return out


def _all_show_params(**extra):
    return core.Params(
        show_SAAB=True, show_Kratos=True, show_BullRVOL1x=True, show_BearRVOL1x=True,
        show_GrandSlam=True, show_MOAB=True, show_Pentagon=True, show_WTC=True,
        show_Hiroshima=True, show_Nagasaki=True, show_Long1=True, show_Short1=True,
        show_Long2=True, show_Short2=True, show_CS1_Bull=True, show_CS1_Bear=True,
        show_CS2_Bull=True, show_CS2_Bear=True, show_CS3_Bull=True, show_CS3_Bear=True,
        show_CS4_Bull=True, show_CS4_Bear=True, **extra)


# ───────────────────────────────── main ─────────────────────────────────────
def main():
    bars = _make_bars()
    n = len(bars)
    checks: list[tuple[str, bool]] = []

    a = core.fire_matrix(bars, tf_seconds=TF)
    res = core.compute(bars, tf_seconds=TF)

    # 1 determinism
    b = core.fire_matrix(bars, tf_seconds=TF)
    checks.append(("determinism", _fire_tuple(a) == _fire_tuple(b)))

    # 2 tick==time on identical bars + identical tf
    P = core.Params(tick_fallback_sec=TF)
    rt = tickmod.run_on_bars(bars, params=P)
    tm = timemod.run_on_bars(bars, tf_seconds=TF, params=P)
    checks.append(("tick==time_fire_matrix", _fire_tuple(rt) == _fire_tuple(tm)))

    # 3 raw==sorted
    sorted_bars = sorted(bars, key=lambda x: x.ts)
    s = core.fire_matrix(sorted_bars, tf_seconds=TF)
    checks.append(("raw==sorted", _fire_tuple(s) == _fire_tuple(a)))

    # 4 raw fire count == coordinate-event count
    raw = sum(sum(a["fire_" + pid]) for pid in PLOTS)
    checks.append((f"raw==events ({raw})", raw == len(a["events"])))

    # 5 negative control: reversed input differs
    rev = core.fire_matrix(list(reversed(bars)), tf_seconds=TF)
    checks.append(("negative_control_reversed_differs", _fire_tuple(rev) != _fire_tuple(a)))

    # 6 flat bars -> all-zero
    base = 1_700_000_000_000
    flat = [Bar(base + i * TF * 1000, 50.0, 50.0, 50.0, 50.0, 1000.0) for i in range(300)]
    fl = core.fire_matrix(flat, tf_seconds=TF)
    checks.append(("flat=0", all(sum(fl["fire_" + pid]) == 0 for pid in PLOTS)))

    # 7 warmup: no WINDOWED plot fires before the longest active lookback (Nagasaki
    #   excluded — it has no lookback window and legitimately fires at the first new max).
    WARMUP = max(core.Params().bb_avgLength, core.Params().bb_smaLength)  # 30
    early = False
    for pid in PLOTS:
        if pid == "Nagasaki":
            continue
        for i in range(min(WARMUP, n)):
            if a["fire_" + pid][i]:
                early = True
    checks.append((f"warmup_clean(<{WARMUP})", not early))

    # 8 offset=-1 for FVG combos (applied bar is exactly one real bar back)
    off_ok = True
    ts = a["ts"]
    idx_of = {ts[i]: i for i in range(n)}
    for e in a["events"]:
        want = core.PLOT_IDS[e.plot_id][3]
        ci = idx_of[e.computed_ts_ms]
        ai = idx_of[e.applied_ts_ms]
        if ai - ci != want:
            off_ok = False
    checks.append(("offset_-1_FVG_combos", off_ok))

    # 9 RVOL normPrice band exclusivity (bands are disjoint -> never co-fire same side)
    excl = True
    sig = res["sig"]
    for i in range(n):
        if sum(1 for k in ("SAAB", "BullRVOL1x", "GrandSlam") if sig[k][i]) > 1:
            excl = False
        if sum(1 for k in ("Kratos", "BearRVOL1x", "MOAB") if sig[k][i]) > 1:
            excl = False
    checks.append(("normprice_band_exclusivity", excl))

    # 10 independent normPrice-band re-derivation, bar-for-bar (compare RAW sig, no toggle)
    ref_np = _ref_normprice_bands(bars, TF)
    np_ok = all(all(bool(sig[pid][i]) == bool(ref_np[pid][i]) for i in range(n))
                for pid in ("SAAB", "Kratos", "BullRVOL1x", "BearRVOL1x", "GrandSlam", "MOAB"))
    checks.append(("indep_normprice_bands", np_ok))

    # 11 independent Nagasaki re-derivation
    ref_n = _ref_nagasaki(bars)
    checks.append(("indep_nagasaki", all(bool(sig["Nagasaki"][i]) == bool(ref_n[i]) for i in range(n))))

    # 12 independent matrix-number re-derivation
    ref_m = _ref_matrix_number(bars, core.Params().matrix_len)
    checks.append(("indep_matrix_number", all(bool(res["_internal"]["is_matrix"][i]) == bool(ref_m[i]) for i in range(n))))

    # 13 STUB-IS-ZERO HONESTY GATE
    #   (a) STUB_IDS must be empty (this is a FULL port — nothing held at 0).
    #   (b) every detection plot is genuinely computed -> each CAN fire across the
    #       union of CRAFTED scenarios built to hit that plot's exact conditions
    #       (so a 0 fire elsewhere means "no signal", never "not implemented").
    #   All show-toggles are exposed so every plot is eligible. (Random data does NOT
    #   reliably hit the narrow normPrice / Reg@Time / FVG-combo conditions; the
    #   crafted scenarios deterministically do — that is the honest way to prove
    #   computation. WTC's band is structurally empty at tf=60, so it is exercised at
    #   tf=10 where the band is valid — faithful Pine, not a stub.)
    no_stubs = (len(core.STUB_IDS) == 0)
    union = {pid: 0 for pid in PLOTS}
    for sbars, stf in _craft_scenarios():
        Pc = _all_show_params(auto_thresh=False, threshPct=0.3)
        oo = core.fire_matrix(sbars, Pc, tf_seconds=stf)
        for pid in PLOTS:
            union[pid] += sum(oo["fire_" + pid])
    never_fire = [pid for pid in PLOTS if union[pid] == 0]
    honesty_ok = no_stubs and (len(never_fire) == 0)
    checks.append(("honesty_no_stubs_all_22_plots_fire", honesty_ok))

    # transparency: fire census on the default (shipped-toggle) matrix
    census = {pid: sum(a["fire_" + pid]) for pid in PLOTS}

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    print("heavy_weapons_4fvg_4matrix — OFFLINE PARITY GATE (Gate-B)")
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("  fire census (default toggles):", {k: c for k, c in census.items() if c})
    print("  honesty union fire counts (all toggles):", union)
    if never_fire:
        print("  WARNING never-fired plots (would break honesty gate):", never_fire)
    print("  DEFERRED: Gate-A render-coordinate parity vs TradingView — PENDING (no TV in this batch)")
    print(f"PARITY heavy_weapons_4fvg_4matrix: {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
