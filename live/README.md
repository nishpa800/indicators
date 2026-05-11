# Live Leaderboard — Tomorrow's MVP (2026-05-11)

Real-time indicator leaderboard. Streams 1-minute closed bars from a public WebSocket source, runs Python ports of indicator detection plots on each bar, and ranks symbols by fire intensity in a rolling 5-minute window. Served as a browser dashboard via FastAPI + SSE.

## Quick start (BTC smoke test)

```
pip install -r live/requirements.txt
python -m live.server
# open http://localhost:8080
```

Default config streams Binance spot 1m for BTCUSDT, ETHUSDT, SOLUSDT.

## What plots fire

V1 smoke test uses heavy_pentagon's Pipeline-1 plots (pure OHLCV, no STUBBED upstream needed):

- **Bull RVOL 1x** — bullish price spike at 1× RVOL threshold
- **Bear RVOL 1x** — bearish price spike at 1× RVOL threshold
- **MOAB** — Mother Of All Bearish (the max-tier bearish RVOL setup)

Per `python_ports/heavy_pentagon/canonical.py` DETECTIONS registry. Pipeline-2 (Pentagon / WTC / Hiroshima) requires Pine's `tv_ta.relativeVolume` engine which we stub for now.

## Config

Edit `live/config.json`:

- `feed` — `"binance"` (default, free public WS) or `"massive"` (equity feed, requires `MASSIVE_API_KEY`)
- `symbols` — list of symbols (Binance spot pairs for crypto; tickers for equities)
- `window_minutes` — rolling window for fire counts (default 5)
- `weights` — per-plot weight in the score (default 1.0; MOAB gets 2.0 since it's the higher-conviction tier)

## 9:30 AM ET equity switchover

```
LEADERBOARD_FEED=massive MASSIVE_API_KEY=... python -m live.server
```

Edit `live/config.json` to swap `symbols` to the equity list (e.g. NVDA, TSLA, AMD, SMCI, PLTR, COIN, MSTR, META, AMZN, AAPL).

The Massive adapter at `live/adapters/massive_ws.py` is a stub written against the Polygon WS schema (since Massive.com is the Polygon-equivalent). Confirm the exact URL + auth flow from your Massive docs before going live; the message-decoding code is fully written and the bar shape matches the Binance adapter, so the server swaps adapters without code changes.

## Architecture

```
[adapter]──>[BarState]──>[port_runner]──>[Leaderboard]
 WS stream   rolling 200    runs DETECTIONS  fire counts in
             bars/symbol    on last bar      5m rolling window
                                                  │
                                                  ▼
                                          [FastAPI + SSE]──>[browser UI]
                                                              localhost:8080
```

In-memory only. Process restart wipes state. SQLite persistence is a Day-2 add.

## Files

- `adapters/binance_ws.py` — public BTC/ETH/SOL feed (no auth)
- `adapters/massive_ws.py` — Massive.com equity feed (stub; needs API key)
- `bar_state.py` — rolling OHLCV deque per symbol
- `port_runner.py` — runs heavy_pentagon DETECTIONS on each closed bar
- `leaderboard.py` — in-memory fire counts + score ranking
- `server.py` — FastAPI app + SSE endpoint
- `static/index.html` — single-page dashboard UI

## Related

See `docs/agentic-os/prompts/gps-satellite-handoff-prompt.html` section 20.5 for the broader architecture.
