# CI & Workflows

## CI Split
- `ci.yml`: Handles code changes (lint + tests for Phase 2+3). Triggers on PR to main, skips docs paths.
- `docs.yml`: Handles docs-only changes (lint only, no code tests). Triggers on PR to main for docs/**, **/*.md, scripts/README_exports.md.

## Branch Protection (main)
- Required: 1 approval, checks [lint, tests].
- Temporary: Set to 0 approvals when working solo (e.g., for auto-merge), then restore to 1.

## Auto-Merge Policy
- Use squash merge for all PRs.
- Arm auto-merge when CI is green and approvals met.
- Re-arm if CI fails and is fixed.

## Pre-commit Hooks
- Optional locally; CI is source of truth.
- `poetry-lock-check` skipped in CI via `SKIP=poetry-lock-check` env.

---

Workflows Project (GitHub)
1) Item added to project — Issues uniquement
Type : Issue ✅ | Pull request ❌

Action : Set value → Status = Backlog

Toggle : On

2) Item reopened
Action : Set value → Status = Backlog

Toggle : On

3) Item closed
Action : Set value → Status = Terminé

Toggle : On

4) Auto-add to project (ajout auto)
Repository : NeoLunaInc/LunaCore

Query : is:issue (optionnel is:open)

Action : Add the item to the project

Si l’UI exige un Set value, choisir Status=Backlog.

5) Pull request merged
Action : Set value → Status = Terminé

Toggle : On

6) Auto-close issue
Trigger : When the status is updated

Filtre : Status: Terminé

Action : Close the issue

Toggle : On

7) Auto-archive items (optionnel)
Filtre : is:issue is:closed updated:<@today-2w

Action : Archive item

Toggle : On

Astuce tri : ajouter un champ Number nommé PhaseNo, le renseigner, puis Sort by PhaseNo (ascending) sur la Board.

## Branch Cleanup
- Use `scripts/cleanup_branches.sh` to safely clean up merged branches.
- Interactive script: lists unmerged remote branches, prompts for keep/delete remote/delete both.
- Requires confirmation before executing deletions.
- Never deletes origin/main.

---
