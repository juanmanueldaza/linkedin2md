---
name: sdd-spec
description: "Write a formal specification for a planned change: goals, acceptance criteria, constraints."
compatibility: opencode
when_to_use: "After sdd-propose. Reads the proposal from memory, writes a spec."
allowed-tools:
  - Read
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_save
model: medium
effort: medium
user-invocable: false
---

## Goal

Produce a specification document that defines exactly what the change must do — precise enough
that a reviewer can verify the implementation against it without ambiguity.

## Steps

1. Load proposal: `memory_recall(topic_key="sdd-<change_id>-proposal")`
2. Load context if needed: `memory_recall(topic_key="sdd-<change_id>-context")`
3. Write the spec document
4. Save to memory:
   - title: `SDD Spec: <change_id>`
   - topic_key: `sdd-<change_id>-spec`
   - type: `context`
   - content (structured):
     ```
     ## Goals
     <what this change achieves>

     ## Non-Goals
     <explicit exclusions — what this change does NOT do>

     ## Acceptance Criteria
     - [ ] <testable criterion 1>
     - [ ] <testable criterion 2>
     ...

     ## Constraints
     <technical, operational, backward-compatibility requirements>

     ## Out of Scope
     <related work deferred to a future change>
     ```

## Quality Bar

Every acceptance criterion must be testable — binary pass/fail, no judgment calls.