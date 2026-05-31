---
description: Review code changes against project standards
agent: n3rv
subtask: true
---
Review the code changes in: $ARGUMENTS

1. Read `AGENTS.md` at the project root for coding standards
2. Check the Skill Index in `AGENTS.md` — use the `skill` tool to load skills that apply to the changed files
3. Apply universal rules and skill-specific REJECT/REQUIRE/PREFER rules

Produce:
1. Summary of changes
2. Issues found (CRITICAL / WARNING / SUGGESTION) — cross-referenced against AGENTS.md rules
3. Specific file:line references
4. Recommended fixes