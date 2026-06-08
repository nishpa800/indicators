# Python parity harness — VOB v10  (FULL faithful port, 31 detection plots)
# =============================================================================
# HONEST PARITY (Gate B, offline). This harness proves what it can prove offline
# and is re-runnable by a stranger: it records REAL pass/total, never claimed.
#
# What it checks:
#   1. time port runs and returns a dict
#   2. tick port runs and returns a dict
#   3. tick == time IDENTICAL fire matrix on the SAME bars (one code path)
#   4. all 31 detection plots present (full port, schema = PLOT_IDS)
#   5. fire matrix EXERCISED (>= 10 distinct plots fire on the demo series)
#   6. determinism (two fresh runs identical)
#   7. STUB-IS-ZERO honesty gate (COMPOSITE_PARTIAL is empty -> no held-at-0 stub)
#   8. cooldown known-plaintext: an independent from-scratch f_cd_ok re-derivation
#      matches the core's gate on a handcrafted signal
#   9. Nagasaki known-plaintext: independent ATH(volume[1]) re-derivation matches
#  10. negative control: reversed input produces a DIFFERENT fire matrix (the
#      detection is input-sensitive, not a constant)
#  11. levels-present: every fired bar has a non-None level (0/1 + level contract)
#  12. plot_count_vs_source: Pine plotshape() count == ported detection-plot count
#
# What it does NOT prove (deferred, never claimed green here):
#   * bar-for-bar parity vs TradingView's own engine (Gate A / TV bridge SOW).
#
# Sens: production A..F = 2500..1000 need >2500 bars; the demo series is 900 bars,
# so a SHORT-EMA sens set is used to actually exercise the engine.
# =============================================================================
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tick"))
sys.path.insert(0, str(ROOT / "time"))

import _nn_harness as H            # noqa: E402
import _vob_v10_core as CORE       # noqa: E402
import vob_v10_time as MT          # noqa: E402
import vob_v10_tick as MK          # noqa: E402

SOURCE = Path("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT "
              "transformed yet/June 7/Tick Friendly conversion/vob v10_tickfriendly.pine")

SHORT = {"sens": {"a": 120, "b": 100, "c": 80, "d": 60, "e": 40, "f": 20},
         "cooldown_bars": 5}


def _fire_keys(out):
    return sorted(k for k in out if k.startswith("fire_"))


def run():
    results = []

    # 1-2 ports run
    try:
        bt = H.load_bars(grain="time", n=900)
        ft = MT.compute(bt, params=SHORT)
        results.append(("time_port_runs", isinstance(ft, dict) and bool(ft),
                        f"{len(_fire_keys(ft))} detection plots"))
    except Exception as e:
        results.append(("time_port_runs", False, f"EXC {e}")); ft = {}
    try:
        bk = H.load_bars(grain="tick", n=900)
        fk = MK.compute(bk, params=SHORT)
        results.append(("tick_port_runs", isinstance(fk, dict) and bool(fk),
                        f"{len(_fire_keys(fk))} detection plots"))
    except Exception as e:
        results.append(("tick_port_runs", False, f"EXC {e}")); fk = {}

    # 3 tick == time on the SAME bars (run both on the identical bar series)
    try:
        same = H.load_bars(grain="time", n=900)
        a = MT.compute(same, params=SHORT)
        b = MK.compute(same, params=SHORT)
        mism = [k for k in a if a[k] != b.get(k)]
        results.append(("tick_eq_time_same_bars", not mism,
                        "identical fire+level matrix" if not mism else f"mismatch {mism[:5]}"))
    except Exception as e:
        results.append(("tick_eq_time_same_bars", False, f"EXC {e}"))

    # 4 full 31-plot schema
    try:
        fkeys = _fire_keys(ft)
        ok = len(fkeys) == 31 and set(f"fire_{p}" for p in CORE.PLOT_IDS) == set(fkeys)
        results.append(("all_31_plots_present", ok,
                        f"{len(fkeys)} fire_ keys; PLOT_IDS={len(CORE.PLOT_IDS)}"))
    except Exception as e:
        results.append(("all_31_plots_present", False, f"EXC {e}"))

    # 5 fire matrix exercised
    try:
        fired = [k for k in _fire_keys(ft) if any(ft[k])]
        results.append(("fire_matrix_exercised", len(fired) >= 10,
                        f"{len(fired)}/31 plots fired"))
    except Exception as e:
        results.append(("fire_matrix_exercised", False, f"EXC {e}"))

    # 6 determinism
    try:
        d1 = MT.compute(H.load_bars(grain="time", n=900), params=SHORT)
        d2 = MT.compute(H.load_bars(grain="time", n=900), params=SHORT)
        results.append(("deterministic", d1 == d2,
                        "stable" if d1 == d2 else "NON-deterministic"))
    except Exception as e:
        results.append(("deterministic", False, f"EXC {e}"))

    # 7 stub-is-zero honesty gate
    try:
        partial_t = getattr(MT, "COMPOSITE_PARTIAL", None)
        partial_k = getattr(MK, "COMPOSITE_PARTIAL", None)
        ok = partial_t == [] and partial_k == []
        # if any port ever declares a partial, that plot MUST be all-zero
        bad = []
        for name in (partial_t or []):
            if any(ft.get(f"fire_{name}", [])):
                bad.append(name)
        results.append(("stub_is_zero_honesty", ok and not bad,
                        f"COMPOSITE_PARTIAL time={partial_t} tick={partial_k}; "
                        f"FULL port, 0 stubs" + (f"; LEAK {bad}" if bad else "")))
    except Exception as e:
        results.append(("stub_is_zero_honesty", False, f"EXC {e}"))

    # 8 cooldown known-plaintext (independent f_cd_ok re-derivation)
    try:
        sig = [False, True, True, True, False, True, False, False, True, True]
        cd = 2
        # independent reference: na(last) or (i-last) > cd ; last := i on fire
        ref = []
        last = None
        for i, s in enumerate(sig):
            if s and (last is None or (i - last) > cd):
                ref.append(1); last = i
            else:
                ref.append(0)
        got = CORE._cd_gate(sig, cd)
        results.append(("cooldown_known_plaintext", got == ref,
                        f"ref={ref} got={got}"))
    except Exception as e:
        results.append(("cooldown_known_plaintext", False, f"EXC {e}"))

    # 9 Nagasaki known-plaintext (independent ATH on volume[1])
    try:
        bars = H.load_bars(grain="time", n=200)
        out = MT.compute(bars, params=SHORT)
        vols = [b.volume for b in bars]
        # independent reference of the PRE-cooldown signal, then apply same cd
        sig = [False] * len(bars)
        mx = 0.0
        for i in range(len(bars)):
            v1 = vols[i - 1] if i - 1 >= 0 else None
            if v1 is not None and v1 > mx:
                mx = v1; sig[i] = True
        ref = CORE._cd_gate(sig, SHORT["cooldown_bars"])
        results.append(("nagasaki_known_plaintext", out["fire_nagasaki"] == ref,
                        f"ref_fires={sum(ref)} got_fires={sum(out['fire_nagasaki'])}"))
    except Exception as e:
        results.append(("nagasaki_known_plaintext", False, f"EXC {e}"))

    # 10 negative control (reversed input differs)
    try:
        bars = H.load_bars(grain="time", n=900)
        rev = list(reversed(bars))
        of = MT.compute(bars, params=SHORT)
        orv = MT.compute(rev, params=SHORT)
        differ = any(of[k] != orv[k] for k in _fire_keys(of))
        results.append(("negative_control", differ,
                        "reversed input -> different matrix" if differ
                        else "IDENTICAL (suspect constant)"))
    except Exception as e:
        results.append(("negative_control", False, f"EXC {e}"))

    # 11 levels present on every fired bar (0/1 + level contract)
    try:
        bars = H.load_bars(grain="time", n=900)
        out = MT.compute(bars, params=SHORT)
        leaks = []
        for pid in CORE.PLOT_IDS:
            f = out[f"fire_{pid}"]; lv = out[f"lvl_{pid}"]
            for i in range(len(f)):
                if f[i] and lv[i] is None:
                    leaks.append((pid, i)); break
        results.append(("levels_present_on_fire", not leaks,
                        "every fired bar has a level" if not leaks
                        else f"missing level(s) {leaks[:5]}"))
    except Exception as e:
        results.append(("levels_present_on_fire", False, f"EXC {e}"))

    # 12 plot count vs source plotshape()
    try:
        if SOURCE.exists():
            src_n = len(re.findall(r"plotshape\(", SOURCE.read_text(errors="ignore")))
            ok = src_n == len(CORE.PLOT_IDS) == 31
            results.append(("plot_count_vs_source", ok,
                            f"source plotshape={src_n}, ported={len(CORE.PLOT_IDS)} "
                            f"(must both == 31; full port, 0 partial)"))
        else:
            results.append(("plot_count_vs_source", False, f"SOURCE missing: {SOURCE}"))
    except Exception as e:
        results.append(("plot_count_vs_source", False, f"EXC {e}"))

    return results


if __name__ == "__main__":
    res = run()
    passed = sum(1 for _, ok, _ in res if ok)
    print(f"=== VOB v10 PARITY: {passed}/{len(res)} ===")
    for name, ok, detail in res:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:26s} {detail}")
    sys.exit(0 if passed == len(res) else 1)
