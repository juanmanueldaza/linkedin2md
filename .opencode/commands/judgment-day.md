---
description: Run dual-model adversarial code review
agent: n3rv
subtask: true
model: opencode-go/deepseek-v4-pro
---
Run a dual-model adversarial review for: $ARGUMENTS

Load the `judgment-day` skill and follow the full protocol.

## Setup

If $ARGUMENTS contains a `change_id` (e.g. "judgment-day for add-user-auth"), extract it.
Otherwise derive a `change_id` from the arguments or prompt the user.

Determine review scope:
- If an SDD run exists for this `change_id`, load the spec from memory:
  `memory_recall(topic_key="sdd-<change_id>-spec")`
- Otherwise, scope the review to the files or description provided in $ARGUMENTS.

## Execute

Follow the full judgment-day skill protocol:

### Phase 1 — Blind Delegation

Delegate a review to another agent via the A2A hub:
```
delegate_task(
  skill_id="review",
  description="Independent code review (judgment-day blind pass).\n\n"
              + "Review scope: <files or change description>\n"
              + "Spec to check against: <spec content or change description>\n\n"
              + "Output format — for each finding:\n"
              + "  SEVERITY: CRITICAL|WARNING|SUGGESTION\n"
              + "  FILE: <path>:<line>\n"
              + "  ISSUE: <description>\n"
              + "  FIX: <recommended fix>\n\n"
              + "Save findings to memory: topic_key=sdd-<change_id>-review-delegated"
)
```

While waiting, run your own independent review — read all changed files and list every finding.
Save your findings: `memory_save(topic_key="sdd-<change_id>-review-local", type="context", ...)`

### Phase 2 — Wait and Collect

Poll for delegated result: `get_task(task_id=<delegated_task_id>)` — up to 5 polls, ~10s apart.
If unavailable after 5 polls, proceed with local-only verdict and note the gap.

### Phase 3 — Synthesis

Classify each finding:
- **CONFIRMED**: found by both → must fix
- **SUSPECT-A**: local only → likely fix
- **SUSPECT-B**: delegated only → likely fix
- **CONTRADICTION**: disagreement on same location → escalate to human

Save synthesis: `memory_save(topic_key="sdd-<change_id>-judgment", type="context", ...)`

### Phase 4 — Fix Loop

Fix all CONFIRMED and SUSPECT findings at CRITICAL or WARNING severity.
Re-run synthesis — maximum **2 iterations**. Escalate remaining issues to the user.

## Done

Report to the user:
- Verdict table (findings, severity, status)
- Fix loop iterations completed
- Memory keys written: `sdd-<change_id>-review-local`, `sdd-<change_id>-review-delegated`, `sdd-<change_id>-judgment`
- Any escalations requiring human judgment