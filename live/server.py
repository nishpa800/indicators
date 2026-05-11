"""FastAPI + SSE server for the live leaderboard.

Run: `python -m live.server` (or `uvicorn live.server:app --host 0.0.0.0 --port 8080`)
Open: http://localhost:8080
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator, List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from live import bar_state, leaderboard as lb_mod, port_runner
from live.adapters import binance_ws, massive_ws

LOG = logging.getLogger("leaderboard")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def load_config(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {
        "feed": "binance",
        "symbols": ["BTCUSDT"],
        "window_minutes": 5,
        "weights": {"Bull RVOL 1x": 1.0, "Bear RVOL 1x": 1.0, "MOAB": 2.0},
    }


def pick_adapter(feed: str):
    feed = os.environ.get("LEADERBOARD_FEED", feed).lower()
    if feed == "massive":
        return massive_ws.stream_bars, "massive"
    return binance_ws.stream_bars, "binance"


class App:
    def __init__(self, config: dict):
        self.config = config
        self.symbols: List[str] = list(config["symbols"])
        self.bars = bar_state.BarState(window=200)
        self.lb = lb_mod.Leaderboard(
            window_minutes=int(config["window_minutes"]),
            weights=dict(config["weights"]),
        )
        self.fire_feed: list[dict] = []
        self.stream_fn, self.feed_name = pick_adapter(config.get("feed", "binance"))
        self._stop = asyncio.Event()

    async def ingest_loop(self) -> None:
        LOG.info("ingest start: feed=%s symbols=%s", self.feed_name, self.symbols)
        try:
            async for bar in self.stream_fn(self.symbols):
                if self._stop.is_set():
                    return
                self.bars.append(bar)
                self.lb.record_bar(bar["symbol"], bar["close"], bar["close_time"])
                df = self.bars.frame(bar["symbol"])
                fires = port_runner.run_smoke_test(df)
                for plot, fired in fires.items():
                    if fired:
                        self.lb.record_fire(bar["symbol"], plot, bar["close_time"])
                        self.fire_feed.append({
                            "symbol": bar["symbol"], "plot": plot,
                            "price": bar["close"], "time": bar["close_time"].isoformat(),
                        })
                        self.fire_feed = self.fire_feed[-20:]
                fired_only = {k: v for k, v in fires.items() if v}
                LOG.info("bar %s @ %s vol=%.2f fires=%s",
                         bar["symbol"], bar["close"], bar["volume"], fired_only or "{}")
        except Exception as exc:
            LOG.exception("ingest loop crashed: %s", exc)

    async def snapshot_stream(self) -> AsyncIterator[dict]:
        plots = list(port_runner.SMOKE_TEST_PLOTS)
        while not self._stop.is_set():
            payload = {
                "now": datetime.now(timezone.utc).isoformat(),
                "feed": self.feed_name,
                "symbols": self.symbols,
                "plots": plots,
                "rows": self.lb.snapshot(plots),
                "feed_recent": list(reversed(self.fire_feed)),
            }
            yield {"event": "snapshot", "data": json.dumps(payload)}
            await asyncio.sleep(1)


app = FastAPI(title="indicator-leaderboard")
state = App(load_config(CONFIG_PATH))


@app.on_event("startup")
async def _startup() -> None:
    asyncio.create_task(state.ingest_loop())


@app.get("/stream")
async def stream():
    return EventSourceResponse(state.snapshot_stream())


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
