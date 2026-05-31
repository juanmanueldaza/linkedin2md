---
name: judgment-day
description: "Dual-model adversarial review: local and delegated reviewers audit independently, verdicts are synthesized."
compatibility: opencode
when_to_use: "After sdd-apply, as an enhanced alternative to sdd-verify. Also usable standalone for any code review."
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_save
  - mcp__n3rv-hub__delegate_task
  - mcp__n3rv-hub__get_task
model: high
effort: high
user-invocable: true
hub-skill-ids: [review, reasoning]
---

## Goal

Two independent reviewers — local reviewer (you) and delegated reviewer (via hub) — review the same code
without seeing each other's findings. Verdicts are synthesized into a confidence-weighted table.

## Protocol

### Phase 1 — Blind Delegation

1. Delegate a review task to another reviewer via the hub:
   ```
   delegate_task(
     skill_id="review",
     description="Independent code review (judgment-day blind pass).\n\n"
                 + "Review scope: <files changed in this SDD run>\n"
                 + "Spec to check against: <sdd-<change_id>-spec from memory>\n\n"
                 + "Output format — for each finding:\n"
                 + "  SEVERITY: CRITICAL|WARNING|SUGGESTION\n"
                 + "  FILE: <path>:<line>\n"
                 + "  ISSUE: <description>\n"
                 + "  FIX: <recommended fix>\n\n"
                  + "Save findings to memory: topic_key=sdd-<change_id>-review-delegated"
   )
   ```
2. While the delegated reviewer works, run your own independent review:
   - Load spec: `memory_recall(topic_key="sdd-<change_id>-spec")`
   - Read all changed files
   - List every finding with SEVERITY, FILE:LINE, ISSUE, FIX
   - Save your findings: `memory_save(topic_key="sdd-<change_id>-review-local", ...)`

### Phase 2 — Wait and Collect

3. Poll for delegated result: `get_task(task_id=<delegated_task_id>)`
   - Poll up to 5 times with ~10s between attempts
   - If no result after 5 polls: note "Delegated review unavailable" and proceed with local-only verdict

### Phase 3 — Synthesis

4. Compare findings from both reviewers. Classify each finding:
   - **CONFIRMED**: found by BOTH reviewers → high confidence, must fix
   - **SUSPECT-A**: found by local only → triage, likely fix
   - **SUSPECT-B**: found by delegated only → triage, likely fix
   - **CONTRADICTION**: reviewers disagree on the same location → escalate to human

5. Save synthesis to memory:
   - title: `Judgment Day: <change_id>`
   - topic_key: `sdd-<change_id>-judgment`
   - type: `context`
   - content:
     ```
     ## Verdict Table

     | Finding | Severity | Reviewer | Location | Issue |
     |---------|----------|----------|----------|-------|
     | <desc>  | CRITICAL | CONFIRMED | file:line | ... |
     ...

     ## Fix Loop Status
     Iteration: <N> / max 2

     ## Escalations
     <contradictions requiring human judgment>
     ```

### Phase 4 — Fix Loop

6. Fix all CONFIRMED and SUSPECT findings (severity CRITICAL or WARNING)
7. Re-run the synthesis — maximum **2 iterations**
8. If issues remain after 2 iterations: escalate to human with the verdict table

## Standalone Usage

When used outside the SDD workflow, replace `sdd-<change_id>-spec` references with a
description of what the code is supposed to do, and scope the review to the files you specify.