# HUB_1020_1153am v20260604 Three-Output Manifest

Pine is a Pine Editor tick-friendly
Python is a Python tick
Python is a Python time-based

## Source

- Indicator: `HUB_1020_1153am`
- Shorttitle: `Hub102011a`
- Pine version: `5`
- Active source path: `/Users/anishpatel/code/anish/indicators/hub-1020-1153am/versions/HUB_1020_1153am_Hub102011a_v20260604.pine`
- Import source path: `/Users/anishpatel/code/anish/indicators/imports/20260531T103840_indicator_studies/pine_v5/hub_1020_1153am_shorttitle_hub102011a.pine`
- Source SHA-256: `719a3f240df431aa59f3d07a148085a3bd0e9aebedea824439f89e138459f2e9`

## Requested Behavior Captured

- Custom Signal A default: `FC Overlap`, window `3`, required `2`.
- Custom Signal B default: `FC 2/3 Fauna`, window `2`, required `2`.
- Custom Signal C default: `FC Cluster`, window `12`, required `2`.
- Custom Signal D default: `FC Overlap` + `Red Plus`, window `1`, required `2`.
- Custom Signal E default: `RVOL Window`, window `7`, required `1`.
- Custom Signal F default: `Fauna X-in-Y` + `PB&J Follow-up Buy`, window `4`, required `2`.
- Custom Signal G default: `Custom Signal D`, window `3`, required `2`.
- Custom Signal H default: `FC Overlap`, window `3`, required `7`.
- Custom Signal I default: `FC 2/3 Fauna`, window `2`, required `2`.
- Custom Signal J default: `FC Cluster` + `E3` + `First Two MB` + `PB&J Follow-up Buy`, window `3`, required `4`.
- `Swing Bottom (Mango)` remains a visual plot/label and is removed from alerts.
- `MB Individual`, `RE Individual`, and `TA Individual` remain calculated internally but are removed from standalone plot and alert output.

## Outputs

- Pine tick-friendly: `/Users/anishpatel/code/anish/indicators/hub-1020-1153am/tick_friendly/HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine`
- Pine tick-friendly SHA-256: `a501fe519759ff6bf5acc56aa50190cf6fc38e361a270f5fee4b4ee9d9464ecb`
- Python tick: `/Users/anishpatel/code/anish/realtime-indicators/rti/signals_tick/hub_1020_1153am.py`
- Python tick SHA-256: `2c8c5b4e10d20eab94fa11e0e24b5f0370f0ebf856ef5870d405a015363a1903`
- Python time-based: `/Users/anishpatel/code/anish/realtime-indicators/rti/signals_time/hub_1020_1153am.py`
- Python time-based SHA-256: `a626dbc448cc5802babc51f69e91118f6c0b266816b802c10a24afd3b3ffeb5c`
- Shared Python core: `/Users/anishpatel/code/anish/realtime-indicators/rti/signals/hub_1020_1153am.py`
- Shared Python core SHA-256: `5cdc298086ae2c225261af1eb2dc0391ac6d267598169b14226d3120391a41df`

## Unsupported / Guarded Constructs

- TradingView session helpers remain Pine-native in Pine output.
- Python time-based runtime uses confirmed OHLCV bars and explicit RTH timezone params.
- Python tick runtime does not assume fixed bar duration; RTH counters use bar timestamps.
- TradingView parity is not claimed here. Trust state remains `verifying`.
