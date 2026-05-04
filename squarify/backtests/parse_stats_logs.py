#!/usr/bin/env python3
"""Parse SQUARIFY v2 STATS log emissions and compute per-detection performance.

Input: a directory of dumps (one file per ticker x timeframe pair) produced
       by feeding pine_get_console output through a basic flattener. Each line
       in each dump that starts with "SQS_STAT|" is a stats record.

Output: CSV (stdout or --out) with one row per (detection, forward_window,
        return_threshold) combination. Columns include PPV / NPV / sensitivity
        / specificity / sample size, matching Covenant Cmd XV thresholds.

Usage:
    parse_stats_logs.py <log_dir> [--out stats.csv]
                                  [--ret-thresholds 0.5,1.0,2.0,5.0]
                                  [--fwd-windows 5,10,20,40]
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# 46 SQUARIFY v2 detection field names, in the order they're emitted by STATS
DETECTION_FIELDS = [
    "F1_SDUPER", "F2_SUPER", "F3_HW", "F4_FLOOR", "F5_2F",
    "F6_UUUU", "F7_UUU", "F8_UU", "F9_ASTAR", "F10_OMEGA",
    "F11_FOX", "F12_OD", "F13_GOLF", "F14_PBJ_F2E3", "F15_PBJ_CL",
    "F16_F2CL_E3", "F17_E3_2of3PUP", "F18_F2_B2BD", "F19_E3_B2BD",
    "F20_F2E3SEQ", "F21_CL_B2BD", "F22_NPMPLUS", "F23_NPM12", "F24_NPM3",
    "F25_B2BNPM", "F26_NPMTNT", "F27_CO", "F28_HVDPBJ", "F29_B2BHVDPBJ",
    "F30_B2BHVD", "F31_UUUC", "F32_GRAIL", "F33_FLRNPM", "F34_NPMPBJPUP",
    "F35_NAGPLUS", "F36_UUHVD", "F37_UUNPM", "F38_FLRUU", "F39_FOSPUPRVOL",
    "F40_NPMUC", "F41_WBUSHBULL", "F42_WBUSHBEAR", "F43_WBUSHNEUTRAL",
    "F44_NPMUCPBJ", "F45_UCNAGBULL", "F46_UCNAGBEAR",
]

CONTINUOUS_FIELDS = [
    "CLOSE", "VOL", "VOLRANK", "VOLRATIO20", "RSI14", "RSI3",
    "DISPSTD_MULT", "RVOL_MULT", "NAG_RATIO",
    "GAP_PCT", "FB_BODY_PCT", "FB_RANGE_PCT", "FB_BODY_DIR",
    "GAP_BODY_RATIO", "GAP_RANGE_RATIO", "BODY_RANGE_PCT",
    "FWD5", "FWD10", "FWD20", "FWD40",
]

META_FIELDS = ["TF", "TICKER", "BAR", "TIME", "SESSBAR"]


@dataclass
class Record:
    meta: dict[str, str]
    cont: dict[str, float]
    fires: dict[str, bool]


def parse_line(line: str) -> Record | None:
    line = line.strip()
    if not line.startswith("SQS_STAT|"):
        return None
    parts = line.split("|")
    if parts[0] != "SQS_STAT":
        return None
    fields = {}
    for p in parts[1:]:
        if "=" not in p:
            continue
        k, _, v = p.partition("=")
        fields[k] = v
    meta = {k: fields.get(k, "") for k in META_FIELDS}
    cont = {}
    for k in CONTINUOUS_FIELDS:
        v = fields.get(k, "")
        try:
            cont[k] = float(v) if v != "" else float("nan")
        except ValueError:
            cont[k] = float("nan")
    fires = {k: fields.get(k, "0") == "1" for k in DETECTION_FIELDS}
    return Record(meta=meta, cont=cont, fires=fires)


def iter_records(log_dir: Path) -> Iterable[Record]:
    for fp in sorted(log_dir.rglob("*")):
        if not fp.is_file():
            continue
        try:
            text = fp.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            rec = parse_line(line)
            if rec is not None:
                yield rec


def compute_stats(
    records: list[Record],
    fwd_windows: list[int],
    ret_thresholds: list[float],
) -> list[dict[str, str | float | int]]:
    """Compute PPV/NPV/sensitivity/specificity per (detection, fwd, threshold)."""
    out: list[dict[str, str | float | int]] = []
    # Group records by (TICKER, TF) so forward returns line up
    grouped: dict[tuple[str, str], list[Record]] = defaultdict(list)
    for r in records:
        grouped[(r.meta["TICKER"], r.meta["TF"])].append(r)

    for det in DETECTION_FIELDS:
        for fwd in fwd_windows:
            fwd_key = f"FWD{fwd}"
            for ret_thresh in ret_thresholds:
                # Build 2x2 contingency: signal {fired,not} x outcome {success,fail}
                # Outcome success = forward return >= ret_thresh
                tp = fp = tn = fn = 0
                for _, recs in grouped.items():
                    for r in recs:
                        ret_val = r.cont.get(fwd_key, float("nan"))
                        if ret_val != ret_val:  # NaN
                            continue
                        success = ret_val >= ret_thresh
                        fired = r.fires.get(det, False)
                        if fired and success:
                            tp += 1
                        elif fired and not success:
                            fp += 1
                        elif not fired and success:
                            fn += 1
                        else:
                            tn += 1
                pos = tp + fp
                neg = tn + fn
                actual_pos = tp + fn
                actual_neg = tn + fp
                ppv = (tp / pos) if pos > 0 else float("nan")
                npv = (tn / neg) if neg > 0 else float("nan")
                sens = (tp / actual_pos) if actual_pos > 0 else float("nan")
                spec = (tn / actual_neg) if actual_neg > 0 else float("nan")
                base_rate = (actual_pos / (actual_pos + actual_neg)) if (actual_pos + actual_neg) > 0 else float("nan")
                lift = (ppv / base_rate) if (base_rate == base_rate and base_rate > 0) else float("nan")
                out.append({
                    "detection": det,
                    "fwd_bars": fwd,
                    "return_threshold_pct": ret_thresh,
                    "n_fires": pos,
                    "n_total": pos + neg,
                    "TP": tp, "FP": fp, "TN": tn, "FN": fn,
                    "PPV": ppv, "NPV": npv,
                    "sensitivity": sens, "specificity": spec,
                    "base_rate": base_rate, "lift": lift,
                })
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("log_dir", type=Path, help="Directory of pine_get_console dumps")
    ap.add_argument("--out", type=Path, default=None, help="Output CSV path (default stdout)")
    ap.add_argument("--ret-thresholds", default="0.5,1.0,2.0,5.0",
                    help="Comma-separated forward-return thresholds (percent gain)")
    ap.add_argument("--fwd-windows", default="5,10,20,40",
                    help="Comma-separated forward-bar windows")
    args = ap.parse_args(argv[1:])

    fwd_windows = [int(x) for x in args.fwd_windows.split(",")]
    ret_thresholds = [float(x) for x in args.ret_thresholds.split(",")]

    records = list(iter_records(args.log_dir))
    if not records:
        print(f"No SQS_STAT records found in {args.log_dir}", file=sys.stderr)
        return 1
    print(f"Parsed {len(records)} records across "
          f"{len({(r.meta['TICKER'], r.meta['TF']) for r in records})} ticker-TF pairs",
          file=sys.stderr)

    rows = compute_stats(records, fwd_windows, ret_thresholds)
    rows.sort(key=lambda r: (-(r["PPV"] if r["PPV"] == r["PPV"] else 0), r["detection"]))

    fieldnames = [
        "detection", "fwd_bars", "return_threshold_pct",
        "n_fires", "n_total", "TP", "FP", "TN", "FN",
        "PPV", "NPV", "sensitivity", "specificity", "base_rate", "lift",
    ]
    out_handle = args.out.open("w", newline="") if args.out else sys.stdout
    writer = csv.DictWriter(out_handle, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    if args.out:
        out_handle.close()
        print(f"Wrote {len(rows)} rows to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
