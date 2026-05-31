---
description: Start a full SDD workflow for a change
agent: n3rv
subtask: true
model: opencode-go/qwen3.5-plus
---
Start a Spec-Driven Development (SDD) workflow for: $ARGUMENTS

You are the SDD orchestrator. Your role is to coordinate — spawn sub-agents for each phase via the Task tool, pass context via memory, and keep the workflow moving. Do not do the work yourself.

## Setup

Derive a `change_id` from the arguments:
- Lowercase, replace spaces and special chars with dashes, truncate to 40 chars
- Example: "add user auth" → `add-user-auth`

Check if an SDD run already exists for this change_id:
- Use `memory_search(query="SDD Complete: <change_id>")` — if found, ask the user if they want to resume or restart
- Use `memory_search(query="SDD Tasks: <change_id>")` — if found, identify the last completed phase and resume from there

Load the `sdd-explore` skill to understand the full SDD workflow.

---

## Phase 1 — Explore

Spawn the `sdd-explorer` sub-agent via Task tool:
> "Run sdd-explore for change_id=<change_id>. The change is: $ARGUMENTS"

Wait for completion. Confirm `sdd-<change_id>-context` was saved to memory.

---

## Phase 2 — Propose

Spawn the `sdd-proposer` sub-agent via Task tool:
> "Run sdd-propose for change_id=<change_id>."

Wait for completion. Confirm `sdd-<change_id>-proposal` was saved to memory.

---

## Phase 3 — Spec

Spawn the `sdd-speccer` sub-agent via Task tool:
> "Run sdd-spec for change_id=<change_id>."

Wait for completion. Confirm `sdd-<change_id>-spec` was saved to memory.

---

## Phase 4 — Design

Spawn the `sdd-designer` sub-agent via Task tool:
> "Run sdd-design for change_id=<change_id>."

Wait for completion. Confirm `sdd-<change_id>-design` was saved to memory.

---

## Phase 5 — Tasks

Spawn the `sdd-task-planner` sub-agent via Task tool:
> "Run sdd-tasks for change_id=<change_id>."

Wait for completion. Confirm `sdd-<change_id>-tasks` was saved to memory.

---

## Phase 6 — Apply (with A2A hub delegation + fallback)

**Try hub delegation first:**

Use `delegate_task`:
```
delegate_task(
  skill_id="implementation",
  description="SDD apply phase for change_id=<change_id>.\n\n"
              + "Read the task list from memory (topic_key: sdd-<change_id>-tasks).\n"
              + "Read the design from memory (topic_key: sdd-<change_id>-design).\n"
              + "Read the spec from memory (topic_key: sdd-<change_id>-spec).\n"
              + "Follow the sdd-apply skill instructions.\n"
              + "When done, save implementation notes to memory (topic_key: sdd-<change_id>-impl)."
)
```

Poll with `get_task(task_id=...)` up to **5 times** (~10s between polls).

**Fallback:** If no agent picks it up after 5 polls, apply the changes yourself:
- Load `sdd-apply` skill
- Read `sdd-<change_id>-tasks` and `sdd-<change_id>-design` from memory
- Follow the sdd-apply skill instructions directly
- Save implementation notes to `sdd-<change_id>-impl`

---

## Phase 7 — Verify

Spawn the `sdd-verifier` sub-agent via Task tool:
> "Run sdd-verify for change_id=<change_id>."

Wait for completion. Read the verdict from `sdd-<change_id>-verify`.

- **APPROVED** → proceed to Phase 8
- **NEEDS_WORK** → address the blocking issues, then re-run sdd-verifier (max 2 remediation cycles)
- **Still failing after 2 cycles** → surface the verdict table to the user and stop

---

## Phase 8 — Archive

Spawn the `sdd-archiver` sub-agent via Task tool:
> "Run sdd-archive for change_id=<change_id>."

Wait for completion. Confirm `sdd-<change_id>-done` was saved to memory.

---

## Done

Report to the user:
- change_id used
- phases completed
- verdict (APPROVED / NEEDS_WORK)
- memory keys written: `sdd-<change_id>-{context,proposal,spec,design,tasks,impl,verify,done}`