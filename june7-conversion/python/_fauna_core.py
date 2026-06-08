"""Fauna Dual Mode 2.0 — detection core (Pine-faithful, runtime-grain agnostic).

Source: "fauna dual mode__06_07_124pm.txt" (Pine v5).

Fire matrix:
  7 family booleans per side: MB, RE, GG, TA, TR, ES, GDR  (x bull/bear)
  resolved combo CODE per side (the hierarchical if/else-if winner) -> the thing
    the source painted as a label; here it is a numeric fire (see CODE map).
  bull_active / bear_active = combo CODE != 0 on a closed bar.

CODE map (matches the tick-friendly Pine exactly, in priority order):
  41 GG+MB+RE+TA | 31 MB+TA+RE | 32 GG+TA+MB | 33 GG+TA+RE | 34 GDR+RE+MB |
  21 MB+RE | 22 MB+GG | 23 MB+TA | 24 MB+TR | 25 MB+ES | 26 MB+GDR |
  27 RE+GG | 28 RE+TA | 29 RE+TR | 30 RE+ES | 35 RE+GDR |
  36 GG+TA | 37 GG+TR | 38 GG+ES | 39 GG+GDR | 40 TA+TR | 42 TA+ES | 43 TA+GDR |
  11 GDR | 12 ES | 13 TR | 14 MB | 15 RE | 16 GG | 17 TA | 0 none
"""
from __future__ import annotations

import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nine_nines_common import Bar, atr, sma  # noqa: E402

# Defaults from the Pine inputs (all hardcoded ON families by default).
P = dict(
    alpha_MB=1.6, beta_MB=0.70, delta_MB=1.8, atr_len_MB=14, vol_len_MB=20,
    gamma_RE=2.2, epsilon_RE=0.15, delta_RE=1.8, atr_len_RE=14,
    zeta_GG=0.9, delta_GG=1.8, atr_len_GG=14,
    theta_TA=1.6, delta_TA=1.8, trend_ma_len_TA=50, avg_delta_len=10,
    alpha_SB=1.5, delta_SB=1.5, weak_ratio=0.2, body_avg_len=20, range_avg_len=20,
)

# Bull/bear combo enable toggles (Pine defaults). True/False exactly as source.
BULL_EN = dict(
    GG_MB_RE_TA=True, MB_TA_RE=True, GG_TA_MB=False, GG_TA_RE=False, GDR_RE_MB=False,
    MB_RE=True, MB_GG=False, MB_TA=True, MB_TR=False, MB_ES=False, MB_GDR=False,
    RE_GG=False, RE_TA=False, RE_TR=False, RE_ES=True, RE_GDR=True,
    GG_TA=True, GG_TR=False, GG_ES=False, GG_GDR=True, TA_TR=False, TA_ES=False, TA_GDR=False,
    GDR=True, ES=True, TR=True, MB=True, RE=True, GG=True, TA=True,
)
BEAR_EN = dict(BULL_EN)  # identical default set in the source


def _families(bars: Sequence[Bar]):
    n = len(bars)
    o=[b.open for b in bars]; h=[b.high for b in bars]; l=[b.low for b in bars]
    c=[b.close for b in bars]; v=[b.volume for b in bars]
    ATR=atr(bars, P["atr_len_MB"]); ATR_RE=atr(bars, P["atr_len_RE"]); ATR_GG=atr(bars, P["atr_len_GG"])
    AvgVol=sma(v, P["vol_len_MB"])
    AvgBody=sma([abs(c[i]-o[i]) for i in range(n)], P["body_avg_len"])
    AvgDelta=sma([0.0]+[abs(c[i]-c[i-1]) for i in range(1,n)], P["avg_delta_len"])
    TrendMA=sma(c, P["trend_ma_len_TA"])

    body=[c[i]-o[i] for i in range(n)]; rng=[h[i]-l[i] for i in range(n)]
    bu=[body[i]>0 for i in range(n)]; bd=[body[i]<0 for i in range(n)]
    bsz=[abs(x) for x in body]
    brt=[0.0 if rng[i]==0 else bsz[i]/rng[i] for i in range(n)]

    def vg(i): return AvgVol[i] is not None and v[i] > P["delta_MB"]*AvgVol[i]
    def vgRE(i): return AvgVol[i] is not None and v[i] > P["delta_RE"]*AvgVol[i]
    def vgGG(i): return AvgVol[i] is not None and v[i] > P["delta_GG"]*AvgVol[i]
    def vgTA(i): return AvgVol[i] is not None and v[i] > P["delta_TA"]*AvgVol[i]

    MBb=[False]*n; MBs=[False]*n; REb=[False]*n; REs=[False]*n
    GGb=[False]*n; GGs=[False]*n; TAb=[False]*n; TAs=[False]*n
    for i in range(n):
        if ATR[i] is not None and vg(i):
            MBb[i]=bu[i] and bsz[i]>P["alpha_MB"]*ATR[i] and brt[i]>P["beta_MB"]
            MBs[i]=bd[i] and bsz[i]>P["alpha_MB"]*ATR[i] and brt[i]>P["beta_MB"]
        if ATR_RE[i] is not None and vgRE(i):
            wide=rng[i]>P["gamma_RE"]*ATR_RE[i]
            REb[i]=bu[i] and wide and (h[i]-c[i])<P["epsilon_RE"]*rng[i]
            REs[i]=bd[i] and wide and (c[i]-l[i])<P["epsilon_RE"]*rng[i]
        if i>0 and ATR_GG[i] is not None and vgGG(i):
            GGb[i]=(o[i]-c[i-1])>P["zeta_GG"]*ATR_GG[i] and bu[i] and l[i]>c[i-1]
            GGs[i]=(c[i-1]-o[i])>P["zeta_GG"]*ATR_GG[i] and bd[i] and h[i]<c[i-1]
        if i>0 and AvgDelta[i] is not None and vgTA(i) and TrendMA[i] is not None and TrendMA[i-1] is not None:
            up=TrendMA[i]>TrendMA[i-1]; dn=TrendMA[i]<TrendMA[i-1]
            TAb[i]=up and bu[i] and (c[i]-c[i-1])>P["theta_TA"]*AvgDelta[i]
            TAs[i]=dn and bd[i] and (c[i-1]-c[i])>P["theta_TA"]*AvgDelta[i]

    TRb=[False]*n; ESb=[False]*n; GDRb=[False]*n
    TRs=[False]*n; ESs=[False]*n; GDRs=[False]*n
    for i in range(1, n):
        pbody=c[i-1]-o[i-1]; prng=h[i-1]-l[i-1]
        ab1=AvgBody[i-1]; av1=AvgVol[i-1]
        strongBear = c[i-1]<o[i-1] and ab1 is not None and av1 is not None and abs(pbody)>P["alpha_SB"]*ab1 and v[i-1]>P["delta_SB"]*av1
        weakBear   = c[i-1]<o[i-1] and (0.0 if prng==0 else abs(pbody)/prng)<=P["weak_ratio"]
        strongBull = c[i-1]>o[i-1] and ab1 is not None and av1 is not None and abs(pbody)>P["alpha_SB"]*ab1 and v[i-1]>P["delta_SB"]*av1
        weakBull   = c[i-1]>o[i-1] and (0.0 if prng==0 else abs(pbody)/prng)<=P["weak_ratio"]
        TRb[i]=weakBear and (MBb[i] or REb[i] or TAb[i])
        ESb[i]=strongBear and (MBb[i] or REb[i] or TAb[i])
        GDRb[i]=c[i-1]<o[i-1] and GGb[i]
        TRs[i]=weakBull and (MBs[i] or REs[i] or TAs[i])
        ESs[i]=strongBull and (MBs[i] or REs[i] or TAs[i])
        GDRs[i]=c[i-1]>o[i-1] and GGs[i]
    return dict(MBb=MBb,REb=REb,GGb=GGb,TAb=TAb,TRb=TRb,ESb=ESb,GDRb=GDRb,
                MBs=MBs,REs=REs,GGs=GGs,TAs=TAs,TRs=TRs,ESs=ESs,GDRs=GDRs)


def _resolve(i, fam, en, side):
    """Return the resolved combo CODE for bar i, side='b'(ull) or 's'(ear)."""
    def g(name): return fam[name + side][i]
    MB=g("MB"); RE=g("RE"); GG=g("GG"); TA=g("TA"); TR=g("TR"); ES=g("ES"); GDR=g("GDR")
    # exact priority ladder from the Pine source
    if en["GG_MB_RE_TA"] and GG and MB and RE and TA: return 41
    if en["MB_TA_RE"] and MB and TA and RE: return 31
    if en["GG_TA_MB"] and GG and TA and MB: return 32
    if en["GG_TA_RE"] and GG and TA and RE: return 33
    if en["GDR_RE_MB"] and GDR and RE and MB: return 34
    if en["MB_RE"] and MB and RE: return 21
    if en["MB_GG"] and MB and GG: return 22
    if en["MB_TA"] and MB and TA: return 23
    if en["MB_TR"] and MB and TR: return 24
    if en["MB_ES"] and MB and ES: return 25
    if en["MB_GDR"] and MB and GDR: return 26
    if en["RE_GG"] and RE and GG: return 27
    if en["RE_TA"] and RE and TA: return 28
    if en["RE_TR"] and RE and TR: return 29
    if en["RE_ES"] and RE and ES: return 30
    if en["RE_GDR"] and RE and GDR: return 35
    if en["GG_TA"] and GG and TA: return 36
    if en["GG_TR"] and GG and TR: return 37
    if en["GG_ES"] and GG and ES: return 38
    if en["GG_GDR"] and GG and GDR: return 39
    if en["TA_TR"] and TA and TR: return 40
    if en["TA_ES"] and TA and ES: return 42
    if en["TA_GDR"] and TA and GDR: return 43
    if en["GDR"] and GDR: return 11
    if en["ES"] and ES: return 12
    if en["TR"] and TR: return 13
    if en["MB"] and MB: return 14
    if en["RE"] and RE: return 15
    if en["GG"] and GG: return 16
    if en["TA"] and TA: return 17
    return 0


def compute(bars: Sequence[Bar], *, show_bull=True, show_bear=True):
    n = len(bars)
    fam = _families(bars)
    bull_code=[0]*n; bear_code=[0]*n
    for i in range(n):
        bull_code[i] = _resolve(i, fam, BULL_EN, "b") if show_bull else 0
        bear_code[i] = _resolve(i, fam, BEAR_EN, "s") if show_bear else 0

    def bi(x): return [1 if z else 0 for z in x]
    return {
        "ts": [b.ts for b in bars],
        "bull_combo_code": bull_code,
        "bear_combo_code": bear_code,
        "bull_active": [1 if bull_code[i] != 0 else 0 for i in range(n)],
        "bear_active": [1 if bear_code[i] != 0 else 0 for i in range(n)],
        "MB_bull": bi(fam["MBb"]), "RE_bull": bi(fam["REb"]), "GG_bull": bi(fam["GGb"]),
        "TA_bull": bi(fam["TAb"]), "TR_bull": bi(fam["TRb"]), "ES_bull": bi(fam["ESb"]),
        "GDR_bull": bi(fam["GDRb"]),
        "MB_bear": bi(fam["MBs"]), "RE_bear": bi(fam["REs"]), "GG_bear": bi(fam["GGs"]),
        "TA_bear": bi(fam["TAs"]), "TR_bear": bi(fam["TRs"]), "ES_bear": bi(fam["ESs"]),
        "GDR_bear": bi(fam["GDRs"]),
    }


# ───────────────────────── DETECTION-PLOT REGISTRY ──────────────────────────
# Every detection plot in the tick-friendly Pine source, as a stable id ->
# (descriptor, level_kind). Level kinds:
#   "code"  -> the resolved combo CODE (the numeric id of the hierarchical
#              if/else-if winner; the thing the Pine source painted as a label).
#   "bool"  -> 0/1 family detector (level identical to the fire).
# The 18 plots = 2 plotshape markers (FAUNA Bull / FAUNA Bear) which collapse to
# the combo-code data-window plots, + 14 family booleans (MB/RE/GG/TA/TR/ES/GDR
# x bull/bear). The marker fire == (combo code != 0 on a closed bar); its level
# is the resolved combo CODE. NINE NINES bans label.new, so the painted combo
# text becomes the numeric BULL/BEAR_COMBO_CODE plot (exactly as the source did
# via plot(display=display.data_window)).
PLOT_IDS = {
    # marker / combo-code detection plots (source: plotshape + BULL/BEAR_COMBO_CODE)
    "BULL_COMBO_CODE": ("FAUNA Bull marker; resolved bull combo CODE", "code"),
    "BEAR_COMBO_CODE": ("FAUNA Bear marker; resolved bear combo CODE", "code"),
    # bull family booleans (source: plot(..,"<X>_bull",display=data_window))
    "MB_bull":  ("Momentum Blast (bull)",    "bool"),
    "RE_bull":  ("Range Expansion (bull)",   "bool"),
    "GG_bull":  ("Gap & Go (bull)",          "bool"),
    "TA_bull":  ("Trend Accelerant (bull)",  "bool"),
    "TR_bull":  ("Trapdoor Reversal (bull)", "bool"),
    "ES_bull":  ("Exhaustion Spike (bull)",  "bool"),
    "GDR_bull": ("Gap & Recover (bull)",     "bool"),
    # bear family booleans
    "MB_bear":  ("Momentum Blast (bear)",    "bool"),
    "RE_bear":  ("Range Expansion (bear)",   "bool"),
    "GG_bear":  ("Gap & Go (bear)",          "bool"),
    "TA_bear":  ("Trend Accelerant (bear)",  "bool"),
    "TR_bear":  ("Trapdoor Reversal (bear)", "bool"),
    "ES_bear":  ("Exhaustion Spike (bear)",  "bool"),
    "GDR_bear": ("Gap & Recover (bear)",     "bool"),
}

# No detection plot is stubbed: this is a FULL faithful port (pure OHLCV math).
STUB_IDS: tuple[str, ...] = ()


def fire_matrix(bars: Sequence[Bar], *, show_bull=True, show_bear=True,
                confirmed_only: bool = True):
    """FULL NINE NINES fire matrix: per-bar 0/1 fire + numeric level for EVERY
    detection plot in PLOT_IDS. One code path; grain-bound by the caller (the
    tick wrapper feeds N-tick bars, the time wrapper feeds time bars).

    Pine non-repaint semantics: the source gates the painted markers behind
    `barstate.isconfirmed` (closed bar only). In an offline batch every bar fed
    in IS a closed bar, so confirmed_only is effectively a no-op here but is kept
    explicit (and the partial forming bar is already dropped by the tick binder).

    Returns a dict with:
      ts                          : bar open timestamps
      fire_<id>   (per plot)      : 0/1 fire for that detection plot
      level_<id>  (per plot)      : numeric level
                                      - combo-code plots: the resolved CODE
                                      - family booleans : same 0/1 as the fire
      bull_active / bear_active   : convenience (== fire_BULL/BEAR_COMBO_CODE)
    """
    base = compute(bars, show_bull=show_bull, show_bear=show_bear)
    n = len(bars)
    bull_code = base["bull_combo_code"]
    bear_code = base["bear_combo_code"]
    bull_active = base["bull_active"]
    bear_active = base["bear_active"]

    out: dict = {"ts": base["ts"]}

    # combo-code marker plots: fire == active; level == resolved code on a fire.
    out["fire_BULL_COMBO_CODE"] = list(bull_active)
    out["level_BULL_COMBO_CODE"] = [bull_code[i] if bull_active[i] else 0 for i in range(n)]
    out["fire_BEAR_COMBO_CODE"] = list(bear_active)
    out["level_BEAR_COMBO_CODE"] = [bear_code[i] if bear_active[i] else 0 for i in range(n)]

    # family boolean plots: fire and level are the same 0/1 series.
    for pid in PLOT_IDS:
        if pid in ("BULL_COMBO_CODE", "BEAR_COMBO_CODE"):
            continue
        series = base[pid]
        out["fire_" + pid] = list(series)
        out["level_" + pid] = list(series)

    out["bull_active"] = list(bull_active)
    out["bear_active"] = list(bear_active)
    return out
