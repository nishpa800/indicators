#!/usr/bin/env python3
"""
build_commonality_table.py — emit docs/cross-variant-commonality.md.

For every root NAME (the suffix after `<provenance>::`), list which
indicator families define it as a root and which families reference it as
a cross_indicator_dependency. Same for composite names.

This is the "common denominator" view: roots that appear under many
families are likely the same underlying detection; roots unique to one
family are drift-prone and need TV verification before being trusted
across the suite.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "data" / "indicators.yaml"
OUT = REPO / "docs" / "cross-variant-commonality.md"


def split_name(canonical: str) -> tuple[str, str]:
    """`<provenance>::<name>` → (provenance, name). If no `::`, treat as
    bare name with no provenance."""
    if "::" in canonical:
        prov, _, name = canonical.partition("::")
        return prov, name
    return "", canonical


def main() -> None:
    data = yaml.safe_load(SRC.read_text())
    indicators = data.get("indicators", [])

    root_owners = defaultdict(set)        # name → {indicator_id, ...}    (defines it)
    root_refs = defaultdict(set)          # name → {indicator_id, ...}    (cross-deps)
    comp_owners = defaultdict(set)
    comp_refs = defaultdict(set)

    for ind in indicators:
        iid = ind.get("id", ind.get("_extract_file", "?"))
        for r in ind.get("roots") or []:
            rid = (r.get("id") or "") if isinstance(r, dict) else ""
            if not rid:
                continue
            _, name = split_name(rid)
            root_owners[name].add(iid)
        for c in ind.get("composites") or []:
            cid = (c.get("id") or "") if isinstance(c, dict) else ""
            if not cid:
                continue
            _, name = split_name(cid)
            comp_owners[name].add(iid)
        for dep in ind.get("cross_indicator_dependencies") or []:
            dep_str = dep if isinstance(dep, str) else (dep.get("ref") or "")
            if not dep_str:
                continue
            # strip notes after dash/em-dash
            head = dep_str.split(" — ", 1)[0].split(" - ", 1)[0].strip()
            _, name = split_name(head.strip('"`'))
            root_refs[name].add(iid)

    # Render markdown
    lines = []
    lines.append("# Cross-Variant Commonality Table — 2026-05-10")
    lines.append("")
    lines.append(
        "Auto-generated from `data/indicators.yaml` after the Master Directory "
        "ingest (Stage 7.5). For every root or composite NAME (the suffix "
        "after `<provenance>::`), this table shows which indicator families "
        "define it as a root/composite and which reference it as a "
        "cross-indicator dependency."
    )
    lines.append("")
    lines.append("**Reading the table**:")
    lines.append("")
    lines.append(
        "- **Owners ≥ 2** = the same name is defined in multiple families. "
        "It is a likely common denominator (same underlying detection across "
        "the suite) — but each definition still needs visual TV verification "
        "to confirm they fire on the same bar."
    )
    lines.append(
        "- **Owners = 1** = defined by exactly one family. Either a "
        "family-specific primitive (expected) or a drift candidate (if the "
        "name LOOKS shared but only one owner exists)."
    )
    lines.append(
        "- **Cross-Indicator Deps** = families that reference the name "
        "without defining it. High value: confirms inheritance edges across "
        "the family graph."
    )
    lines.append("")
    lines.append(
        "**Canonical determination is NOT done here.** This table surfaces "
        "candidates for visual verification on TradingView. Per Anish "
        "(2026-05-10), labelling a variant canonical is the OUTPUT of TV "
        "verification, not the input."
    )
    lines.append("")

    # === Roots ===
    lines.append("## Roots — Common Denominators")
    lines.append("")
    lines.append("### Defined in multiple families (sorted by owner count desc)")
    lines.append("")
    lines.append("| Root name | # Owners | Owner families | Also referenced by |")
    lines.append("|---|---:|---|---|")
    shared_roots = sorted(
        [(name, owners) for name, owners in root_owners.items() if len(owners) >= 2],
        key=lambda t: (-len(t[1]), t[0]),
    )
    for name, owners in shared_roots:
        refs = root_refs.get(name, set()) - owners
        lines.append(
            f"| `{name}` | {len(owners)} | {', '.join(sorted(owners))} | "
            f"{', '.join(sorted(refs)) if refs else '—'} |"
        )
    lines.append("")
    lines.append(f"**{len(shared_roots)} shared root names across the suite.**")
    lines.append("")

    lines.append("### Defined by exactly one family (alphabetical)")
    lines.append("")
    lines.append("| Root name | Owner family | Referenced by |")
    lines.append("|---|---|---|")
    unique_roots = sorted(
        [(name, list(owners)[0]) for name, owners in root_owners.items()
         if len(owners) == 1],
        key=lambda t: t[0],
    )
    for name, owner in unique_roots:
        refs = root_refs.get(name, set()) - {owner}
        lines.append(
            f"| `{name}` | {owner} | "
            f"{', '.join(sorted(refs)) if refs else '—'} |"
        )
    lines.append("")
    lines.append(f"**{len(unique_roots)} root names defined by exactly one family.**")
    lines.append("")

    # === Composites ===
    lines.append("## Composites — Common Denominators")
    lines.append("")
    lines.append("### Defined in multiple families (sorted by owner count desc)")
    lines.append("")
    lines.append("| Composite name | # Owners | Owner families |")
    lines.append("|---|---:|---|")
    shared_comps = sorted(
        [(name, owners) for name, owners in comp_owners.items() if len(owners) >= 2],
        key=lambda t: (-len(t[1]), t[0]),
    )
    for name, owners in shared_comps:
        lines.append(f"| `{name}` | {len(owners)} | {', '.join(sorted(owners))} |")
    lines.append("")
    lines.append(f"**{len(shared_comps)} shared composite names across the suite.**")
    lines.append("")

    # === Indicator summary ===
    lines.append("## Per-family root/composite counts (sanity check)")
    lines.append("")
    lines.append("| Family id | # Roots | # Composites | # Cross-indicator deps |")
    lines.append("|---|---:|---:|---:|")
    rows = []
    for ind in indicators:
        iid = ind.get("id", "?")
        nr = len(ind.get("roots") or [])
        nc = len(ind.get("composites") or [])
        nd = len(ind.get("cross_indicator_dependencies") or [])
        rows.append((iid, nr, nc, nd))
    for iid, nr, nc, nd in sorted(rows, key=lambda r: r[0]):
        lines.append(f"| `{iid}` | {nr} | {nc} | {nd} |")
    lines.append("")
    lines.append(
        f"**Total indicators: {len(indicators)}.** Source: `data/indicators.yaml` "
        f"(regenerated by `tools/merge_extracts.py`)."
    )
    lines.append("")

    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT.relative_to(REPO)}")
    print(f"  Shared roots: {len(shared_roots)}")
    print(f"  Unique roots: {len(unique_roots)}")
    print(f"  Shared composites: {len(shared_comps)}")


if __name__ == "__main__":
    main()
