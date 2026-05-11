"""Massive.com WebSocket adapter — stub for the 9:30 AM ET equity switchover.

Run this on a machine where MASSIVE_API_KEY is set. The exact WebSocket URL
and message schema depend on Anish's Massive.com subscription tier; fill in
the TODOs from the Massive docs when wiring it up. The output shape (bar
dict) MUST match adapters.binance_ws.stream_bars so the server can swap
adapters without touching downstream code.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import AsyncIterator, Iterable

import websockets

LOG = logging.getLogger("adapters.massive_ws")

# TODO(anish): confirm the exact Massive.com WS endpoint for 1m aggregate bars.
# Per Anish 2026-05-11 the subscription is the Polygon-equivalent tier; the
# corresponding Polygon WS path is wss://socket.polygon.io/stocks for stocks
# 1m aggregates (event A.<TICKER>). Massive.com likely mirrors that schema.
MASSIVE_WS_URL = os.environ.get(
    "MASSIVE_WS_URL",
    "wss://socket.polygon.io/stocks",
)


async def stream_bars(symbols: Iterable[str], interval: str = "1m") -> AsyncIterator[dict]:
    """Stream 1m closed bars from Massive.com for the given equity tickers."""
    api_key = os.environ.get("MASSIVE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MASSIVE_API_KEY env var is required for the Massive adapter. "
            "Run this from a machine where the Massive.com key is set."
        )
    symbols = [s.upper() for s in symbols]
    sub_topics = ",".join(f"A.{s}" for s in symbols)  # 1m aggregate bar topic

    backoff = 1.0
    while True:
        try:
            async with websockets.connect(MASSIVE_WS_URL, ping_interval=30) as ws:
                await ws.send(json.dumps({"action": "auth", "params": api_key}))
                await ws.recv()
                await ws.send(json.dumps({"action": "subscribe", "params": sub_topics}))
                LOG.info("connected to massive ws: %d symbols", len(symbols))
                backoff = 1.0
                async for raw in ws:
                    for evt in json.loads(raw):
                        if evt.get("ev") != "A":
                            continue
                        yield {
                            "symbol": evt["sym"],
                            "open_time": datetime.fromtimestamp(evt["s"] / 1000, tz=timezone.utc),
                            "close_time": datetime.fromtimestamp(evt["e"] / 1000, tz=timezone.utc),
                            "open": float(evt["o"]),
                            "high": float(evt["h"]),
                            "low": float(evt["l"]),
                            "close": float(evt["c"]),
                            "volume": float(evt["v"]),
                        }
        except Exception as exc:
            LOG.warning("massive ws disconnected (%s); retry in %.1fs", exc, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30.0)
