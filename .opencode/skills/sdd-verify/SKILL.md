---
name: sdd-verify
description: "Verify the implementation against the spec's acceptance criteria. Produces a pass/fail verdict."
compatibility: opencode
when_to_use: "After sdd-apply. Reads spec and implementation from memory, checks each acceptance criterion."
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_save
model: medium
effort: medium
user-invocable: false
hub-skill-ids: [review]
---

## Goal

Determine whether the implementation satisfies every acceptance criterion in the spec.
Produce a structured verdict that can be acted on.

## Steps

1. Load spec: `memory_recall(topic_key="sdd-<change_id>-spec")`
2. Load implementation notes: `memory_recall(topic_key="sdd-<change_id>-impl")`
3. For each acceptance criterion:
   a. Read the relevant code
   b. Run tests where applicable
   c. Mark as PASS, FAIL, or PARTIAL with evidence
4. Check for regressions: run the full test suite
5. Save verdict to memory:
   - title: `SDD Verify: <change_id>`
   - topic_key: `sdd-<change_id>-verify`
   - type: `context`
   - content (structured):
     ```
     ## Acceptance Criteria Check

     | Criterion | Status | Evidence |
     |-----------|--------|----------|
     | <criterion 1> | PASS/FAIL/PARTIAL | <file:line or test name> |
     ...

     ## Regression Check
     <test suite result>

     ## Verdict
     APPROVED / NEEDS_WORK

     ## Blocking Issues (if NEEDS_WORK)
     <what must be fixed before approval>
     ```

## Output

If verdict is APPROVED, the workflow proceeds to sdd-archive.
If NEEDS_WORK, the blocking issues are returned to the orchestrator for remediation.