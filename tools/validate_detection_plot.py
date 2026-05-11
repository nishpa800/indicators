#!/usr/bin/env python3
"""
validate_detection_plot.py — deterministic Phase 1 ENUMERATE harness for the
detection-plot-validation skill.

Runs the canonical grep + classification deterministically so two different
Claude agents running Phase 1 on the same target produce byte-identical
enumeration tables.

Usage:
    python3 tools/validate_detection_plot.py --target=<canonical-name> [--aliases=A,B,C]

Outputs (to stdout, also written to a file under bible-input/validation/):
    A YAML enumeration record that conforms to templates/enumeration-table.md.

This script is read-only. It NEVER modifies any file. It's a deterministic
oracle for Phase 1 that the skill's parent agent can shell out to instead of
dispatching subagents — saving tokens AND guaranteeing reproducibility.

Phase 2 (static-diff), Phase 3 (TV-firing), Phase 4 (reconcile) are NOT done
here. They require Claude's judgment + MCP access + user approval.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent

# Patterns from references/pine-grep-patterns.md. Compiled once for speed.
PATTERN_DEFINITION = re.compile(
    r"(^|\s)(var\s+)?(bool|float|int|string|color|line|label|box|table|polyline)?\s*"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*(:=|=)\s*",
    re.IGNORECASE,
)
PATTERN_INPUT = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*input\.(bool|int|float|string|source|color|"
    r"timeframe|symbol|session|price|time|enum|text_area)\s*\(",
    re.IGNORECASE,
)
PATTERN_PLOT = re.compile(
    r"(plot(shape|char|bar|candle|arrow|zigzag)?|bgcolor|barcolor|fill)\s*\(",
    re.IGNORECASE,
)
PATTERN_ALERT = re.compile(r"alert(condition)?\s*\(", re.IGNORECASE)
PATTERN_COMMENT_PREFIX = re.compile(r"^\s*//")


def find_pine_files() -> list[Path]:
    """Every canonical .pine file in <indicator>/versions/ — excludes legacy and backtests."""
    pine_files = []
    for ind_dir in REPO.iterdir():
        if not ind_dir.is_dir() or ind_dir.name.startswith("."):
            continue
        versions_dir = ind_dir / "versions"
        if versions_dir.is_dir():
            pine_files.extend(sorted(versions_dir.glob("*.pine")))
    # Also include path-a-loggers and test-indicators
    for special in ("path-a-loggers", "test-indicators"):
        sp = REPO / special / "versions"
        if sp.is_dir():
            pine_files.extend(sorted(sp.glob("*.pine")))
    return pine_files


def indicator_family_of(pine_file: Path) -> str:
    """Infer the indicator family from the file's parent dir name."""
    return pine_file.parent.parent.name


def classify_line(line: str, alias: str) -> str:
    """Classify a single Pine line into one of the six classes."""
    if PATTERN_COMMENT_PREFIX.match(line):
        return "COMMENT"
    if PATTERN_PLOT.search(line):
        return "PLOT"
    if PATTERN_ALERT.search(line):
        return "ALERT"
    # INPUT: alias = input.*(...) — must check before DEFINITION
    input_match = PATTERN_INPUT.search(line)
    if input_match and input_match.group(1).lower() == alias.lower():
        return "INPUT"
    # DEFINITION: <type?> alias = <expr> OR alias := <expr>
    # Quick check: does the alias appear on the LHS of = or :=?
    # Pragmatic: split on '=' first occurrence and see if alias is in the LHS.
    if "=" in line:
        lhs, _, _ = line.partition("=")
        # Handle :=
        if lhs.endswith(":"):
            lhs = lhs[:-1]
        # Strip type keywords
        lhs_tokens = lhs.strip().split()
        if lhs_tokens and lhs_tokens[-1].lower() == alias.lower():
            return "DEFINITION"
    # Else: REFERENCE
    return "REFERENCE"


def enumerate_occurrences(
    pine_files: list[Path], aliases: list[str]
) -> dict[str, list[dict]]:
    """For every alias, find every occurrence across every Pine file."""
    per_file: dict[str, list[dict]] = {}
    alias_lower = [a.lower() for a in aliases]
    alias_re = re.compile(r"\b(" + "|".join(re.escape(a) for a in aliases) + r")\b")
    for pine_file in pine_files:
        try:
            content = pine_file.read_text()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        occurrences = []
        for line_no, line in enumerate(content.splitlines(), start=1):
            matches = alias_re.findall(line)
            if not matches:
                continue
            for match in matches:
                classification = classify_line(line, match)
                occurrences.append({
                    "line": line_no,
                    "alias_matched": match,
                    "classification": classification,
                    "raw_line": line.rstrip(),
                })
        if occurrences:
            per_file[str(pine_file.relative_to(REPO))] = occurrences
    return per_file


def summarize(
    per_file: dict[str, list[dict]],
) -> tuple[list[dict], dict[str, dict[str, int]]]:
    """
    Returns:
      - DEFINITIONs list (every DEFINITION across files; rows for the parent skill)
      - counts table: per-indicator-family, per-classification counts
    """
    definitions = []
    counts: dict[str, dict[str, int]] = {}
    for path_str, occs in per_file.items():
        path = REPO / path_str
        family = indicator_family_of(path)
        counts.setdefault(
            family,
            {k: 0 for k in ("DEFINITION", "REFERENCE", "INPUT", "PLOT", "ALERT", "COMMENT")},
        )
        for occ in occs:
            cls = occ["classification"]
            counts[family][cls] = counts[family].get(cls, 0) + 1
            if cls == "DEFINITION":
                definitions.append({
                    "indicator_family": family,
                    "file": path_str,
                    "line": occ["line"],
                    "pine_variable": occ["alias_matched"],
                    "raw_line": occ["raw_line"],
                })
    return definitions, counts


def cross_check_yaml(target: str, aliases: list[str], definitions: list[dict]) -> dict:
    """Compare DEFINITIONs against data/indicators.yaml — orphans + missings."""
    try:
        import yaml
    except ImportError:
        return {"_skipped": "pyyaml not installed; install with `pip install pyyaml`"}
    yaml_path = REPO / "data" / "indicators.yaml"
    if not yaml_path.exists():
        return {"_skipped": "data/indicators.yaml not found; run tools/merge_extracts.py first"}
    with yaml_path.open() as f:
        data = yaml.safe_load(f) or {}
    # Walk the flat roots + composites arrays
    flat_records = (data.get("roots") or []) + (data.get("composites") or [])
    # Match records whose id matches target or aliases (case-insensitive)
    alias_lower = {a.lower() for a in aliases}
    yaml_matching = []
    for rec in flat_records:
        rec_id = rec.get("id", "")
        # The id is like "<provenance>::<NAME>" — extract the NAME
        name = rec_id.split("::", 1)[-1] if "::" in rec_id else rec_id
        if name.lower() in alias_lower or target.lower() == name.lower():
            yaml_matching.append({
                "id": rec_id,
                "indicator": rec.get("in_indicator"),
                "pine_source_line_range": rec.get("pine_source_line_range"),
            })
    # Orphans: YAML records with no Pine DEFINITION match
    pine_lines_per_indicator: dict[str, set[int]] = {}
    for d in definitions:
        pine_lines_per_indicator.setdefault(d["indicator_family"], set()).add(d["line"])
    orphans = []
    for ym in yaml_matching:
        ind = ym["indicator"]
        line_range = ym.get("pine_source_line_range") or ""
        # Parse "L78-L82" or "L78"
        line_nums = [int(s.strip("L")) for s in re.findall(r"L\d+", line_range)]
        if not line_nums:
            orphans.append({**ym, "reason": "no line range in YAML"})
            continue
        # Check if any Pine DEFINITION line in this indicator is within ±5 of any YAML line
        pine_lines = pine_lines_per_indicator.get(ind, set())
        if not pine_lines:
            orphans.append({**ym, "reason": f"no Pine DEFINITION in {ind}"})
            continue
        matched = False
        for yl in line_nums:
            if any(abs(pl - yl) <= 5 for pl in pine_lines):
                matched = True
                break
        if not matched:
            orphans.append({**ym, "reason": f"line range {line_range} doesn't match any Pine line ±5 in {ind}"})
    # Missings: Pine DEFINITIONs with no YAML match
    yaml_indicators = {ym["indicator"] for ym in yaml_matching}
    missings = [
        d for d in definitions
        if d["indicator_family"] not in yaml_indicators
    ]
    return {
        "yaml_matching_records": yaml_matching,
        "orphans": orphans,
        "missings": missings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("--target", required=True, help="canonical detection-plot name (e.g. UNIFIED_COMBO_BULL)")
    parser.add_argument(
        "--aliases",
        default="",
        help="comma-separated additional aliases (e.g. csNew3_Bull,unified_combo,UC)",
    )
    parser.add_argument(
        "--format",
        choices=("yaml", "json"),
        default="yaml",
        help="output format",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="output file path (default: stdout only)",
    )
    args = parser.parse_args()

    aliases = [args.target]
    if args.aliases:
        aliases.extend(a.strip() for a in args.aliases.split(",") if a.strip())

    pine_files = find_pine_files()
    per_file = enumerate_occurrences(pine_files, aliases)
    definitions, counts = summarize(per_file)
    yaml_check = cross_check_yaml(args.target, aliases, definitions)

    output = {
        "skill_phase": "1-ENUMERATE",
        "skill_version": "detection-plot-validation@v1.0.0",
        "target": args.target,
        "aliases_searched": aliases,
        "pine_files_scanned": len(pine_files),
        "definitions": definitions,
        "occurrences_per_indicator": counts,
        "yaml_cross_check": yaml_check,
        "status": "COMPLETE",
    }

    if args.format == "yaml":
        try:
            import yaml
            serialized = yaml.safe_dump(output, sort_keys=False, allow_unicode=True, default_flow_style=False, width=120)
        except ImportError:
            sys.stderr.write("pyyaml not installed; falling back to JSON\n")
            serialized = json.dumps(output, indent=2)
    else:
        serialized = json.dumps(output, indent=2)

    sys.stdout.write(serialized)
    if args.out:
        Path(args.out).write_text(serialized)
        sys.stderr.write(f"\nAlso wrote to {args.out}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
