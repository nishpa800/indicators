# Reference: Pine grep patterns

The canonical search patterns for Phase 1 ENUMERATE. Every subagent uses these so occurrences are classified consistently across all 22+ Pine files.

## Setup

Set the target name to `T` (e.g. `UNIFIED_COMBO_BULL`).

Build the alias set per `references/4-phase-procedure.md § Phase 1 step 1`:

```bash
ALIASES=(UNIFIED_COMBO_BULL csNew3_Bull unified_combo UC sigUnifiedComboBull)
```

## Pattern 1 — DEFINITION

A DEFINITION is a Pine assignment that produces the boolean (or value) for the target.

Patterns to match:

```regex
(^|\s)(var\s+)?(bool|float|int|string|color)?\s*<ALIAS>\s*(:=|=)\s*
```

Grep example:

```bash
grep -nE '(^|[[:space:]])((var[[:space:]]+)?(bool|float|int|string|color)[[:space:]]+)?<ALIAS>[[:space:]]*(:?=)[[:space:]]*' <file>
```

Examples that should match:

```
bool sigUNIFIED_COMBO_BULL = conf and csNew1 and csNew2[1]
var float pp_barSize = 3.0
csNew3_Bull := isMatrixCombo[1] and isFvgCombo
```

Examples that should NOT match (these are REFERENCES, not DEFINITIONS):

```
anyBull = sigUNIFIED_COMBO_BULL or sigHwBull
if csNew3_Bull
    label.new(bar_index, na, "UC")
```

## Pattern 2 — REFERENCE

The target appears on the RHS of an expression or in a conditional, but is NOT being assigned.

Pragmatic approach: find every occurrence of the alias, subtract DEFINITION matches.

```bash
grep -nE '\b<ALIAS>\b' <file> > all_occurrences.txt
grep -nE '(^|[[:space:]])((var[[:space:]]+)?(bool|float|int|string|color)[[:space:]]+)?<ALIAS>[[:space:]]*(:?=)' <file> > definitions.txt
# REFERENCES = (all - definitions - input_lines - plot_lines - alert_lines - comment_lines)
```

## Pattern 3 — INPUT

The target is exposed as a Pine `input.*` toggle, slider, dropdown, etc.

```regex
<ALIAS>\s*=\s*input\.(bool|int|float|string|source|color|timeframe|symbol|session|price|time|enum|text_area)\s*\(
```

Grep:

```bash
grep -nE '<ALIAS>[[:space:]]*=[[:space:]]*input\.(bool|int|float|string|source|color|timeframe|symbol|session|price|time|enum|text_area)' <file>
```

Examples:

```
show_UNIFIED_COMBO = input.bool(true, "Show Unified Combo", group=grp_plots)
gziProximity = input.int(6, "Max Bar Distance", minval=1, maxval=200)
```

## Pattern 4 — PLOT

A `plotshape`, `plotchar`, `plot`, `plotbar`, `plotcandle`, `plotarrow`, `plotzigzag`, `bgcolor`, or `barcolor` call gated by the target.

```regex
plot(shape|char|bar|candle|arrow|zigzag)?\s*\([^)]*\b<ALIAS>\b
bgcolor\s*\([^)]*\b<ALIAS>\b
barcolor\s*\([^)]*\b<ALIAS>\b
```

Grep:

```bash
grep -nE '(plot(shape|char|bar|candle|arrow|zigzag)?|bgcolor|barcolor)[[:space:]]*\(' <file> | grep -E '\b<ALIAS>\b'
```

Examples:

```
plotshape(sigUNIFIED_COMBO_BULL, title="UC", style=shape.flag, ...)
bgcolor(csNew3_Bull ? color.green : na, ...)
```

## Pattern 5 — ALERT

`alertcondition()` or `alert()` call gated by the target.

```regex
alertcondition\s*\([^)]*\b<ALIAS>\b
alert\s*\([^)]*\b<ALIAS>\b
```

Grep:

```bash
grep -nE 'alert(condition)?[[:space:]]*\(' <file> | grep -E '\b<ALIAS>\b'
```

## Pattern 6 — COMMENT

Mentioned only inside a `//` line comment (no logic).

Grep:

```bash
grep -nE '//.*\b<ALIAS>\b' <file>
```

## Aggregation script template

```bash
#!/usr/bin/env bash
# For a single Pine file, produce the classified occurrence list.

T=$1                # primary alias
ALIASES=$2          # comma-separated
FILE=$3

ALIAS_RE=$(echo "$ALIASES" | tr ',' '|')

# All occurrences
all=$(grep -nE "\b($ALIAS_RE)\b" "$FILE")

# Classify each line by checking against patterns 1-6 in order
echo "$all" | while IFS=: read -r line content; do
    case "$content" in
        *"//"*) classification="COMMENT" ;;
        *"plotshape"*|*"plotchar"*|*"plot("*|*"bgcolor"*|*"barcolor"*) classification="PLOT" ;;
        *"alertcondition"*|*"alert("*) classification="ALERT" ;;
        *"input."*) classification="INPUT" ;;
        *=*|*":="*) classification="DEFINITION" ;;
        *) classification="REFERENCE" ;;
    esac
    printf "%s:%s  %s\n" "$line" "$classification" "$(echo "$content" | sed 's/^[[:space:]]*//' | cut -c1-80)"
done
```

(Not a hard requirement — subagents can classify in their own way as long as they follow the 6-class taxonomy. The above is just convenience.)

## Caveats

- **Pine is whitespace-sensitive on the LHS**: `bool sigX = ...` (definition) vs `   sigX = ...` (re-assignment inside `if` block — also a definition for our purposes; record as DEFINITION).
- **Multi-line booleans**: Pine allows line continuation via the `\` character or implicit when an expression ends with an operator. If the DEFINITION spans multiple lines, capture all of them — record the full line range, not just the first line.
- **Pine v6 method-style calls**: `foo.bar()` doesn't show in the same grep pattern as `bar(foo)`. If the target uses method-style syntax, expand the grep to match `\.<ALIAS>\b` too.
- **Case insensitivity**: Pine identifiers ARE case-sensitive. `sigPUP` and `sigpup` are different variables. Don't lowercase the alias set during enumeration; only do that during Phase-2 normalization.
- **Comments often DOCUMENT alias relationships** ("// also known as UC"). These ARE useful — record them as COMMENT occurrences so the alias resolution step finds them.
