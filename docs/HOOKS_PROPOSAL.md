# Hooks proposal — for `detection-plot-validation` skill

You asked "I don't know if we need any hooks for that skill". Three candidates, you pick which to enable. Each one is a small `.claude/settings.json` (or `.claude/settings.local.json`) addition; you can enable them one at a time, test, and disable any that misbehave.

## Background — what hooks are

Claude Code hooks are shell commands the harness runs at specific lifecycle events. Documented at https://docs.claude.com/en/docs/claude-code/hooks. Configured in `.claude/settings.json` (or `settings.local.json`) under the `hooks` key.

Lifecycle events relevant to the bible workflow:

- **`PostToolUse`** — fires AFTER a tool call (e.g. after a `Write` to a specific file)
- **`PreToolUse`** — fires BEFORE a tool call; can block the call (e.g. before a `Bash` running `git commit`)
- **`Stop`** — fires when a session is about to end (you already have one — `~/.claude/stop-hook-git-check.sh`)
- **`UserPromptSubmit`** — fires when you send a message; can inject context

## Proposal A — auto-regen on extract edits (POST-TOOL-USE)

**Trigger**: any `Write` or `Edit` to `bible-input/extract-*.yaml`.

**Action**: automatically run `tools/merge_extracts.py`, then `tools/build_lineage_cards.py`, then `tools/build_docs.py`.

**Why useful**: the bible's source of truth is `bible-input/extract-*.yaml`. Every Phase 4 reconcile edits one of these files. The derived artifacts (`data/indicators.yaml`, `data/indicators.json`, all the `docs/*.md` files, all the lineage cards, visual trees) MUST be regenerated to match — otherwise the next session reads stale data and makes wrong decisions on it.

**Why dangerous**: if `merge_extracts.py` throws (e.g. YAML syntax error in the just-edited extract), the regen aborts. The hook should NOT block the session — it should log the error and continue. The user fixes the YAML and re-saves; the hook re-runs and succeeds.

**Settings snippet**:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'bible-input/extract-.*\\.yaml'; then cd /home/user/indicators && python3 tools/merge_extracts.py 2>&1 | tail -3 && python3 tools/build_lineage_cards.py 2>&1 | tail -1 && python3 tools/build_docs.py 2>&1 | tail -1 || echo 'regen failed — fix YAML and re-save to retry'; fi"
          }
        ]
      }
    ]
  }
}
```

**Trade-off**: every `Edit` / `Write` invocation in the repo runs the matcher (cheap — just a grep). If the matcher hits, regen runs (~2 seconds). Worth it for the "no stale data" guarantee.

**Recommendation**: ENABLE. The cost of stale derived artifacts is high; the hook is cheap.

---

## Proposal B — YAML == JSON guard before commit (PRE-TOOL-USE)

**Trigger**: any `Bash` running `git commit`.

**Action**: run a 2-line Python script that asserts `yaml.safe_load(open('data/indicators.yaml')) == json.load(open('data/indicators.json'))`. If they differ, BLOCK the commit.

**Why useful**: the bible commits MUST have YAML and JSON in sync. If a hand-edit (or a bot edit) bypasses `merge_extracts.py`, the JSON gets out of sync silently. Committing that ships a corrupted source of truth.

**Why low-risk**: the hook is read-only and runs in <1 second. It can be bypassed with `--no-verify` if absolutely needed (you'd want to do that knowingly).

**Settings snippet**:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git commit'; then python3 -c \"import yaml,json; y=yaml.safe_load(open('/home/user/indicators/data/indicators.yaml')); j=json.load(open('/home/user/indicators/data/indicators.json')); assert y==j, 'YAML != JSON; run tools/merge_extracts.py before commit'\" || exit 1; fi"
          }
        ]
      }
    ]
  }
}
```

**Trade-off**: every `Bash` invocation runs the matcher. Only triggers on `git commit`. ~1 second when triggered. Blocks commit if mismatch.

**Recommendation**: ENABLE. The "ship corrupted YAML/JSON" failure mode is exactly what this prevents.

---

## Proposal C — stop-hook reinforcement (STOP)

**Trigger**: session about to end.

**Current behavior**: your existing `~/.claude/stop-hook-git-check.sh` complains about untracked files. Good.

**Proposed addition**: ALSO check that:
- `data/indicators.yaml` parses
- `data/indicators.json` parses
- YAML == JSON
- No staged-but-not-committed changes to `bible-input/extract-*.yaml` (those should regen before commit)

**Why useful**: defense in depth. If A and B somehow fail to fire, C catches the session-end state.

**Why low-risk**: stop hooks can already block session-end with a message. Your existing hook already does this. Adding 4 more checks is incremental.

**Settings snippet** (proposed addition to your existing stop-hook script):

```bash
# Add to ~/.claude/stop-hook-git-check.sh

# Bible-specific checks (only if we're in the indicators repo)
if [ "$(git rev-parse --show-toplevel 2>/dev/null)" = "$HOME/code/indicators" ] || \
   [ "$(git rev-parse --show-toplevel 2>/dev/null)" = "/home/user/indicators" ]; then
    cd "$(git rev-parse --show-toplevel)"
    # YAML parses
    python3 -c "import yaml; yaml.safe_load(open('data/indicators.yaml'))" 2>/dev/null \
      || echo "WARN: data/indicators.yaml does not parse"
    # JSON parses
    python3 -c "import json; json.load(open('data/indicators.json'))" 2>/dev/null \
      || echo "WARN: data/indicators.json does not parse"
    # YAML == JSON
    python3 -c "import yaml,json; assert yaml.safe_load(open('data/indicators.yaml'))==json.load(open('data/indicators.json'))" 2>/dev/null \
      || echo "WARN: data/indicators.yaml != data/indicators.json"
    # No staged extract edits without regen
    if ! git diff --cached --quiet bible-input/extract-*.yaml 2>/dev/null; then
        if git diff --cached --quiet data/indicators.yaml 2>/dev/null; then
            echo "WARN: bible-input/extract-*.yaml has staged changes but data/indicators.yaml does not — run tools/merge_extracts.py"
        fi
    fi
fi
```

**Recommendation**: ENABLE. Belt-and-suspenders for the worst-case where A and B miss something.

---

## How to enable

For a per-project hook (recommended for the bible work), add to `<repo>/.claude/settings.local.json`. For a user-global hook, add to `~/.claude/settings.json`.

Test each hook independently: enable A, do an edit, verify regen runs. Enable B, do a commit, verify guard triggers on a mismatch (use `python3 -c "import json; json.dump({'fake': True}, open('/tmp/bad.json','w'))"` to force a mismatch and verify the guard catches it). Enable C by editing your existing stop-hook script.

## Anti-recommendations (don't enable these)

- **PostToolUse on every Write/Edit** without a matcher — regen would run on every doc edit, slowing the session.
- **PreToolUse on every Bash** without matcher — same problem.
- **Auto-commit on regen success** — too aggressive; commits should be intentional.
- **Auto-push on commit** — never; user wants the option to inspect before pushing.

## Verifying hooks are working

After enabling, in Claude Code:

```
/hooks
```

Should list the active hooks with their matchers. If a hook fails to fire when expected, check `.claude/settings.local.json` syntax (JSON must validate) and the matcher pattern (case-sensitive, regex semantics per the Claude Code hooks docs).

## Skill v1.1 plan

If you enable A + B + C, the `detection-plot-validation` skill v1.1 will:

- Trust the hooks to do auto-regen + YAML==JSON guard automatically
- Drop the explicit "run merge_extracts.py" step from Phase 4 procedure (the hook handles it)
- Add a section to the validation report noting hooks were verified active

Bump skill version on enabling. Document in `.claude/skills/detection-plot-validation/CHANGELOG.md`.
