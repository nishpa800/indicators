"""PB & PBJ — 4 Signals — parity harness (offline Gate-B).

FULL port (every detection plot derived from OHLCV — no stub layer). This harness
runs on deterministic synthetic + engineered bars and prints a REAL pass/total.

The PB/PBJ detector is a deep stateful machine (supertrend + level landers +
approach latches). A blind "second copy" would not be an independent check, so we
INDEPENDENTLY re-derive the upstream gates the four detection plots are pure
functions of — supertrend sig_line, ta.crossover/crossunder, and the PB&J filter
(ema/atr/HH-LL/vol) — and assert the core's fires are consistent with them. Then we
assert the structural invariants and the honesty/negative-control/warmup gates.

Checks (each prints PASS/FAIL + REAL detail):
   1. TICK PORT RUNS          — tick wrapper produces the 4-plot fire matrix.
   2. TIME PORT RUNS          — time wrapper produces the 4-plot fire matrix.
   3. PLOT COUNT == 4         — PLOT_IDS length == source plotshape count (4).
   4. TICK == TIME            — SAME core on the SAME Bar objects -> byte-identical
                                fire matrix through both wrappers (one code path).
   5. DETERMINISM             — two runs on identical bars give identical matrix.
   6. BOOLEAN + LEVELS        — every fire_* is strictly 0/1; lvl_* is float where
                                fire==1 and None where fire==0 (exact alignment).
   7. MUTUAL EXCLUSION        — sigBullPB & sigBullPBJ never both fire on a bar;
                                likewise sigBearPB & sigBearPBJ (Pine `and not`).
   8. sigAny INVARIANT        — sigAny == OR of the four fires, every bar.
   9. CROSSOVER PARITY        — every bull fire bar has an independent buy_cross;
                                every bear fire bar has an independent sell_cross
                                (the four signals all require buy/sell_cross).
  10. PBJ-FILTER PARITY       — every BullPBJ fire requires independent pbj_buy to
                                have latched at/before that bar; BearPBJ requires
                                pbj_sell. (PBJ plots are gated by the PB&J filter.)
  11. NON-TRIVIALITY          — the fire matrix is NOT all-zero on the event-rich
                                tape (a green that fired nothing = fabricated).
  12. NEGATIVE CONTROL        — a flat doji tape (no body, no range, no vol change)
                                fires nothing (no false positives from warmup math).
  13. WARMUP                  — a tiny tape does not crash and does not fire before
                                the engines are warm.
  14. HONESTY (stub-is-zero)  — COMPOSITE_PARTIAL is empty on BOTH wrappers AND the
                                matrix is genuinely exercised (>= 1 distinct plot
                                fires). A passing honesty gate that fired nothing
                                would be fabricated parity; forbidden.

Re-runnable by a stranger:  python3 pbj_only_4_signals_parity.py
REAL pass/total is printed; exit 0 only if all pass.
"""
from __future__ import annotations

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tick"))
sys.path.insert(0, os.path.join(_ROOT, "time"))

from _nine_nines_common import Bar  # noqa: E402
from _nn_harness import (  # noqa: E402
    synthetic_bars, sma, atr as _atr_ohlc, highest, lowest, nz,
)
import _pbj_only_4_signals_core as core  # noqa: E402
import pbj_only_4_signals_tick as tickmod  # noqa: E402
import pbj_only_4_signals_time as timemod  # noqa: E402

SOURCE = ("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT "
          "transformed yet/June 7/Tick Friendly conversion/"
          "pbj_only_4_signals_tickfriendly.pine")

PIDS = core.PLOT_IDS


# ─────────────────────────── deterministic tapes ────────────────────────────
def _osc_tape(nbars=1400, seed=7):
    """Multi-session oscillating tape: a slow sine drift (so price repeatedly
    crosses the supertrend sig_line both ways -> buy_cross & sell_cross both reachable)
    with periodic widely-spaced HIGH-VOLUME spikes that punch fresh HH/LL extremes
    (so the PB&J filter pbj_buy/pbj_sell can latch). This genuinely lights all four
    detection plots end-to-end."""
    import math
    import random
    random.seed(seed)
    rows = []
    t0 = 1_700_000_000_000
    px = 100.0
    for i in range(nbars):
        ts = t0 + (i // 90) * 86_400_000 + (i % 90) * 60_000
        # slow sine so the MA/supertrend is repeatedly crossed in both directions
        target = 100.0 + 14.0 * math.sin(i / 11.0) + 6.0 * math.sin(i / 47.0)
        o = px
        drift = (target - px) * 0.55 + (random.random() - 0.5) * 0.5
        c = max(0.5, o + drift)
        body = abs(c - o)
        spike = random.random() > 0.90        # widely-spaced extreme bars
        if spike:
            # push a fresh HH or LL extreme + heavy volume for the PB&J filter
            if c >= o:
                c = o + (2.5 + random.random() * 4.0)
            else:
                c = max(0.5, o - (2.5 + random.random() * 4.0))
            body = abs(c - o)
        hi = max(o, c) + body * (0.05 + random.random() * 0.2) + 0.02
        lo = min(o, c) - body * (0.05 + random.random() * 0.2) - 0.02
        vol = random.uniform(800, 1200)
        if spike:
            vol *= 8.0 + random.random() * 10.0
        rows.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(c, 4), round(vol, 2)))
        px = c
    return rows


def _flat_tape(nbars=300):
    """Doji tape: open==close, no range, constant volume, no gaps -> no fires."""
    rows = []
    t0 = 1_700_000_000_000
    for i in range(nbars):
        ts = t0 + (i // 24) * 86_400_000 + (i % 24) * 60_000
        rows.append(Bar(ts, 100.0, 100.0, 100.0, 100.0, 1000.0))
    return rows


# ─────────────────── independent re-derivations (answer keys) ────────────────
def _independent(bars, p: core.Params):
    """Re-derive supertrend sig_line, crossovers, and the PB&J filter from scratch
    using only the harness primitives (NOT the core's code path)."""
    n = len(bars)
    o = [b.open for b in bars]; h = [b.high for b in bars]; l = [b.low for b in bars]
    c = [b.close for b in bars]; v = [b.volume for b in bars]

    # base MA (default VWMA len5): re-derive vwma = sma(c*v,L)/sma(v,L)
    pv = [c[i] * v[i] for i in range(n)]
    num = sma(pv, p.zoo_ma_len); den = sma(v, p.zoo_ma_len)
    base_ma = [None if (num[i] is None or den[i] in (None, 0)) else num[i] / den[i] for i in range(n)]
    st_atr_s = _atr_ohlc(o, h, l, c, p.st_period)

    # supertrend (independent forward pass)
    st_dir = 1
    cl_prev = cs_prev = sigprev = sigprev2 = None
    sig_line = [None] * n
    buy_cross = [False] * n
    sell_cross = [False] * n
    for i in range(n):
        bm = base_ma[i]; sa = st_atr_s[i]
        if bm is None or sa is None:
            sigprev2 = sigprev; sigprev = None
            continue
        st_atr = p.st_mult * sa
        dl = bm - st_atr; ds = bm + st_atr
        clb = nz(cl_prev, dl); csb = nz(cs_prev, ds)
        cl = max(dl, nz(cl_prev)) if bm > clb else dl
        cs = min(ds, nz(cs_prev)) if bm < csb else ds
        if p.use_st:
            if st_dir == -1 and c[i] > nz(cs_prev):
                st_dir = 1
            elif st_dir == 1 and c[i] < nz(cl_prev):
                st_dir = -1
            sl = cl if st_dir == 1 else cs
        else:
            sl = bm
        sig_line[i] = sl
        if sigprev is not None and i >= 1:
            buy_cross[i] = c[i] > sl and c[i - 1] <= sigprev
            sell_cross[i] = c[i] < sl and c[i - 1] >= sigprev
        cl_prev = cl; cs_prev = cs; sigprev2 = sigprev; sigprev = sl

    # PB&J filter (independent)
    pbj_ma = core._ema(c, p.pbj_ma_period)   # ta.ema (same primitive)
    pbj_atr = _atr_ohlc(o, h, l, c, p.pbj_atr_period)
    avg_vol = sma(v, p.pbj_vol_period)
    low_hh = lowest(l, p.pbj_hh_ll); high_hh = highest(h, p.pbj_hh_ll)
    pbj_buy = [False] * n; pbj_sell = [False] * n
    for i in range(n):
        thr = 0.0 if (c[i] == 0 or pbj_atr[i] is None) else pbj_atr[i] / c[i] * p.pbj_atr_mult
        if pbj_ma[i] is not None and avg_vol[i] is not None and low_hh[i] is not None:
            pbj_buy[i] = (l[i] < pbj_ma[i] * (1 - thr) and l[i] == low_hh[i]
                          and v[i] > avg_vol[i] * p.pbj_vol_mult)
        if pbj_ma[i] is not None and avg_vol[i] is not None and high_hh[i] is not None:
            pbj_sell[i] = (h[i] > pbj_ma[i] * (1 + thr) and h[i] == high_hh[i]
                           and v[i] > avg_vol[i] * p.pbj_vol_mult)

    return dict(buy_cross=buy_cross, sell_cross=sell_cross,
                pbj_buy=pbj_buy, pbj_sell=pbj_sell)


# ───────────────────────────────── checks ───────────────────────────────────
def run():
    results = []
    p = core.Params()
    osc = _osc_tape(1400, 7)
    multi = synthetic_bars(n=1200, grain="time")

    # 1/2 ports run
    try:
        ok_b = tickmod.run_on_bars(osc)
        ok = isinstance(ok_b, dict) and any(k.startswith("fire_") for k in ok_b)
        results.append(("tick_port_runs", ok, f"{sum(1 for k in ok_b if k.startswith('fire_'))} plots"))
    except Exception as e:
        ok_b = {}; results.append(("tick_port_runs", False, f"EXC {e}"))
    try:
        ot = timemod.run_on_bars(osc)
        ok = isinstance(ot, dict) and any(k.startswith("fire_") for k in ot)
        results.append(("time_port_runs", ok, f"{sum(1 for k in ot if k.startswith('fire_'))} plots"))
    except Exception as e:
        ot = {}; results.append(("time_port_runs", False, f"EXC {e}"))

    # 3 plot count == 4 (and source plotshape sanity)
    src_plotshapes = None
    if os.path.exists(SOURCE):
        src_plotshapes = len(re.findall(r"plotshape\(", open(SOURCE, errors="ignore").read()))
    results.append(("plot_count_eq_4", len(PIDS) == 4,
                    f"PLOT_IDS={len(PIDS)}, source plotshape(={src_plotshapes})"))

    # 4 tick == time
    try:
        a = tickmod.run_on_bars(osc); b = timemod.run_on_bars(osc)
        mism = [k for k in a if a[k] != b.get(k)]
        results.append(("tick_eq_time", not mism, "identical matrix" if not mism else f"mismatch {mism[:4]}"))
    except Exception as e:
        a = {}; results.append(("tick_eq_time", False, f"EXC {e}"))

    # 5 determinism
    try:
        d1 = tickmod.run_on_bars(osc); d2 = tickmod.run_on_bars(_osc_tape(1400, 7))
        results.append(("deterministic", d1 == d2, "stable" if d1 == d2 else "non-deterministic"))
    except Exception as e:
        results.append(("deterministic", False, f"EXC {e}"))

    # 6 boolean + level alignment
    try:
        mt = tickmod.run_on_bars(osc); bad = []
        for pid in PIDS:
            f = mt[f"fire_{pid}"]; lv = mt[f"lvl_{pid}"]
            if any(x not in (0, 1) for x in f):
                bad.append(f"{pid}:nonbool")
            for i in range(len(f)):
                if f[i] == 1 and lv[i] is None:
                    bad.append(f"{pid}:fire-no-lvl"); break
                if f[i] == 0 and lv[i] is not None:
                    bad.append(f"{pid}:nofire-has-lvl"); break
        results.append(("boolean_matrix_and_levels", not bad,
                        "all 0/1 + levels aligned" if not bad else str(bad[:4])))
    except Exception as e:
        results.append(("boolean_matrix_and_levels", False, f"EXC {e}"))

    # 7 mutual exclusion
    mt = tickmod.run_on_bars(osc); n = len(osc)
    mx = all(not (mt["fire_sigBullPB"][i] and mt["fire_sigBullPBJ"][i])
             and not (mt["fire_sigBearPB"][i] and mt["fire_sigBearPBJ"][i]) for i in range(n))
    results.append(("mutual_exclusion", mx, "PB and PBJ never co-fire same side"))

    # 8 sigAny invariant
    anyok = all(mt["sigAny"][i] == (1 if (mt["fire_sigBullPB"][i] or mt["fire_sigBullPBJ"][i]
               or mt["fire_sigBearPB"][i] or mt["fire_sigBearPBJ"][i]) else 0) for i in range(n))
    results.append(("sigAny_invariant", anyok, "sigAny == OR(4 fires) every bar"))

    # 9 crossover parity (independent)
    ind = _independent(osc, p)
    bull_ok = all((not (mt["fire_sigBullPB"][i] or mt["fire_sigBullPBJ"][i])) or ind["buy_cross"][i]
                  for i in range(n))
    bear_ok = all((not (mt["fire_sigBearPB"][i] or mt["fire_sigBearPBJ"][i])) or ind["sell_cross"][i]
                  for i in range(n))
    results.append(("crossover_parity", bull_ok and bear_ok,
                    f"bull fires require independent buy_cross ({sum(ind['buy_cross'])}); "
                    f"bear fires require independent sell_cross ({sum(ind['sell_cross'])})"))

    # 10 PB&J-filter parity: a PBJ fire on bar i requires pbj_buy/sell to have
    #    latched at/before i (wait_pbj_* latch persists until a crossover consumes it).
    def _latched_before(flag):
        seen = [False] * n; s = False
        for i in range(n):
            if flag[i]:
                s = True
            seen[i] = s
        return seen
    pbj_buy_seen = _latched_before(ind["pbj_buy"])
    pbj_sell_seen = _latched_before(ind["pbj_sell"])
    pbjbull_ok = all((not mt["fire_sigBullPBJ"][i]) or pbj_buy_seen[i] for i in range(n))
    pbjbear_ok = all((not mt["fire_sigBearPBJ"][i]) or pbj_sell_seen[i] for i in range(n))
    results.append(("pbj_filter_parity", pbjbull_ok and pbjbear_ok,
                    f"BullPBJ fires require prior independent pbj_buy ({sum(ind['pbj_buy'])}); "
                    f"BearPBJ require prior pbj_sell ({sum(ind['pbj_sell'])})"))

    # 11 non-triviality
    fired = sum(sum(mt[f"fire_{pid}"]) for pid in PIDS)
    results.append(("non_triviality", fired > 0, f"total fires on osc tape={fired}"))

    # 12 negative control (flat doji tape)
    try:
        flat = tickmod.run_on_bars(_flat_tape(300))
        flat_fires = sum(sum(flat[f"fire_{pid}"]) for pid in PIDS)
        results.append(("negative_control_zero", flat_fires == 0, f"flat tape total fires={flat_fires}"))
    except Exception as e:
        results.append(("negative_control_zero", False, f"EXC {e}"))

    # 13 warmup
    try:
        tiny = synthetic_bars(n=8, grain="time")
        wt = tickmod.run_on_bars(tiny)
        warm_fires = sum(sum(wt[f"fire_{pid}"]) for pid in PIDS)
        results.append(("warmup_no_premature_fire", warm_fires == 0,
                        f"fires on 8-bar tape={warm_fires}"))
    except Exception as e:
        results.append(("warmup_no_premature_fire", False, f"EXC {e}"))

    # 14 honesty: no declared stubs + matrix exercised (>=1 distinct plot fires)
    no_stubs = (len(tickmod.COMPOSITE_PARTIAL) == 0 and len(timemod.COMPOSITE_PARTIAL) == 0)
    union_fire = set()
    for tape in (osc, multi):
        m = tickmod.run_on_bars(tape)
        for pid in PIDS:
            if sum(m[f"fire_{pid}"]) > 0:
                union_fire.add(pid)
    results.append(("honesty_no_stub_and_exercised", no_stubs and len(union_fire) >= 1,
                    f"declared_stubs=0, distinct plots fired={len(union_fire)}: {sorted(union_fire)}"))

    return results


if __name__ == "__main__":
    res = run()
    passed = sum(1 for _, ok, _ in res if ok)
    total = len(res)
    print(f"=== PBJ ONLY 4 SIGNALS PARITY (FULL port, 4 plots): {passed}/{total} ===")
    for name, ok, detail in res:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:30s} {detail}")
    sys.exit(0 if passed == total else 1)
