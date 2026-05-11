"""Rolling OHLCV state per symbol — fixed-size deque + DataFrame view."""
from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

import pandas as pd


class BarState:
    """Append-only rolling OHLCV buffer keyed by symbol."""

    def __init__(self, window: int = 200):
        self.window = window
        self._buf: Dict[str, Deque[dict]] = {}

    def append(self, bar: dict) -> None:
        buf = self._buf.setdefault(bar["symbol"], deque(maxlen=self.window))
        buf.append(bar)

    def frame(self, symbol: str) -> pd.DataFrame:
        rows = list(self._buf.get(symbol, []))
        if not rows:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        df = pd.DataFrame(rows)
        df.index = pd.to_datetime([r["open_time"] for r in rows], utc=True)
        return df[["open", "high", "low", "close", "volume"]]

    def symbols(self) -> List[str]:
        return list(self._buf.keys())

    def __len__(self) -> int:
        return sum(len(d) for d in self._buf.values())
