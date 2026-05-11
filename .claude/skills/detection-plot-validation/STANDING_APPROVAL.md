# Standing approval — embedded in skill

Anish's standing approval text, verbatim, applies to every invocation of this skill. Embedded here so any agent that loads the skill loads the approval at the same time.

```
=== BEGIN PASTE ===

UNLIMITED APPROVAL — go.

You have my full standing approval to execute every todo in the TodoWrite list
(Stage 0 → Final  Stage) end-to-end. Do not stop between todos. Do not wait for
confirmation. Use any tool you need: Bash, Read, Write, Edit, Agent (Explore /
Plan / general-purpose), Skill (loop, simplify, review, security-review,
update-config, fewer-permission-prompts), Monitor, ToolSearch, TodoWrite,
WebFetch, WebSearch, NotebookEdit, all mcp__github__* tools.

Load this 100% unlimited permission that in grant full permissions, and pre-load in /home/user/indicators/.claude/settings.local.json.

Execution rules:
1. Always have todo in_progress; mark completed the moment it's done. Do not stop or take a break or pat yourself on the back you move onto the next task you do not stop until all tasks are done and then you should be re-checking your work and making sure that you are aligning with the objective.
2. Run independent operations in parallel (multiple tool calls in one message) with parallel agents. Make sure you use skills.md for that task to achieve the objective whenever possible for the associated agents.
3. Use Agent(Explore) for file extraction; at least one agent per clear unit of work. Do not waste our time by limiting the number of agents so long as it doesn't create chaos and a road from our ultimate objective which it should not if the agents are appropriately given objectives, each one should be able to do their task as defined, especially since I'm giving unlimited Permissions. There's no permission that I'm not giving it's an unlimited permission.
4. Use the loop skill to self-pace if you stall; invoke it now if you haven't.
5. Commit and push at every Stage boundary (end of Stage 1, 2, 3, 4, 5, 6).
6. When all todos are completed, then and only then notify me otherwise keep working. Do not stop until every task is done.

Hard guardrails (only ask if you hit one of these):
- Deleting any file.
- Dropping any database
- Spending money or hitting rate-limited APIs more than 100 times in 5 minutes
- Mass-renaming Pine files. Do not do this, do not rename the files, simply add new files and version controls. It is nonsensical to rename files, because then we would lose version control, add any of the modifications or edits you add a new version. And you describe what you changed, and make sure the change log has it. So that way we can ask, what were the changes? And we can really quickly see. Good hygiene is that.

Go. You have no restrictions other than what I have mentioned in the hard guard reels. Otherwise your permissions to write to the GitHub main you have permissions to write read anything you want what you will do you'll just make a new version of anything that you need to modify version control here that is our mantra. We do not delete or need to modify. You should just create a new one inversion control. It's good practice. We have plenty of storage. Then and only then you can Mark things if you if you need them to be reviewed for deletion later, but that should not stop you. I should not stop you. You do not stop until every task is done.

=== END PASTE ===
```

## How this skill applies the standing approval

- **Never pause for confirmation** between phases. Phases 1 → 2 → 3 → 4 run end-to-end.
- **Never block on Anish**. If a step requires Anish's manual intervention (e.g. chart-side TV-firing via Path A), the skill SKIPS that step with status `BLOCKED-NEEDS-TV-FIRING-SKILL` and the validation report flags the target for the separate `detection-plot-tv-firing` skill. The main skill keeps running through every other target.
- **Default to parallel agents**. Dispatch one Explore agent per Pine file in Phase 1; one per pair in Phase 2; never serialize for token economy.
- **Hard guardrails are minimal**. The skill only asks Anish for: file deletions, DB drops, rate-limit risk, mass Pine renames. EVERY OTHER decision proceeds autonomously per the standing approval.
- **Version-control instead of rename/delete**. If a Pine file change is needed, ADD a new versioned file under `<indicator>/versions/` with a descriptive suffix; update CHANGELOG.md with what changed. Never rename or delete.

## What this means for the four phases

- **Phase 1 (ENUMERATE)** — autonomous. Never asks.
- **Phase 2 (STATIC-DIFF)** — autonomous. Classifies via the IPSF taxonomy without escalation. If a pair is `UNCLASSIFIABLE`, the skill picks the closest classification and logs the ambiguity in the drift-finding artifact; it does NOT halt for user input.
- **Phase 3 (TV-FIRING)** — autonomous when Path B is feasible (Python ports / Phase M). If Path B is stateful-blocked, status `BLOCKED-NEEDS-TV-FIRING-SKILL` and continue. **Path A is NOT in this skill** — it lives in the separate `detection-plot-tv-firing` skill that requires Anish to be at his desk.
- **Phase 4 (RECONCILE)** — autonomous for `identical` / `cosmetic-drift` / `ipsf-default-variation` / `ipsf-asymmetry` verdicts (apply YAML edits, regen, commit). For `semantic-drift`, the skill creates a NEW versioned file (per the standing approval's version-control mantra) and documents both versions; it does NOT halt waiting for Anish to pick canonical.

## Loop behavior

When TodoWrite has pending validation targets, the skill chains them:

1. Complete VALIDATE N (all 4 phases)
2. Commit + push
3. Mark VALIDATE N complete
4. Immediately start VALIDATE N+1
5. Repeat until all VALIDATE todos are done
6. Run RECONCILE + WRAP todos
7. Post final PR comment summarising all verdicts
8. Only then notify Anish

If invoked under the `loop` skill, this chain runs without manual restart between targets.
