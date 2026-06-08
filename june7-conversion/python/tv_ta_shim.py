"""Canonical Python shim for TradingView's `tv_ta.relativeVolume()` (ta v7).

THIS IS THE ONLY SANCTIONED IMPLEMENTATION of relativeVolume in the entire
quant stack. Every Pine port that calls `tv_ta.relativeVolume(...)` MUST import
from here. DO NOT re-implement relativeVolume anywhere else, and in particular
DO NOT approximate it as `volume / ta.sma(volume, N)` — that is a different,
wrong formula (it ignores the intraday volume "smile" and the session anchor).

Pine source it ports (vault: sources/tradingview/pine_libraries/raw/TradingView__ta__v7.pine, L342):

    import TradingView/RelativeValue/2 as TVrv
    export relativeVolume(
         simple int  length,              simple string anchorTimeframe = "D",
         simple bool isCumulative = true, simple bool   adjustRealtime  = true
     ) =>
        bool  anchor   = timeframe.change(anchorTimeframe)
        float currVol  = isCumulative ? TVrv.calcCumulativeSeries(volume, anchor, adjustRealtime) : volume
        float pastVol  = TVrv.averageAtTime(volume, length, anchorTimeframe, isCumulative)
        float volRatio = currVol / pastVol
        [currVol, pastVol, volRatio]

The two `RelativeValue/2` helpers are SOURCE-LOCKED (HTTP 401 for everyone), so
they are reimplemented here from TradingView's documented spec and verified
against TradingView's own plotted numbers (known-plaintext). Their meaning:

  calcCumulativeSeries(volume, anchor, adjustRealtime)
      = running sum of `volume` since the most recent anchor reset (e.g. the
        session open for anchorTimeframe="D"). `adjustRealtime` only affects the
        still-forming bar, which is IRRELEVANT here because we compare CLOSED
        bars only.

  averageAtTime(volume, length, anchorTimeframe, isCumulative)
      = the value (cumulative-since-anchor if isCumulative else raw volume) at
        the SAME clock offset from the anchor as the current bar, averaged over
        the last `length` completed sessions. This is "Relative Volume at Time"
        and respects the intraday volume smile. It is NOT volume/SMA(volume,N).

THE EQUATION (isCumulative=True, the suite default)
---------------------------------------------------
Let bar i sit at intraday offset k from its session anchor (k = number of bars
since that session's anchor reset, 0-indexed). Let C(i) be the cumulative volume
from the session anchor of bar i through bar i inclusive:

    C(i) = sum( volume[j] for j in [anchor_of(i) .. i] )

Then for the current bar t at offset k_t, over the previous `length` sessions
s in {1..length} that contain a bar at the SAME offset k_t:

    currVol(t) = C(t)
    pastVol(t) = mean over those s of C(bar in session s at offset k_t)
    volRatio   = currVol / pastVol

isCumulative=False replaces C(.) with raw volume.

VERSION: ta/7 — anchorTimeframe default "D", RelativeValue/2. (ta/12 differs:
default "1D", RelativeValue/3 — DO NOT use those defaults here.)

HISTORY: output depends on `length` AND on how much history is loaded. Provide at
least `length`+1 full sessions of bars. (Same reason TradingView "Fast
Calculation" is BANNED — it truncates history and moves the plots.)

CLOSED BARS ONLY: we only ever score confirmed/painted bars, so `adjustRealtime`
and realtime nondeterminism drop out entirely.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

import math

__all__ = [
    "relative_volume",
    "RelativeVolumeResult",
    "session_offsets",
    "SHIM_VERSION",
    "TA_LIBRARY_VERSION",
]

SHIM_VERSION = "1.0.0"
TA_LIBRARY_VERSION = "TradingView/ta/7 (RelativeValue/2)"

# Pine `timeframe.change("D")` is keyed off the exchange session/day boundary.
# We anchor on the UTC calendar day by default; callers feeding exchange-local
# bar timestamps get exchange-day anchoring automatically because the day index
# is computed from whatever epoch the timestamps already encode. The only
# requirement is that bar_timestamps be monotonic and consistent.
_MS_PER_DAY = 86_400_000


@dataclass(frozen=True, slots=True)
class RelativeVolumeResult:
    """Per-bar output, mirroring Pine's [currVol, pastVol, volRatio] tuple.

    Arrays are aligned 1:1 with the input `volume` series (oldest-first). Where
    there is insufficient history to form `pastVol`, the entry is None (Pine na).
    """

    curr_vol: list[float | None]
    past_vol: list[float | None]
    vol_ratio: list[float | None]


def _day_index(ts_ms: int, anchor_timeframe: str) -> int:
    """Integer session bucket for a bar timestamp.

    For anchorTimeframe "D"/"1D" (the only modes the suite uses) this is the
    UTC calendar-day ordinal. A new value of this index == a Pine
    `timeframe.change(anchorTimeframe)` == True (session reset).

    For non-daily anchors we fall back to flooring by the anchor's millisecond
    span so the shim degrades gracefully rather than silently mis-bucketing.
    """
    tf = anchor_timeframe.strip().upper()
    if tf in ("D", "1D", ""):
        # Calendar-day ordinal in whatever timezone the timestamps encode.
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        return dt.toordinal()
    if tf in ("W", "1W"):
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        iso = dt.isocalendar()
        return iso.year * 53 + iso.week
    if tf in ("M", "1M"):
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        return dt.year * 12 + dt.month
    # Generic intraday anchor like "60" minutes etc. — bucket by span.
    span_min = _parse_minutes(tf)
    if span_min is None:
        # Unknown anchor: default to daily so we never crash.
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        return dt.toordinal()
    return ts_ms // (span_min * 60_000)


def _parse_minutes(tf: str) -> int | None:
    """Parse a numeric Pine resolution string ("60", "240") into minutes."""
    try:
        return int(tf)
    except ValueError:
        return None


def session_offsets(bar_timestamps: Sequence[int], anchor_timeframe: str = "D") -> list[int]:
    """Return the intraday offset k for each bar (0 at each session's first bar).

    k resets to 0 whenever the session bucket changes (Pine's
    `timeframe.change(anchorTimeframe)`). Exposed for tests / verification.
    """
    offsets: list[int] = []
    prev_bucket: int | None = None
    k = 0
    for ts in bar_timestamps:
        bucket = _day_index(int(ts), anchor_timeframe)
        if prev_bucket is None or bucket != prev_bucket:
            k = 0
        else:
            k += 1
        offsets.append(k)
        prev_bucket = bucket
    return offsets


def _cumulative_since_anchor(
    volume: Sequence[float], buckets: Sequence[int]
) -> list[float]:
    """Running sum of volume since the most recent anchor reset (per bucket)."""
    cum: list[float] = []
    running = 0.0
    prev_bucket: int | None = None
    for v, b in zip(volume, buckets):
        if prev_bucket is None or b != prev_bucket:
            running = 0.0
        running += float(v)
        cum.append(running)
        prev_bucket = b
    return cum


def relative_volume(
    volume: Sequence[float],
    length: int,
    *,
    anchor_timeframe: str = "D",
    is_cumulative: bool = True,
    bar_timestamps: Sequence[int],
) -> RelativeVolumeResult:
    """Port of Pine `tv_ta.relativeVolume(length, anchorTimeframe, isCumulative, adjustRealtime)`.

    Parameters
    ----------
    volume : sequence of float, OLDEST-FIRST (chronological), one per bar.
    length : number of prior SESSIONS to average the at-time value over.
    anchor_timeframe : Pine anchor TF. "D" (default) = daily session reset.
    is_cumulative : True (suite default) → currVol/pastVol use cumulative-since-anchor
                    volume; False → raw per-bar volume.
    bar_timestamps : sequence of int epoch-millis, OLDEST-FIRST, aligned with `volume`.
                     Required — the at-time algorithm cannot be computed without
                     knowing each bar's session and intraday offset.

    Returns
    -------
    RelativeVolumeResult with curr_vol / past_vol / vol_ratio lists aligned 1:1
    with the input. Entries are None where history is insufficient (Pine na) or
    where pastVol would be 0 (avoids div-by-zero; Pine would yield na/inf).

    Notes
    -----
    * adjustRealtime is intentionally ignored: we score CLOSED bars only.
    * Determinism: same inputs → same outputs, every run.
    """
    if length < 1:
        raise ValueError(f"length must be >= 1, got {length}")
    if len(volume) != len(bar_timestamps):
        raise ValueError(
            f"volume ({len(volume)}) and bar_timestamps ({len(bar_timestamps)}) "
            "must be the same length"
        )

    n = len(volume)
    buckets = [_day_index(int(ts), anchor_timeframe) for ts in bar_timestamps]
    offsets = session_offsets(bar_timestamps, anchor_timeframe)

    base_series: list[float] = (
        _cumulative_since_anchor(volume, buckets)
        if is_cumulative
        else [float(v) for v in volume]
    )

    # Build, per (session bucket, intraday offset k), the base value at that cell.
    # We walk forward; for bar t we need the SAME-offset value in each of the
    # previous `length` DISTINCT sessions.
    #
    # Index: for each k, an ordered list of (bucket, base_value) as sessions appear.
    by_offset: dict[int, list[tuple[int, float]]] = {}

    curr_vol: list[float | None] = [None] * n
    past_vol: list[float | None] = [None] * n
    vol_ratio: list[float | None] = [None] * n

    for i in range(n):
        k = offsets[i]
        b = buckets[i]
        cur = base_series[i]
        curr_vol[i] = cur

        prior = by_offset.get(k, [])
        # Prior sessions (distinct buckets) that had a bar at this same offset k,
        # most recent `length` of them, excluding the current session bucket.
        prior_vals = [val for (bk, val) in prior if bk != b]
        if len(prior_vals) >= length:
            window = prior_vals[-length:]
            avg = sum(window) / length
            past_vol[i] = avg
            vol_ratio[i] = (cur / avg) if avg != 0.0 else None
        # else: insufficient history → leave None (Pine na)

        # Record this bar's cell AFTER computing, so it never averages itself.
        # Only the FIRST bar at a given (bucket, k) defines the cell (offsets are
        # unique per session by construction, so this is one append per session).
        if not prior or prior[-1][0] != b:
            by_offset.setdefault(k, []).append((b, cur))
        else:
            # Same bucket already recorded at this k (shouldn't happen since k is
            # unique within a session) — overwrite defensively.
            by_offset[k][-1] = (b, cur)

    return RelativeVolumeResult(curr_vol=curr_vol, past_vol=past_vol, vol_ratio=vol_ratio)


def relative_volume_at_bar0(
    bars,
    length: int,
    *,
    anchor_timeframe: str = "D",
    is_cumulative: bool = True,
) -> tuple[float | None, float | None, float | None]:
    """Bars-buffer adapter: relativeVolume for the CURRENT bar (Pine bar[0]).

    Mirrors how a Pine study reads `tv_ta.relativeVolume(...)` on the confirmed
    bar. `bars` is an rti.bars.Bars instance (bars[0] newest). Internally we
    rebuild oldest-first volume + timestamp series from the ring buffer and run
    the canonical algorithm.

    This is the ONLY sanctioned replacement for the old, wrong
    `volume / ta.sma(volume, N)` approximation. Returns (currVol, pastVol,
    volRatio) for bar[0]; volRatio is None when history is insufficient (Pine na).
    """
    n = len(bars)
    if n == 0:
        return None, None, None
    # bars[i] is i bars back; build oldest-first.
    vols = [bars[i].volume for i in range(n - 1, -1, -1)]
    tss = [bars[i].ts for i in range(n - 1, -1, -1)]
    return relative_volume_last(
        vols,
        length,
        anchor_timeframe=anchor_timeframe,
        is_cumulative=is_cumulative,
        bar_timestamps=tss,
    )


def relative_volume_last(
    volume: Sequence[float],
    length: int,
    *,
    anchor_timeframe: str = "D",
    is_cumulative: bool = True,
    bar_timestamps: Sequence[int],
) -> tuple[float | None, float | None, float | None]:
    """Convenience: return only the (currVol, pastVol, volRatio) for the LAST
    (most recent, closed) bar — the value a Pine study reads at bar[0]."""
    res = relative_volume(
        volume,
        length,
        anchor_timeframe=anchor_timeframe,
        is_cumulative=is_cumulative,
        bar_timestamps=bar_timestamps,
    )
    return res.curr_vol[-1], res.past_vol[-1], res.vol_ratio[-1]
