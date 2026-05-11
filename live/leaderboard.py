"""In-memory leaderboard state — per-symbol fire counts in a rolling window."""
from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Deque, Dict, List, Optional


class Leaderboard:
    def __init__(self, window_minutes: int = 5, weights: Optional[Dict[str, float]] = None):
        self.window = timedelta(minutes=window_minutes)
        self.weights = weights or {}
        self._fires: Dict[tuple, Deque[datetime]] = {}
        self._price: Dict[str, float] = {}
        self._last_bar: Dict[str, datetime] = {}

    def record_bar(self, symbol: str, close_price: float, close_time: datetime) -> None:
        self._price[symbol] = close_price
        self._last_bar[symbol] = close_time

    def record_fire(self, symbol: str, plot: str, ts: datetime) -> None:
        dq = self._fires.setdefault((symbol, plot), deque())
        dq.append(ts)

    def _prune(self, now: datetime) -> None:
        cutoff = now - self.window
        for dq in self._fires.values():
            while dq and dq[0] < cutoff:
                dq.popleft()

    def snapshot(self, plots: List[str], now: Optional[datetime] = None) -> List[dict]:
        now = now or datetime.now(timezone.utc)
        self._prune(now)
        symbols = sorted(self._price.keys())
        rows: List[dict] = []
        for s in symbols:
            counts = {p: len(self._fires.get((s, p), [])) for p in plots}
            score = sum(self.weights.get(p, 1.0) * counts[p] for p in plots)
            rows.append({
                "symbol": s,
                "price": self._price.get(s),
                "last_bar": self._last_bar.get(s).isoformat() if self._last_bar.get(s) else None,
                "fires": counts,
                "score": round(score, 2),
            })
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows
