#!/usr/bin/env python3
"""
merge_extracts.py — combine bible-input/extract-*.yaml into data/indicators.yaml.

Reads every extract-<family>.yaml in bible-input/, normalises into a single
document, and writes data/indicators.yaml as the bible's source of truth.

Schema (data/indicators.yaml):
    schema_version: 1
    generated_at: "<ISO date>"
    operating_definitions: { ... }
    indicators: [ <indicator records> ]

Each indicator record carries its `indicator` metadata plus `roots`,
`composites`, `internal_helpers`, etc., as the agent emitted them.

Usage:  python3 tools/merge_extracts.py
"""

from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
EXTRACT_DIR = REPO / "bible-input"
OUT_YAML = REPO / "data" / "indicators.yaml"
OUT_JSON = REPO / "data" / "indicators.json"


OPERATING_DEFINITIONS = {
    "root": (
        "A NAMED, LEAST-COMMON-DENOMINATOR detection plot — the lowest-level "
        "named primitive humans refer to. The bible STOPS at this level. "
        "Internal mechanics (Supertrend, OKE engine, Zoo engine, EMA / SMA / "
        "WMA / VWMA, ATR multipliers, σ-multipliers, raw highest()/lowest() "
        "calls) are NOT roots."
    ),
    "composite": (
        "A detection plot whose composition uses ≥1 root or lower-tier "
        "composite by name."
    ),
    "tier": (
        "Depth from root. Root = 0. Composite-of-roots = 1. "
        "Composite-of-tier-1 = 2. ..."
    ),
    "lifecycle_stage": {
        "1": "Bar close & confirmation (`barstate.isconfirmed`).",
        "2": "Independent root calculation (decoupled, no cross-root "
              "ordering).",
        "3": "Per-root offset application.",
        "4": "Visual plot render.",
        "5": "Composite evaluation (reads post-offset boolean outputs only).",
        "6": "Composite offset & plot.",
        "7": "Alert firing (always at bar close, regardless of plot offset).",
    },
    "canonical_name": (
        "<provenance>::<name>. Provenance is the indicator study where this "
        "primitive is canonically defined."
    ),
    "non_roots": [
        "Supertrend", "OKE engine", "Zoo engine / Zoo MA",
        "EMA / SMA / WMA / VWMA crossings", "ATR thresholds",
        "σ-multipliers", "raw ta.highest()/ta.lowest() calls",
        "barstate.* flags", "request.security results",
        "raw FVG geometry primitives (when not exposed as a named root)",
    ],
}


def load_extract(path: Path) -> dict:
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        sys.stderr.write(f"WARNING: {path.name} did not parse as a mapping\n")
        return {}
    return data


def merge() -> dict:
    extracts = sorted(EXTRACT_DIR.glob("extract-*.yaml"))
    indicators = []
    flat_roots = []
    flat_composites = []
    skipped: list[Path] = []
    for extract_path in extracts:
        data = load_extract(extract_path)
        if not data:
            # Empty / unparseable / unexpected-shape extract. The bible's source
            # of truth must not silently drop indicators — accumulate and fail
            # at the end so all skips are visible at once.
            skipped.append(extract_path)
            continue
        # Normalise: each extract has top-level `indicator`, `roots`,
        # `composites`, etc. Combine them into one indicator record.
        record = {}
        meta = data.get("indicator") or {}
        record.update(meta)
        record["_extract_file"] = str(extract_path.relative_to(REPO))
        ind_id = record.get("id", extract_path.stem.replace("extract-", ""))
        for key in (
            "internal_helpers", "roots", "composites",
            "phantom_toggles", "fauna_decomposition",
            "cross_indicator_dependencies", "architecture_layers",
            "uncertain_or_questions",
        ):
            if key in data:
                record[key] = data[key]
        # Normalise individual roots/composites: tag with in_indicator,
        # mirror `offset` → `plot_offset` for downstream tool compatibility,
        # default lifecycle_stage if missing.
        for r in record.get("roots") or []:
            if isinstance(r, dict):
                r.setdefault("in_indicator", ind_id)
                if "offset" in r and "plot_offset" not in r:
                    r["plot_offset"] = r["offset"]
                r.setdefault("lifecycle_stage", 2)
                flat_roots.append(r)
        for c in record.get("composites") or []:
            if isinstance(c, dict):
                c.setdefault("in_indicator", ind_id)
                if "offset" in c and "plot_offset" not in c:
                    c["plot_offset"] = c["offset"]
                c.setdefault("lifecycle_stage", 5)
                flat_composites.append(c)
        indicators.append(record)
    if skipped:
        names = ", ".join(p.name for p in skipped)
        sys.stderr.write(
            f"ERROR: {len(skipped)} extract(s) were unparseable or empty and were skipped: "
            f"{names}\n"
            "Refusing to write a partial bible. Fix the extract(s) and re-run.\n"
        )
        sys.exit(2)
    return {
        "schema_version": 1,
        "generated_at": _dt.date.today().isoformat(),
        "generated_by": "tools/merge_extracts.py from bible-input/extract-*.yaml",
        "operating_definitions": OPERATING_DEFINITIONS,
        "indicators": indicators,
        # Denormalised flat views — used by tools/build_lineage_cards.py and
        # docs/{roots,composites}.md generators. Source of truth remains
        # the per-indicator nesting in `indicators[]`.
        "roots": flat_roots,
        "composites": flat_composites,
    }


def main() -> int:
    merged = merge()
    OUT_YAML.parent.mkdir(parents=True, exist_ok=True)
    with OUT_YAML.open("w") as f:
        yaml.safe_dump(merged, f, sort_keys=False, allow_unicode=True,
                       default_flow_style=False, width=120)
    with OUT_JSON.open("w") as f:
        json.dump(merged, f, indent=2, sort_keys=False)
    # Verify equality
    yaml_loaded = yaml.safe_load(OUT_YAML.read_text())
    json_loaded = json.loads(OUT_JSON.read_text())
    assert yaml_loaded == json_loaded, "YAML and JSON do not match!"
    n_ind = len(merged["indicators"])
    n_roots = sum(len(i.get("roots") or []) for i in merged["indicators"])
    n_comps = sum(len(i.get("composites") or []) for i in merged["indicators"])
    print(f"Wrote {OUT_YAML.relative_to(REPO)} and {OUT_JSON.relative_to(REPO)}")
    print(f"  Indicators: {n_ind}")
    print(f"  Total roots: {n_roots}")
    print(f"  Total composites: {n_comps}")
    print(f"  YAML == JSON: True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
