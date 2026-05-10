# SOP — iCloud Mirror

**When to use**: when syncing the bible to a local Mac + iCloud Drive for
offline access (laptop / phone). Anish runs this manually; the sandbox does
not have iCloud access.

## Goal

Maintain a 1:1 mirror of the indicator bible at `~/iCloud Drive/indicators/`
on Anish's Mac, kept in sync with `https://github.com/nishpa800/indicators`.

## Initial setup (once)

```bash
# On Anish's Mac, in the iCloud Drive root
cd "$HOME/Library/Mobile Documents/com~apple~CloudDocs"
git clone git@github.com:nishpa800/indicators.git
cd indicators
git checkout claude/organize-indicators-hierarchy-8JDw1
```

## Recurring sync (every PR merge)

```bash
cd "$HOME/Library/Mobile Documents/com~apple~CloudDocs/indicators"
git fetch origin
git checkout main      # or whichever branch is canonical at the moment
git pull --ff-only
```

iCloud auto-detects file changes and uploads to the cloud. No additional sync
step needed.

## Reading on iPad / iPhone

iCloud Drive surfaces the markdown files in the Files app. Use any markdown
viewer (Working Copy, Textastic, GitHub Mobile) to render
`INDICATORS_INDEX.md` with proper formatting.

## Don'ts

- **Don't `git push` from the iCloud copy.** Treat it as read-only — pushes
  from a sync copy create merge conflicts when iCloud's filesystem
  half-applies changes.
- **Don't enable "Optimize Mac Storage"** for the iCloud Drive folder —
  iCloud may evict files locally and reload them on demand, which breaks
  `git status` (sees missing files as deletions).
- **Don't run `tools/*.py` from the iCloud copy** — pyyaml installations
  vary between machines; run generators in the canonical repo only.

## Verifying the mirror is current

```bash
cd "$HOME/Library/Mobile Documents/com~apple~CloudDocs/indicators"
git rev-parse HEAD                           # should match origin/main HEAD
git status --short                           # should be empty
ls bible-input/extract-*.yaml | wc -l        # should be 12
ls docs/lineage/*.md | wc -l                 # should be ~76 + 1 INDEX
wc -l data/indicators.yaml data/indicators.json   # should match counts in INDICATORS_INDEX.md
```

If any of these don't match, `git pull` again and inspect.

## Daily-ops loop

Anish's optimisation workflow:

1. **Morning**: open `INDICATORS_INDEX.md` in iCloud Drive on iPad. Review
   any new lineage cards or composites added overnight.
2. **At desk**: load test indicators on TradingView. Run `root-validation`
   and `composite-validation` SOPs as needed.
3. **Findings**: append to `docs/validation-log/<date>-*.md` files in the
   canonical repo (NOT iCloud copy). Commit + push.
4. **Evening**: pull updates back into iCloud copy.

## When the mirror is stale

If iCloud + git get out of sync (rare, but happens after macOS updates), the
nuclear option:

```bash
cd "$HOME/Library/Mobile Documents/com~apple~CloudDocs"
rm -rf indicators
git clone git@github.com:nishpa800/indicators.git
```

iCloud will sync the fresh clone within 30-60 minutes.
