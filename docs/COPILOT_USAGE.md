# Copilot Usage Policy

## General Rules
- Copilot should write/edit files directly in the editor (no bash commands).
- Always include tests and show unified diffs for changes.
- Run editor-integrated tests and fix lint/format issues before committing.
- For docs-only PRs: rely on `docs.yml` workflow (lint only, no code tests).

## Checklist Before Finishing a Task
- [ ] All files edited/created with correct content.
- [ ] Tests written and passing locally.
- [ ] Lint/format issues fixed (ruff/black).
- [ ] Unified diffs shown for all changes.
- [ ] No shell commands executed; all via editor.
- [ ] Documentation updated if needed.
