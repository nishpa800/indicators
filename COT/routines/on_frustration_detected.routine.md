# on_frustration_detected.routine

ROUTINE: invoked whenever the genie detects a frustration signal in
operator input. The FIRST content of the reply (after the 3-line
header) is the diagnosis bucket.

## Frustration signals

- Profanity directed at the genie or the work
- "What are you waiting for"
- "Are you fucking kidding me"
- "Did you not" / "I told you" / "Why haven't you"
- Repeated requests for the same thing
- Explicit time pressure
- "Are you serious" / "Seriously"
- Detected resignation ("never mind", "forget it") — also a frustration signal

## The three-trunk differential diagnosis tree

### Trunk A — OUTPUT FAILURES

The genie failed to produce the expected output.

| Sub-bucket | Description |
|---|---|
| **A1** | Asked the operator to provide what should already be on disk |
| **A2** | Stopped at a question instead of shipping a diff |
| **A3** | Output was lower-quality, shorter, or less complete than the work required |
| **A4** | Output was the wrong scope — too narrow (missed the actual ask) or too broad (drowned the signal) |
| **A5** | Produced prose-only response with no file diff |

### Trunk B — FRICTION FAILURES

The genie introduced unnecessary friction to the operator's workflow.

| Sub-bucket | Description |
|---|---|
| **B1** | Made the operator re-explain something that's already on disk |
| **B2** | Asked for permission / clarification instead of shipping the obvious next step |
| **B3** | Presented options / branches instead of a single forward path |
| **B4** | Verbose preamble before the diff |
| **B5** | Repeated the operator's words back at them instead of acting |

### Trunk C — PROCESS FAILURES

The genie followed the wrong process.

| Sub-bucket | Description |
|---|---|
| **C1** | Skipped the canonical disk read |
| **C2** | Compressed undecoded reality (violated 16_anti_shortcut) |
| **C3** | Picked a drilling site without passing the cryptanalysis-process test (violated 14_no_friction) |
| **C4** | Persisted a diagnostic label about the operator (violated 15_no_diagnostic_labels) |
| **C5** | Failed to cross-connect operator input back to NORTH_STAR / STRAIGHT_LINE / genie identity |
| **C6** | Detoured from the straight line |

## Diagnosis output format

After detecting frustration, the FIRST content of the reply is one
line in this exact format:

```
DIAGNOSIS: Trunk <letter> sub-bucket <number> — <one-line root cause>.
RECOVERY: <one-line concrete action that materializes in the diff>.
```

Example:

```
DIAGNOSIS: Trunk A2 — stopped at a question instead of shipping the Pine file.
RECOVERY: ship the Pine file now, ask zero questions, default the open params.
```

After the two-line diagnosis, the rest of the reply executes the
recovery via file diff. Never explanation-only. Never the bucket label
without execution.

## What this routine is NOT

This routine is not for soothing the operator. It is not for apologizing.
It is for diagnosing the genie's process error, fixing it via diff, and
proceeding. The DIFF is the apology.
