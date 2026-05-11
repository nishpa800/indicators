"""Public Binance WebSocket adapter. No auth required.

Streams the @kline_<interval> feed and yields one bar per symbol per interval
when the bar closes (kline.x == True). Crypto symbols only.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import AsyncIterator, Iterable

import websockets

LOG = logging.getLogger("adapters.binance_ws")
BINANCE_WS_URL = "wss://stream.binance.com:9443/stream"


async def stream_bars(symbols: Iterable[str], interval: str = "1m") -> AsyncIterator[dict]:
    """Yield closed bars from Binance kline streams for the given symbols."""
    symbols = [s.lower() for s in symbols]
    streams = "/".join(f"{s}@kline_{interval}" for s in symbols)
    url = f"{BINANCE_WS_URL}?streams={streams}"
    backoff = 1.0
    while True:
        try:
            async with websockets.connect(url, ping_interval=30, ping_timeout=20) as ws:
                LOG.info("connected to binance ws: %d symbols, interval=%s", len(symbols), interval)
                backoff = 1.0
                async for raw in ws:
                    msg = json.loads(raw)
                    k = msg.get("data", {}).get("k")
                    if not k or not k.get("x"):
                        continue
                    yield {
                        "symbol": k["s"],
                        "open_time": datetime.fromtimestamp(k["t"] / 1000, tz=timezone.utc),
                        "close_time": datetime.fromtimestamp(k["T"] / 1000, tz=timezone.utc),
                        "open": float(k["o"]),
                        "high": float(k["h"]),
                        "low": float(k["l"]),
                        "close": float(k["c"]),
                        "volume": float(k["v"]),
                    }
        except Exception as exc:
            LOG.warning("ws disconnected (%s); retry in %.1fs", exc, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30.0)
