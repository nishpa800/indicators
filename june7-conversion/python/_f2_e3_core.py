"""f2 e3 — detection core (Pine-faithful, runtime-grain agnostic).

ULTRACODE FULL PORT — every detection plot is ported 1:1; nothing is stubbed.

Source (read from disk, quoted exactly):
  "/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT transformed
   yet/June 7/Tick Friendly conversion/f2_e3_tickfriendly.pine"
  Pine v5, indicator "e3 f2 cluster THIS bull bear 58% reduction THIS"
  (shorttitle "f2 e3 58%"), source file "f2 e3_06_07_124pm.txt".

DETECTION PLOTS (the fire matrix — every plotshape in the Pine PLOTS block):
  S1 Bull FC Cluster   sBullFC   (Pine L311 plotshape "Bull FC Cluster")
  S2 Bull E3           sBullE3   (Pine L312 plotshape "Bull E3")
  S3 Bull First Two    sBullF2   (Pine L313 plotshape "Bull First Two")
  S4 Bear FC Cluster   sBearFC   (Pine L314 plotshape "Bear FC Cluster")
  S5 Bear E3           sBearE3   (Pine L315 plotshape "Bear E3")
  S6 Bear First Two    sBearF2   (Pine L316 plotshape "Bear First Two")
  S7 Any Bull          sAnyBull  (Pine L317 plotshape "Any Bull")
  S8 Any Bear          sAnyBear  (Pine L318 plotshape "Any Bear")

This is bar-sequential state-machine Pine (var int counters, var float[] arrays,
while-loop eviction, for-loop overlap scan), ported 1:1 to explicit Python state.
The SAME core runs on N-tick bars and on time bars (one code path); only the
caller (tick/ vs time/ wrapper) differs in how it builds the Bar list.

NINE NINES note: detection = per-bar 0/1 fires + numeric debug levels in the
returned dict. No graphic label objects (matches the Pine, which is plotshape
only — the source header certifies no label.new).

PINE-SEMANTICS PRESERVED:
  * `var` counters / arrays  -> explicit Python locals carried across the bar loop.
  * `ta.atr(14)`             -> Wilder RMA of true range (_nine_nines_common.atr).
  * `ta.sma(...)`            -> simple MA, first (length-1) bars na (None).
  * `ta.sma(x,30)[1]`        -> previous bar's SMA value (smaP[i-1]).
  * `ta.sma(b_pos, 20)` where b_pos is na on most bars -> Pine na-propagating SMA
                              (window value is None unless ALL `length` window
                              entries are non-None) -> _sma_napropagate.
  * `nz(x, repl)`            -> repl only when x is na (None); NOT when x == 0.
  * `barstate.isconfirmed`   -> always True (we score CLOSED bars only).
  * session gate / sessBar   -> ported from time((tf),"0930-1600","America/New_York")
                              + ta.change(dayofmonth) bar counter.

EVERY THRESHOLD IS A PARAMETER (Params dataclass) — none hardcoded inline.
"""
from __future__ import annotations

import os
import sys
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nine_nines_common import Bar, atr, sma  # noqa: E402

# Stable detection-plot ids (id -> descriptor). Same-named signals across other
# indicators are NOT equivalent; these are scoped to f2_e3.
PLOT_IDS = {
    "S1_bull_fc": "Bull FC Cluster (2-of-3 sequence inds AND theta/seq box overlap)",
    "S2_bull_e3": "Bull E3 (sessBar==3 AND 3-in-a-row MB|RE|TA)",
    "S3_bull_f2": "Bull First Two (sessBar==2 AND two consecutive bull MB)",
    "S4_bear_fc": "Bear FC Cluster (2-of-3 sequence inds AND theta/seq box overlap)",
    "S5_bear_e3": "Bear E3 (sessBar==3 AND 3-in-a-row MB|RE|TA)",
    "S6_bear_f2": "Bear First Two (sessBar==2 AND two consecutive bear MB)",
    "S7_any_bull": "Any Bull (S1 OR S2 OR S3)",
    "S8_any_bear": "Any Bear (S4 OR S5 OR S6)",
}


@dataclass(frozen=True)
class Params:
    """Every Pine literal/threshold surfaced as an adjustable parameter.

    Defaults are the EXACT values in the Pine source. Changing a default here is
    the single place to tune the detector at scale (NINE NINES rule: no inline
    hardcoded thresholds).
    """
    atr_len: int = 14                 # ta.atr(14)
    vol_len: int = 20                 # ta.sma(volume, 20) -> avgVol20
    delta_len: int = 10               # ta.sma(abs(close-close[1]), 10) -> avgDelta
    trend_len: int = 50               # ta.sma(close, 50) -> trendMA
    wide_k: float = 2.2               # rng > 2.2 * atr14
    mb_body_k: float = 1.6            # bodySize > 1.6 * atr14
    mb_ratio: float = 0.7             # bodyRatio > 0.7
    vol_k: float = 1.8                # volume > 1.8 * avgVol20
    re_edge: float = 0.15             # (high-close)<0.15*rng / (close-low)<0.15*rng
    ta_delta_k: float = 1.6           # (close-close[1]) > 1.6 * avgDelta
    seq_min: int = 2                  # s1/s2/s3 >= 2 ; FC 2-of-3 ; F2 two-MB ; E3 3-in-row
    twoofthree_min: int = 2           # (ind1+ind2+ind3) >= 2
    e3_sessbar: int = 3               # sessBar == 3
    f2_sessbar: int = 2               # sessBar == 2
    ovl_window: int = 20              # bar_index - idx > 20 eviction
    sma_spk_len: int = 30             # ta.sma(spk,30) and ta.sma(volume,30)
    sma_pos_len: int = 20             # ta.sma(b_pos,20)
    bull_seq_sum: float = 0.1         # b1_sum >= 0.1
    bear_seq_sum: float = 0.5         # b4_sum >= 0.5
    rvol_lo: float = 2.9              # inRng: v > 2.9
    rvol_hi: float = 1_000_000.0      # inRng: v < 1000000.0
    seq_len_min: int = 2              # b_len >= 2
    sess_open_min: int = 9 * 60 + 30  # 0930 ET
    sess_close_min: int = 16 * 60     # 1600 ET


def _ny_minutes(ts_ms: int) -> int:
    """Wall-clock minutes-from-midnight in US/Eastern for a bar timestamp.

    Pine uses time(tf, "0930-1600", "America/New_York"); na outside the window.
    Crude DST (Mar-Nov -> EDT(-4), else EST(-5)). The parity harness feeds
    Eastern-anchored UTC timestamps so the window matches deterministically;
    real runtime should pass exchange-local-anchored ts (TASK 4, candle SOW).
    """
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    offset = -4 if 3 <= dt.month <= 11 else -5
    ldt = datetime.fromtimestamp(dt.timestamp() + offset * 3600, tz=timezone.utc)
    return ldt.hour * 60 + ldt.minute


def _sma_napropagate(series: Sequence[float | None], length: int) -> list[float | None]:
    """Pine ta.sma over a series that contains na (None) entries.

    Pine semantics: ta.sma sums the last `length` source values; if ANY value in
    that window is na, the sum is na -> result na. The window advances by bar
    (na bars still occupy a slot). So the result is non-na only when the rolling
    window holds `length` consecutive non-na values.
    """
    out: list[float | None] = []
    win: deque[float | None] = deque()
    for val in series:
        win.append(val)
        if len(win) > length:
            win.popleft()
        if len(win) == length and all(x is not None for x in win):
            out.append(sum(x for x in win if x is not None) / length)  # type: ignore[misc]
        else:
            out.append(None)
    return out


def compute(bars: Sequence[Bar], *, use_session: bool = True,
            params: Params | None = None) -> dict[str, list]:
    """Return the per-bar fire matrix + numeric debug levels for f2 e3.

    use_session=False forces inSession True for every bar (matches a Pine chart
    whose session filter is satisfied everywhere — used by deterministic parity
    tests so the fire matrix is grain-independent).
    """
    p = params or Params()
    n = len(bars)
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    lo = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]

    if n == 0:
        return _empty_result()

    # ── SHARED CORE CALCULATIONS (Pine L62-L75) ──────────────────────────────
    atr14 = atr(bars, p.atr_len)                 # ta.atr(14)
    avgVol20 = sma(v, p.vol_len)                 # ta.sma(volume, 20)
    absDelta = [0.0] + [abs(c[i] - c[i - 1]) for i in range(1, n)]
    avgDelta = sma(absDelta, p.delta_len)        # ta.sma(abs(close-close[1]), 10)
    trendMA = sma(c, p.trend_len)                # ta.sma(close, 50)

    body = [c[i] - o[i] for i in range(n)]
    rng = [h[i] - lo[i] for i in range(n)]
    bodySize = [abs(b) for b in body]
    bodyRatio = [0.0 if rng[i] == 0 else bodySize[i] / rng[i] for i in range(n)]
    bodyUp = [body[i] > 0 for i in range(n)]
    bodyDn = [body[i] < 0 for i in range(n)]
    wide = [(atr14[i] is not None) and (rng[i] > p.wide_k * atr14[i]) for i in range(n)]
    upTrend = [False] + [
        (trendMA[i] is not None and trendMA[i - 1] is not None and trendMA[i] > trendMA[i - 1])
        for i in range(1, n)
    ]
    dnTrend = [False] + [
        (trendMA[i] is not None and trendMA[i - 1] is not None and trendMA[i] < trendMA[i - 1])
        for i in range(1, n)
    ]

    # session gate (Pine L75) + new-day change (Pine ta.change(dayofmonth))
    if use_session:
        inSession = []
        for i in range(n):
            m = _ny_minutes(bars[i].ts)
            inSession.append(p.sess_open_min <= m < p.sess_close_min)
    else:
        inSession = [True] * n

    day_ord = [datetime.fromtimestamp(b.ts / 1000, tz=timezone.utc).day for b in bars]
    change_day = [False] + [day_ord[i] != day_ord[i - 1] for i in range(1, n)]

    def volgate(i: int) -> bool:
        return avgVol20[i] is not None and v[i] > p.vol_k * avgVol20[i]

    # ── BULL / BEAR EVENTS (Pine L78-L85) ────────────────────────────────────
    bull_MB = [False] * n; bull_RE = [False] * n; bull_TA = [False] * n
    bear_MB = [False] * n; bear_RE = [False] * n; bear_TA = [False] * n
    for i in range(n):
        ag = atr14[i] is not None
        vg = volgate(i)
        if ag and vg:
            big_body = bodySize[i] > p.mb_body_k * atr14[i] and bodyRatio[i] > p.mb_ratio
            bull_MB[i] = bodyUp[i] and big_body
            bear_MB[i] = bodyDn[i] and big_body
            bull_RE[i] = bodyUp[i] and wide[i] and (h[i] - c[i]) < p.re_edge * rng[i]
            bear_RE[i] = bodyDn[i] and wide[i] and (c[i] - lo[i]) < p.re_edge * rng[i]
        if vg and avgDelta[i] is not None and i > 0:
            bull_TA[i] = upTrend[i] and (c[i] - c[i - 1]) > p.ta_delta_k * avgDelta[i] and bodyUp[i]
            bear_TA[i] = dnTrend[i] and (c[i - 1] - c[i]) > p.ta_delta_k * avgDelta[i] and bodyDn[i]

    # ── SESSION BAR COUNTER (Pine L88-L98) ───────────────────────────────────
    sessBar = [0] * n
    is_new_day = False
    cur = 0
    for i in range(n):
        if change_day[i]:
            is_new_day = True
        if is_new_day and inSession[i]:
            cur = 1
            is_new_day = False
        elif inSession[i] and cur > 0:
            cur += 1
        elif not inSession[i]:
            cur = 0
        sessBar[i] = cur

    # ── FC CLUSTER ENGINE (Pine L100-L189 bull / L201-L289 bear) ─────────────
    sBullFC, bull_dbg = _fc_engine(
        is_bull=True, n=n, h=h, lo=lo, body=body, bodySize=bodySize,
        bodyUp=bodyUp, bodyDn=bodyDn, v=v, change_day=change_day, inSession=inSession,
        ev_MB=bull_MB, ev_RE=bull_RE, ev_TA=bull_TA, p=p,
    )
    sBearFC, bear_dbg = _fc_engine(
        is_bull=False, n=n, h=h, lo=lo, body=body, bodySize=bodySize,
        bodyUp=bodyUp, bodyDn=bodyDn, v=v, change_day=change_day, inSession=inSession,
        ev_MB=bear_MB, ev_RE=bear_RE, ev_TA=bear_TA, p=p,
    )

    # ── E3 / FIRST-TWO (Pine S2/S3/S5/S6: L193-L199, L294-L300) ──────────────
    sBullE3 = [False] * n; sBearE3 = [False] * n
    sBullF2 = [False] * n; sBearF2 = [False] * n
    for i in range(n):
        bev = bull_MB[i] or bull_RE[i] or bull_TA[i]
        sev = bear_MB[i] or bear_RE[i] or bear_TA[i]
        if i >= 2:
            bev1 = bull_MB[i - 1] or bull_RE[i - 1] or bull_TA[i - 1]
            bev2 = bull_MB[i - 2] or bull_RE[i - 2] or bull_TA[i - 2]
            sev1 = bear_MB[i - 1] or bear_RE[i - 1] or bear_TA[i - 1]
            sev2 = bear_MB[i - 2] or bear_RE[i - 2] or bear_TA[i - 2]
            sBullE3[i] = sessBar[i] == p.e3_sessbar and bev and bev1 and bev2
            sBearE3[i] = sessBar[i] == p.e3_sessbar and sev and sev1 and sev2
        if i >= 1:
            sBullF2[i] = sessBar[i] == p.f2_sessbar and bull_MB[i] and bull_MB[i - 1]
            sBearF2[i] = sessBar[i] == p.f2_sessbar and bear_MB[i] and bear_MB[i - 1]

    # ── ANY BULL / ANY BEAR (Pine S7/S8: L305-L306) ──────────────────────────
    sAnyBull = [sBullFC[i] or sBullE3[i] or sBullF2[i] for i in range(n)]
    sAnyBear = [sBearFC[i] or sBearE3[i] or sBearF2[i] for i in range(n)]

    def b(x):
        return [1 if z else 0 for z in x]

    return {
        "ts": [bar.ts for bar in bars],
        # detection plots (fire matrix)
        "S1_bull_fc": b(sBullFC),
        "S2_bull_e3": b(sBullE3),
        "S3_bull_f2": b(sBullF2),
        "S4_bear_fc": b(sBearFC),
        "S5_bear_e3": b(sBearE3),
        "S6_bear_f2": b(sBearF2),
        "S7_any_bull": b(sAnyBull),
        "S8_any_bear": b(sAnyBear),
        # numeric debug levels (Pine display.data_window equivalents)
        "lvl_atr14": atr14,
        "lvl_sessBar": sessBar,
        "ev_bull_MB": b(bull_MB),
        "ev_bull_RE": b(bull_RE),
        "ev_bull_TA": b(bull_TA),
        "ev_bear_MB": b(bear_MB),
        "ev_bear_RE": b(bear_RE),
        "ev_bear_TA": b(bear_TA),
        "lvl_bull_rvolP": bull_dbg["rvolP"],
        "lvl_bear_rvolP": bear_dbg["rvolP"],
        "ev_bull_2of3": b(bull_dbg["twoofthree"]),
        "ev_bear_2of3": b(bear_dbg["twoofthree"]),
        "ev_bull_ovlp": b(bull_dbg["ovlp"]),
        "ev_bear_ovlp": b(bear_dbg["ovlp"]),
    }


def _fc_engine(*, is_bull: bool, n: int, h, lo, body, bodySize, bodyUp, bodyDn,
               v, change_day, inSession, ev_MB, ev_RE, ev_TA,
               p: Params) -> tuple[list[bool], dict[str, list]]:
    """Port of the Pine FC-cluster block (b1 bull / b4 bear).

    Returns (fc_fire_per_bar, debug_dict). fc = 2-of-3 AND box overlap.
    """
    seq_sum_thresh = p.bull_seq_sum if is_bull else p.bear_seq_sum

    # spk / rvolP / rvolV  (Pine L128-L133 / L229-L234)
    spk = bodySize[:]                                   # math.abs(body)
    smaP_spk = sma(spk, p.sma_spk_len)                  # ta.sma(spk,30)
    smaV = sma(v, p.sma_spk_len)                        # ta.sma(volume,30)
    rvolP = [0.0] * n
    rvolV = [0.0] * n
    for i in range(n):
        # Pine: ta.sma(...,30)[1] => previous bar's value; nz(...,1) => 1 if na.
        prevP = smaP_spk[i - 1] if i > 0 else None
        prevV = smaV[i - 1] if i > 0 else None
        denomP = prevP if prevP is not None else 1.0     # nz(b_avgSpk, 1)
        denomV = prevV if prevV is not None else 1.0     # nz(b_avgVolD, 1)
        # guard div-by-zero (Pine would yield inf/na on exactly-0 SMA; rare).
        rvolP[i] = spk[i] / (denomP if denomP != 0 else 1.0)
        rvolV[i] = v[i] / (denomV if denomV != 0 else 1.0)

    diff = [rvolP[i] - rvolV[i] for i in range(n)]
    # Pine L134: bull pos = diff>0 ? diff : na
    # Pine L235: bear neg = (diff>0 and bodyDn) ? diff : na
    if is_bull:
        pos = [diff[i] if diff[i] > 0 else None for i in range(n)]
    else:
        pos = [diff[i] if (diff[i] > 0 and bodyDn[i]) else None for i in range(n)]
    smaPos = _sma_napropagate(pos, p.sma_pos_len)        # ta.sma(b_pos, 20)

    def inrng(x: float) -> bool:                         # b_inRng(v)
        return p.rvol_lo < x < p.rvol_hi

    def overlap(loA, hiA, loB, hiB) -> bool:             # b_chk(loA,hiA,loB,hiB)
        return loA <= hiB and loB <= hiA

    # var state
    s1 = 0; s2 = 0; s3 = 0
    seq_len = 0; seq_sum = 0.0
    ind1 = [False] * n; ind2 = [False] * n; ind3 = [False] * n
    twoofthree = [False] * n
    ovlp = [False] * n
    thIdx: list[int] = []; thHi: list[float] = []; thLo: list[float] = []
    sqIdx: list[int] = []; sqHi: list[float] = []; sqLo: list[float] = []

    for i in range(n):
        # 1.1 MB sequence (Pine L104-L106 / L205-L207)
        s1 = s1 + 1 if ev_MB[i] else 0
        ind1[i] = ev_MB[i] and s1 >= p.seq_min
        # 1.2 MBRETA sequence (Pine L109-L117 / L210-L218)
        ev2 = ev_MB[i] or ev_RE[i] or ev_TA[i]
        if change_day[i]:
            s2 = 0
        elif not ev2:
            s2 = 0
        if ev2:
            s2 += 1
        ind2[i] = ev2 and s2 >= p.seq_min
        # 1.3 MB+RE session (Pine L120-L123 / L221-L224)
        ev3 = (ev_MB[i] or ev_RE[i]) and inSession[i]
        s3 = s3 + 1 if ev3 else 0
        ind3[i] = ev3 and s3 >= p.seq_min
        # 2-of-3 (Pine L125 / L226)
        twoofthree[i] = (int(ind1[i]) + int(ind2[i]) + int(ind3[i])) >= p.twoofthree_min

        # base / thEv / uBar (Pine L136-L139 / L237-L240)
        base_dir = bodyUp[i] if is_bull else bodyDn[i]
        pos_nz = 0.0 if pos[i] is None else pos[i]
        smaPos_nz = 0.0 if smaPos[i] is None else smaPos[i]
        base = base_dir and (pos_nz > smaPos_nz)
        # barstate.isconfirmed == True on closed bars
        thEv = base and inrng(rvolP[i])
        uBar = base and inrng(rvolP[i])

        # seq accumulator (Pine L143-L149 / L244-L250)
        if uBar:
            seq_len += 1
            seq_sum += rvolP[i]
        else:
            seq_len = 0
            seq_sum = 0.0
        seqEv = (seq_len >= p.seq_len_min and seq_sum >= seq_sum_thresh)

        # array eviction: bar_index - idx > window (Pine L159-L168 / L260-L269)
        while thIdx and i - thIdx[0] > p.ovl_window:
            thIdx.pop(0); thHi.pop(0); thLo.pop(0)
        while sqIdx and i - sqIdx[0] > p.ovl_window:
            sqIdx.pop(0); sqHi.pop(0); sqLo.pop(0)

        # NOTE on Pine var-array overlap semantics (L172-L186 / L273-L287):
        # `b_ovlp` is a plain (non-var) bool re-init False each bar. On a theta
        # event we push the theta box AND scan EXISTING seq boxes; on a seq event
        # (only if not already overlapping) we push the seq box AND scan EXISTING
        # theta boxes. Because b_ovlp is bar-local, the per-bar value is what
        # matters for sBullFC = b1_2of3 and b1_ovlp.
        cur_ovlp = False
        if thEv:
            for j in range(len(sqIdx)):
                if overlap(lo[i], h[i], sqLo[j], sqHi[j]):
                    cur_ovlp = True
                    break
            thIdx.append(i); thHi.append(h[i]); thLo.append(lo[i])
        if seqEv and not cur_ovlp:
            for j in range(len(thIdx)):
                if overlap(lo[i], h[i], thLo[j], thHi[j]):
                    cur_ovlp = True
                    break
            sqIdx.append(i); sqHi.append(h[i]); sqLo.append(lo[i])
        ovlp[i] = cur_ovlp

    fc = [twoofthree[i] and ovlp[i] for i in range(n)]
    dbg = {
        "rvolP": rvolP,
        "twoofthree": twoofthree,
        "ovlp": ovlp,
        "ind1": ind1, "ind2": ind2, "ind3": ind3,
    }
    return fc, dbg


def _empty_result() -> dict[str, list]:
    keys = (
        list(PLOT_IDS.keys())
        + ["lvl_atr14", "lvl_sessBar",
           "ev_bull_MB", "ev_bull_RE", "ev_bull_TA",
           "ev_bear_MB", "ev_bear_RE", "ev_bear_TA",
           "lvl_bull_rvolP", "lvl_bear_rvolP",
           "ev_bull_2of3", "ev_bear_2of3", "ev_bull_ovlp", "ev_bear_ovlp"]
    )
    out: dict[str, list] = {"ts": []}
    for k in keys:
        out[k] = []
    return out
