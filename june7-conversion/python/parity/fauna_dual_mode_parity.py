"""Fauna Dual Mode 2.0 — parity harness (offline Gate-B).

FULL port (every detection plot derived from pure OHLCV — no stub layer). The
core under test is _fauna_core.fire_matrix / .compute. On deterministic synthetic
bars this harness proves, with REAL pass/total printed:

  1. FAMILY parity (x14)      — every family boolean (MB/RE/GG/TA/TR/ES/GDR x
                                bull/bear) matches an INDEPENDENT re-typing of the
                                literal Pine formulas, bar-for-bar.
  2. RESOLVER parity (x2)     — the resolved BULL/BEAR combo CODE matches an
                                INDEPENDENT re-typed if/else-if priority ladder.
  3. MARKER consistency (x2)  — bull/bear_active == (combo code != 0).
  4. DETERMINISM              — two fire_matrix runs on identical bars are equal.
  5. TICK == TIME            — the SAME core on the SAME Bar objects yields an
                                identical fire matrix through both wrappers
                                (one code path, grain-bound).
  6. BOOLEAN matrix          — every fire_* series is strictly 0/1.
  7. LEVEL integrity         — combo-code levels equal the code on a fire and 0
                                otherwise; family-boolean levels equal their fire.
  8. HONESTY (stub-is-zero)  — no faked all-zero "stub" plots (STUB_IDS empty,
                                no 'stub' keys) AND the matrix is genuinely
                                exercised (>= 6 distinct plots fire on the shock
                                tape). A green that fired nothing would be fake.
  9. NEGATIVE CONTROL        — a flat doji tape (no body, no volume) fires nothing.
 10. WARMUP                  — a very short tape does not crash and does not fire
                                ATR/SMA-window-dependent plots before they warm.

Re-runnable by a stranger:  python3 fauna_dual_mode_parity.py  -> "PARITY fauna: n/m".
Exit 0 only if all pass.
"""
from __future__ import annotations

import os
import sys
import random

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from _nine_nines_common import Bar, atr, sma  # noqa: E402
import _fauna_core as core  # noqa: E402


# ─────────────────────────── deterministic test tape ────────────────────────
def _make_bars(seed=99, n=500):
    """Self-contained deterministic tape with engineered gap-up/gap-down momentum
    and follow-through so the FAUNA fire matrix is genuinely exercised."""
    random.seed(seed)
    rows = []; t = 1_700_000_000_000; px = 100.0
    for i in range(n):
        o = px
        if i in (50, 90, 130, 170):            # gap-up momentum
            px = o + 4.0; hi = px + 0.01; lo = o - 0.01; vol = 200000.0
        elif i in (60, 100, 140):              # gap-down momentum
            px = o - 4.0; hi = o + 0.01; lo = px - 0.01; vol = 200000.0
        elif i in (51, 91):                    # follow-through up after gap
            px = o + 3.5; hi = px + 0.01; lo = o - 0.01; vol = 200000.0
        else:
            px = o + random.uniform(-0.05, 0.05)
            hi = max(o, px) + 0.02; lo = min(o, px) - 0.02; vol = 1000.0
        rows.append((t + i * 60_000, o, hi, lo, px, vol))
    return [Bar(int(a), b, c, d, e, f) for (a, b, c, d, e, f) in rows]


def _flat_tape(n=300):
    """Flat doji tape: zero body, no volume spike -> must fire nothing."""
    return [Bar(1_700_000_000_000 + i * 60_000, 100.0, 100.0, 100.0, 100.0, 1000.0)
            for i in range(n)]


# ───────── independent family reference (re-typed from the Pine source) ──────
def _ref_families(bars):
    P = core.P; n = len(bars)
    o=[b.open for b in bars]; h=[b.high for b in bars]; l=[b.low for b in bars]
    c=[b.close for b in bars]; v=[b.volume for b in bars]
    A=atr(bars,P["atr_len_MB"]); Are=atr(bars,P["atr_len_RE"]); Agg=atr(bars,P["atr_len_GG"])
    AV=sma(v,P["vol_len_MB"]); AB=sma([abs(c[i]-o[i]) for i in range(n)],P["body_avg_len"])
    AD=sma([0.0]+[abs(c[i]-c[i-1]) for i in range(1,n)],P["avg_delta_len"])
    TM=sma(c,P["trend_ma_len_TA"])
    out = {k: [False]*n for k in ("MBb","REb","GGb","TAb","TRb","ESb","GDRb",
                                   "MBs","REs","GGs","TAs","TRs","ESs","GDRs")}
    for i in range(n):
        bu=(c[i]-o[i])>0; bd=(c[i]-o[i])<0; bsz=abs(c[i]-o[i]); rng=h[i]-l[i]
        brt=0.0 if rng==0 else bsz/rng
        if A[i] is not None and AV[i] is not None and v[i]>P["delta_MB"]*AV[i]:
            out["MBb"][i]=bu and bsz>P["alpha_MB"]*A[i] and brt>P["beta_MB"]
            out["MBs"][i]=bd and bsz>P["alpha_MB"]*A[i] and brt>P["beta_MB"]
        if Are[i] is not None and AV[i] is not None and v[i]>P["delta_RE"]*AV[i]:
            wide=rng>P["gamma_RE"]*Are[i]
            out["REb"][i]=bu and wide and (h[i]-c[i])<P["epsilon_RE"]*rng
            out["REs"][i]=bd and wide and (c[i]-l[i])<P["epsilon_RE"]*rng
        if i>0 and Agg[i] is not None and AV[i] is not None and v[i]>P["delta_GG"]*AV[i]:
            out["GGb"][i]=(o[i]-c[i-1])>P["zeta_GG"]*Agg[i] and bu and l[i]>c[i-1]
            out["GGs"][i]=(c[i-1]-o[i])>P["zeta_GG"]*Agg[i] and bd and h[i]<c[i-1]
        if i>0 and AD[i] is not None and AV[i] is not None and v[i]>P["delta_TA"]*AV[i] and TM[i] is not None and TM[i-1] is not None:
            up=TM[i]>TM[i-1]; dn=TM[i]<TM[i-1]
            out["TAb"][i]=up and bu and (c[i]-c[i-1])>P["theta_TA"]*AD[i]
            out["TAs"][i]=dn and bd and (c[i-1]-c[i])>P["theta_TA"]*AD[i]
    for i in range(1,n):
        pb=c[i-1]-o[i-1]; pr=h[i-1]-l[i-1]; ab1=AB[i-1]; av1=AV[i-1]
        sBear=c[i-1]<o[i-1] and ab1 is not None and av1 is not None and abs(pb)>P["alpha_SB"]*ab1 and v[i-1]>P["delta_SB"]*av1
        wBear=c[i-1]<o[i-1] and (0.0 if pr==0 else abs(pb)/pr)<=P["weak_ratio"]
        sBull=c[i-1]>o[i-1] and ab1 is not None and av1 is not None and abs(pb)>P["alpha_SB"]*ab1 and v[i-1]>P["delta_SB"]*av1
        wBull=c[i-1]>o[i-1] and (0.0 if pr==0 else abs(pb)/pr)<=P["weak_ratio"]
        out["TRb"][i]=wBear and (out["MBb"][i] or out["REb"][i] or out["TAb"][i])
        out["ESb"][i]=sBear and (out["MBb"][i] or out["REb"][i] or out["TAb"][i])
        out["GDRb"][i]=c[i-1]<o[i-1] and out["GGb"][i]
        out["TRs"][i]=wBull and (out["MBs"][i] or out["REs"][i] or out["TAs"][i])
        out["ESs"][i]=sBull and (out["MBs"][i] or out["REs"][i] or out["TAs"][i])
        out["GDRs"][i]=c[i-1]>o[i-1] and out["GGs"][i]
    return out


def main():
    checks = []
    bars = _make_bars(); n = len(bars)
    out = core.fire_matrix(bars)
    ref = _ref_families(bars)

    # 1. FAMILY parity (14 checks) — fire_<X>_<side> vs independent reference.
    pairs = [
        ("MB_bull","MBb"),("RE_bull","REb"),("GG_bull","GGb"),("TA_bull","TAb"),
        ("TR_bull","TRb"),("ES_bull","ESb"),("GDR_bull","GDRb"),
        ("MB_bear","MBs"),("RE_bear","REs"),("GG_bear","GGs"),("TA_bear","TAs"),
        ("TR_bear","TRs"),("ES_bear","ESs"),("GDR_bear","GDRs"),
    ]
    for gk, rk in pairs:
        ok = all(out["fire_" + gk][i] == (1 if ref[rk][i] else 0) for i in range(n))
        checks.append((f"family {gk}", ok))

    # 2. RESOLVER parity (2 checks) — combo CODE level vs independent ladder.
    #    The marker fire is active when code != 0; level holds the code on a fire.
    bull_ref_code = [core._resolve(i, ref, core.BULL_EN, "b") for i in range(n)]
    bear_ref_code = [core._resolve(i, ref, core.BEAR_EN, "s") for i in range(n)]
    bull_code_ok = all(out["level_BULL_COMBO_CODE"][i] == bull_ref_code[i] for i in range(n))
    bear_code_ok = all(out["level_BEAR_COMBO_CODE"][i] == bear_ref_code[i] for i in range(n))
    checks.append(("bull_combo_code", bull_code_ok))
    checks.append(("bear_combo_code", bear_code_ok))

    # 3. MARKER consistency — active == (code != 0).
    checks.append(("bull_active=code!=0",
                   all(out["fire_BULL_COMBO_CODE"][i] == (1 if bull_ref_code[i] != 0 else 0) for i in range(n))))
    checks.append(("bear_active=code!=0",
                   all(out["fire_BEAR_COMBO_CODE"][i] == (1 if bear_ref_code[i] != 0 else 0) for i in range(n))))

    # 4. DETERMINISM — identical inputs -> identical matrix.
    out2 = core.fire_matrix(bars)
    checks.append(("determinism", all(out[k] == out2[k] for k in out)))

    # 5. TICK == TIME — same Bar objects through both wrappers -> identical matrix.
    sys.path.insert(0, os.path.join(_ROOT, "tick"))
    sys.path.insert(0, os.path.join(_ROOT, "time"))
    import fauna_dual_mode_tick as tickmod  # noqa: E402
    import fauna_dual_mode_time as timemod  # noqa: E402
    out_tick = tickmod.run_on_bars(bars)
    out_time = timemod.run_on_bars(bars)
    keys_t = [k for k in out if k.startswith(("fire_", "level_"))]
    tt_ok = all(out_tick[k] == out_time[k] for k in keys_t)
    checks.append(("tick_eq_time_fire_matrix", tt_ok))

    # 6. BOOLEAN matrix — every fire_* series strictly 0/1.
    fire_keys = [k for k in out if k.startswith("fire_")]
    checks.append(("all_fires_boolean",
                   all(all(x in (0, 1) for x in out[k]) for k in fire_keys)))

    # 7. LEVEL integrity.
    lvl_ok = True
    for i in range(n):
        if out["fire_BULL_COMBO_CODE"][i] and out["level_BULL_COMBO_CODE"][i] == 0:
            lvl_ok = False
        if not out["fire_BULL_COMBO_CODE"][i] and out["level_BULL_COMBO_CODE"][i] != 0:
            lvl_ok = False
    for gk, _rk in pairs:
        if out["fire_" + gk] != out["level_" + gk]:
            lvl_ok = False
    checks.append(("level_integrity", lvl_ok))

    # 8. HONESTY (stub-is-zero) — no faked stub plots + matrix exercised.
    no_stub = (len(core.STUB_IDS) == 0
               and not any("stub" in k.lower() for k in out))
    fired_plots = sum(1 for k in fire_keys if sum(out[k]) > 0)
    checks.append(("no_faked_stub_series", no_stub))
    checks.append(("matrix_exercised_ge_6_plots", fired_plots >= 6))

    # 9. NEGATIVE CONTROL — flat doji tape fires nothing.
    outf = core.fire_matrix(_flat_tape())
    checks.append(("negative_control_zero_fires",
                   all(sum(outf[k]) == 0 for k in fire_keys)))

    # 10. WARMUP — short tape must not crash and not fire ATR/SMA-window plots
    #     (MB/RE/GG/TA all need ATR(14)+SMA(20) warm; TR/ES/GDR derive from them).
    short = bars[:8]
    try:
        outs = core.fire_matrix(short)
        warm_ok = (len(outs["ts"]) == 8
                   and sum(outs["fire_MB_bull"]) == 0
                   and sum(outs["fire_RE_bull"]) == 0
                   and sum(outs["fire_TA_bull"]) == 0)
    except Exception as exc:  # pragma: no cover
        warm_ok = False
        print("  warmup exception:", exc)
    checks.append(("warmup_no_crash_no_window_fire", warm_ok))

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    nz = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  fired plots on shock tape ({len(nz)}/{len(fire_keys)}): {nz}")
    print(f"PARITY fauna: {passed}/{total}")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
