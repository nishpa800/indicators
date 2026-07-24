#!/usr/bin/env bash
# CONSTITUTIONAL GATE — TICK_FRIENDLY_INDEX.md must cover EVERY indicator study in the repo.
# Every non-vendor *.pine file's basename must appear in the index (raw links are matched with
# %20 decoded back to spaces). vendor/pine_libraries/ is excluded by design (TradingView's own
# built-in reference sources, not our studies).
# Usage: tools/check_index_coverage.sh   (run from repo root)
# Exit 0 = every file indexed; exit 1 = at least one study missing from the index.
set -u
cd "$(dirname "$0")/.."
INDEX="TICK_FRIENDLY_INDEX.md"
[ -f "$INDEX" ] || { echo "FAIL: $INDEX not found"; exit 1; }

# Index text with URL-encoded spaces decoded, so 'heavy%20weapons%20v3_...' matches the filename.
decoded=$(sed 's/%20/ /g' "$INDEX")

missing=0
total=0
while IFS= read -r f; do
  total=$((total + 1))
  base=$(basename "$f")
  if ! printf '%s' "$decoded" | grep -qF "$base"; then
    missing=$((missing + 1))
    echo "MISSING FROM INDEX: $f"
  fi
done < <(find . -name '*.pine' -not -path './vendor/*' -not -path './.git/*' | sort)

if [ "$missing" -eq 0 ]; then
  echo "PASS: all $total non-vendor .pine files appear in $INDEX."
  exit 0
else
  echo "FAIL: $missing of $total .pine files are NOT in $INDEX. Every study needs its original AND its tick-friendly build on the index."
  exit 1
fi
