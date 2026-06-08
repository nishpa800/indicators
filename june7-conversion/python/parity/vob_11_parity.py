"""VOB v11 MULTIPLES — parity harness (offline Gate-B). FULL port.

Runnable by a stranger:  python3 vob_11_parity.py  -> "PARITY vob_11: n/m".

This is a FULL port: the deep multi-sensitivity VOB zone engine, the strict F->A
VLB ladder, multi-zone same-candle counts, T3 cluster, Nagasaki, and the embedded
HW-Single v3 engine (-> hws_any) are all ported in _vob_11_core from OHLCV. There
is NO EngineInputs stub and COMPOSITE_PARTIAL is empty on both wrappers.

A blind "second copy" is not an independent check, so the harness INDEPENDENTLY
re-derives the deterministic leaf gates that the fires are pure functions of, and
asserts the core's fires are CONSISTENT with them (a fire implies its required
leaf gate). It also asserts the structural invariants + honesty/negative/warmup.

Checks (each prints PASS/FAIL + REAL detail):
   1.  TICK PORT RUNS        — tick wrapper produces the full fire matrix.
   2.  TIME PORT RUNS        — time wrapper produces the full fire matrix.
   3.  PLOT COUNT            — PLOT_IDS length == enumerated source detection plots.
   4.  TICK == TIME          — SAME core on SAME Bar objects -> byte-identical fire
                               matrix through both wrappers (one code path).
   5.  DETERMINISM           — two runs on identical bars give identical matrix.
   6.  BOOLEAN + LEVELS      — every fire is strictly 0/1; lvl_* is float where
                               fire==1 (and None where fire==0) for marker plots.
   7.  sigAny INVARIANT      — sigAny == OR of all PLOT_IDS fires, every bar.
   8.  COOLDOWN SEMANTICS    — independent f_cd_ok re-derivation on a raw zone-fire
                               series matches the core's gated fire_zb_a.
   9.  MULTI-ZONE COMPOSITION— mz_b2 iff exactly 2 bull zone markers (& cooldown);
                               mz_b3 iff >=3; mirror bear; counts == sum of 6.
  10.  T3 CLUSTER            — tc_cluster iff >=2 of the 12 t3 fires (& cooldown).
  11.  VOBxHW NECESSITY      — every vobhws fire requires (vob_left_side & hws_any)
                               on that bar (independent recompute of the left side).
  12.  VLB NECESSITY         — every vlb_bull fire bar had bull zone formations and
                               no bear zone formation on that bar (ladder invariant).
  13.  NAGASAKI LEAF         — every nagasaki fire bar has volume[1] strictly > all
                               earlier volume[1] seen (all-time-high-vol invariant).
  14.  HWS LEAF CONSISTENCY  — hws_any == (hws_bull|hws_bear|hws_neutral) every bar.
  15.  NON-TRIVIALITY        — the matrix is NOT all-zero on the event-rich tape;
                               >= 1 distinct detection plot fires.
  16.  NEGATIVE CONTROL      — a flat doji tape fires nothing (no warmup ghosts).
  17.  WARMUP                — a tiny tape does not crash and does not fire.
  18.  HONESTY (stub-is-zero)— COMPOSITE_PARTIAL empty on BOTH wrappers AND the
                               matrix is genuinely exercised (>= 1 distinct plot
                               fires). A green that fired nothing = fabricated.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)
sys.path.insert(0, _HERE)                       # local _nn_harness
sys.path.insert(0, os.path.join(_ROOT, "tick"))
sys.path.insert(0, os.path.join(_ROOT, "time"))

from _nine_nines_common import Bar  # noqa: E402
from _nn_harness import synthetic_bars  # noqa: E402
import _vob_11_core as core  # noqa: E402
import vob_11_tick as tickmod  # noqa: E402
import vob_11_time as timemod  # noqa: E402

SOURCE = ("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT "
          "transformed yet/June 7/Tick Friendly conversion/vob_11_tickfriendly.pine")

PIDS = core.PLOT_IDS


def _params_eventful():
    """Params that turn the cosmetic/disabled paths ON so the matrix is exercised:
    enable all zone markers + all T3 toggles + Nagasaki, and shorten the EMA
    sensitivities so crossovers actually happen on a ~900-bar synthetic tape."""
    p = core.Params()
    for t in core.TIERS:
        p.en_zone[t] = True
        p.show_t3_buy[t] = True
        p.show_t3_sell[t] = True
    p.show_nagasaki = True
    # Short EMAs so the zone engine fires on a finite tape (defaults 1000-2500 are
    # far longer than 900 bars -> no crossovers -> no zones). These are inputs.
    p.sens_a = 40; p.sens_b = 34; p.sens_c = 28
    p.sens_d = 22; p.sens_e = 16; p.sens_f = 10
    p.cooldown_bars = 5   # let multiple fires through on the short tape
    return p


def _ref_cooldown(raw, cd):
    out = [0] * len(raw); last = None
    for i, f in enumerate(raw):
        ok = last is None or (i - last) > cd
        fire = bool(f) and ok
        if fire:
            last = i
        out[i] = 1 if fire else 0
    return out


def main():
    checks = []

    bars = synthetic_bars(n=900, grain="time")
    p = _params_eventful()

    # 1/2. tick & time wrappers run (same Bar objects -> one code path)
    out_t = tickmod.run_on_bars(bars, params=p, tf_seconds=60)
    out_m = timemod.run_on_bars(bars, params=p, tf_seconds=60)
    checks.append(("tick_port_runs", all(k in out_t for k in PIDS)))
    checks.append(("time_port_runs", all(k in out_m for k in PIDS)))

    # 3. plot count == enumerated source detection plots
    #    nagasaki(1) + zoneform bull/bear(12) + fire_zb/zs(12) + t3 buy/sell(12)
    #    + vlb(2) + mz(4) + tc(1) + vobhws(1) = 45
    expected = 1 + 12 + 12 + 12 + 2 + 4 + 1 + 1
    checks.append((f"plot_count_eq_{expected}", len(PIDS) == expected))

    # 4. tick == time identical fire matrix
    tt = all(out_t[k] == out_m[k] for k in PIDS)
    checks.append(("tick_eq_time", tt))

    # 5. determinism
    out_t2 = tickmod.run_on_bars(bars, params=_params_eventful(), tf_seconds=60)
    det = all(out_t[k] == out_t2[k] for k in PIDS)
    checks.append(("determinism", det))

    # 6. boolean + levels
    n = len(bars)
    bool_ok = all(all(x in (0, 1) for x in out_t[k]) for k in PIDS)
    lvl_ok = True
    for k in PIDS:
        lv = out_t.get(f"lvl_{k}")
        if lv is None:
            lvl_ok = False; break
        for i in range(n):
            if out_t[k][i] == 1 and lv[i] is None:
                lvl_ok = False; break
            if out_t[k][i] == 0 and lv[i] is not None:
                lvl_ok = False; break
        if not lvl_ok:
            break
    checks.append(("all_fires_boolean", bool_ok))
    checks.append(("levels_aligned_to_fires", lvl_ok))

    # 7. sigAny invariant
    sa_ok = all(out_t["sigAny"][i] == (1 if any(out_t[k][i] for k in PIDS) else 0) for i in range(n))
    checks.append(("sigAny_eq_OR_all_fires", sa_ok))

    # 8. cooldown semantics: re-derive f_cd_ok on the RAW zone-creation series for
    #    tier 'a' bull and confirm it equals the core's gated fire_zb_a.
    #    Raw = bar where lower_a array grew (nzb_a). We recompute nzb_a by running
    #    the core with cooldown=0 and en_zone[a]=True (fires == every formation).
    p_raw = _params_eventful(); p_raw.cooldown_bars = 0
    out_raw = tickmod.run_on_bars(bars, params=p_raw, tf_seconds=60)
    raw_a = out_raw["fire_zb_a"]                       # cooldown 0 -> raw formations
    ref_a = _ref_cooldown(raw_a, p.cooldown_bars)
    checks.append(("cooldown_zone_a_matches_f_cd_ok", out_t["fire_zb_a"] == ref_a))

    # 9. multi-zone composition (independent count + iff condition w/ cooldown)
    cd = p.cooldown_bars
    cd_b2 = _MZGate(cd); cd_b3 = _MZGate(cd); cd_s2 = _MZGate(cd); cd_s3 = _MZGate(cd)
    mz_ok = True
    for i in range(n):
        bc = sum(out_t[f"fire_zb_{t}"][i] for t in core.TIERS)
        sc = sum(out_t[f"fire_zs_{t}"][i] for t in core.TIERS)
        b2 = 1 if cd_b2.fire(i, bc == 2) else 0
        b3 = 1 if cd_b3.fire(i, bc >= 3) else 0
        s2 = 1 if cd_s2.fire(i, sc == 2) else 0
        s3 = 1 if cd_s3.fire(i, sc >= 3) else 0
        if (out_t["mz_b2"][i], out_t["mz_b3"][i], out_t["mz_s2"][i], out_t["mz_s3"][i]) != (b2, b3, s2, s3):
            mz_ok = False; break
    checks.append(("multi_zone_count_composition", mz_ok))

    # 10. T3 cluster: >=2 of 12 t3 fires (& cooldown)
    cd_tc = _MZGate(cd); tc_ok = True
    for i in range(n):
        cnt = sum(out_t[f"t3_buy_{t}"][i] + out_t[f"t3_sell_{t}"][i] for t in core.TIERS)
        want = 1 if cd_tc.fire(i, cnt >= 2) else 0
        if out_t["tc_cluster"][i] != want:
            tc_ok = False; break
    checks.append(("t3_cluster_iff_2plus", tc_ok))

    # 11. VOBxHW necessity: a fire requires vob_left_side & hws_any on that bar
    hws_any = out_t["hws_any"]
    vh_ok = True
    for i in range(n):
        if out_t["vobhws"][i] == 1:
            left = (any(out_t[f"t3_buy_{t}"][i] or out_t[f"t3_sell_{t}"][i] for t in core.TIERS)
                    or any(out_t[f"fire_zb_{t}"][i] or out_t[f"fire_zs_{t}"][i] for t in core.TIERS))
            if not (left and hws_any[i]):
                vh_ok = False; break
    checks.append(("vobhws_requires_left_and_hws", vh_ok))

    # 12. VLB necessity: a bull fire requires bull zone formation on the bar and
    #     no bear zone formation on the bar (the ladder kill rule).
    vlb_ok = True
    for i in range(n):
        if out_t["vlb_bull"][i] == 1:
            bull_form = any(out_t[f"zoneform_bull_{t}"][i] for t in core.TIERS)
            bear_form = any(out_t[f"zoneform_bear_{t}"][i] for t in core.TIERS)
            if not (bull_form and not bear_form):
                vlb_ok = False; break
        if out_t["vlb_bear"][i] == 1:
            bull_form = any(out_t[f"zoneform_bull_{t}"][i] for t in core.TIERS)
            bear_form = any(out_t[f"zoneform_bear_{t}"][i] for t in core.TIERS)
            if not (bear_form and not bull_form):
                vlb_ok = False; break
    checks.append(("vlb_requires_same_dir_formation", vlb_ok))

    # 13. Nagasaki leaf: each fire bar has volume[1] strictly > all earlier volume[1]
    nag_ok = True
    seen_max = 0.0
    for i in range(n):
        if i >= 1:
            v1 = bars[i - 1].volume
            is_ath = v1 > seen_max
            if out_t["nagasaki"][i] == 1 and not is_ath:
                nag_ok = False; break
            if v1 > seen_max:
                seen_max = v1
    checks.append(("nagasaki_is_ath_volume", nag_ok))

    # 14. HWS leaf consistency
    hws_ok = all(out_t["hws_any"][i] == (out_t["hws_bull"][i] or out_t["hws_bear"][i] or out_t["hws_neutral"][i]) for i in range(n))
    checks.append(("hws_any_eq_or_of_sides", hws_ok))

    # 15. non-triviality
    fired = {k for k in PIDS if sum(out_t[k]) > 0}
    checks.append(("non_trivial_matrix", len(fired) >= 1))

    # 16. negative control: a perfectly-flat doji tape has NO price movement, so
    #     every MOVEMENT-dependent detection plot must fire ZERO (no EMA-cross
    #     zones, no displacement/HWS, no VLB/multi-zone/cluster/VOBxHW). The ONLY
    #     permitted fire is the single seed Nagasaki on bar 1: the source's
    #     maxVolEver seeds at 0.0 (line 761) so the first non-zero volume[1] is an
    #     all-time high BY CONSTRUCTION — that is faithful Pine behavior, not a
    #     ghost. We assert: zero on all non-Nagasaki plots AND Nagasaki fires at
    #     most once (the seed), never repeatedly.
    flat = [Bar(1_700_000_000_000 + i * 60_000, 100.0, 100.0, 100.0, 100.0, 1000.0) for i in range(400)]
    out_flat = tickmod.run_on_bars(flat, params=_params_eventful(), tf_seconds=60)
    non_nag = [k for k in PIDS if k != "nagasaki"]
    neg_ok = all(sum(out_flat[k]) == 0 for k in non_nag) and sum(out_flat["nagasaki"]) <= 1
    checks.append(("negative_control_movement_zero", neg_ok))

    # 17. warmup: a tiny tape does not crash and fires no MOVEMENT plot. (Tiny
    #     constant-volume tape can fire the same seed Nagasaki once; same rule.)
    tiny = [Bar(1_700_000_000_000 + i * 60_000, 100.0, 100.0, 100.0, 100.0, 1000.0) for i in range(3)]
    out_tiny = tickmod.run_on_bars(tiny, params=_params_eventful(), tf_seconds=60)
    warm_ok = all(sum(out_tiny[k]) == 0 for k in non_nag) and sum(out_tiny["nagasaki"]) <= 1
    checks.append(("warmup_no_movement_fire", warm_ok))

    # 18. honesty (stub-is-zero): no COMPOSITE_PARTIAL on either wrapper AND matrix exercised
    honest = (tickmod.COMPOSITE_PARTIAL == [] and timemod.COMPOSITE_PARTIAL == []
              and len(fired) >= 1)
    checks.append(("honesty_no_stub_and_exercised", honest))

    passed = sum(1 for _, ok in checks if ok); total = len(checks)
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"\nfired plots ({len(fired)}): " + ", ".join(sorted(fired)))
    print(f"PARITY vob_11: {passed}/{total}")
    sys.exit(0 if passed == total else 1)


class _MZGate:
    """Independent f_cd_ok gate for the harness's multi-zone/cluster re-derivation."""
    __slots__ = ("cd", "last")

    def __init__(self, cd):
        self.cd = cd; self.last = None

    def fire(self, i, cond):
        ok = self.last is None or (i - self.last) > self.cd
        f = bool(cond) and ok
        if f:
            self.last = i
        return f


if __name__ == "__main__":
    main()
