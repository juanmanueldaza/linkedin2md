---
name: sdd-archive
description: "Archive all SDD artifacts for a change as a single completed record in memory."
compatibility: opencode
when_to_use: "Final phase of the SDD workflow, after sdd-verify returns APPROVED."
allowed-tools:
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_save
  - mcp__n3rv-memory__memory_search
model: low
effort: low
user-invocable: false
---

## Goal

Consolidate all SDD phase artifacts into one searchable summary entry and mark the change as done.

## Steps

1. Load all phase artifacts from memory:
   - `memory_recall(topic_key="sdd-<change_id>-context")`
   - `memory_recall(topic_key="sdd-<change_id>-proposal")`
   - `memory_recall(topic_key="sdd-<change_id>-spec")`
   - `memory_recall(topic_key="sdd-<change_id>-design")`
   - `memory_recall(topic_key="sdd-<change_id>-tasks")`
   - `memory_recall(topic_key="sdd-<change_id>-impl")`
   - `memory_recall(topic_key="sdd-<change_id>-verify")`
2. Write a consolidated archive entry:
   - title: `SDD Complete: <change_id>`
   - topic_key: `sdd-<change_id>-done`
   - type: `summary`
   - content (structured):
     ```
     ## Change: <change_id>
     ## Description: <original change request>
     ## Status: COMPLETE
     ## Approach taken: <one-sentence summary from proposal>
     ## Key design decisions: <2–3 bullet points from design>
     ## Tests added: <from impl notes>
     ## Verified: <date/session from verify>
     ## Artifacts: sdd-<change_id>-{context,proposal,spec,design,tasks,impl,verify}
     ```

## Note

This entry becomes the institutional memory for this change — searchable in future SDD runs
when exploring related areas of the codebase.