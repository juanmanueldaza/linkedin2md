---
name: sdd-tasks
description: "Break the technical design into an ordered list of atomic, reviewable implementation tasks."
compatibility: opencode
when_to_use: "After sdd-design. Reads design + spec from memory, produces a task list."
allowed-tools:
  - Read
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_save
model: low
effort: low
user-invocable: false
---

## Goal

Decompose the design into the smallest independent tasks that can each be implemented and
reviewed in a single focused session.

## Steps

1. Load design: `memory_recall(topic_key="sdd-<change_id>-design")`
2. Load spec: `memory_recall(topic_key="sdd-<change_id>-spec")`
3. Break work into atomic tasks — each task touches one area and can be verified independently
4. Order tasks so earlier tasks unblock later ones
5. Save to memory:
   - title: `SDD Tasks: <change_id>`
   - topic_key: `sdd-<change_id>-tasks`
   - type: `context`
   - content (structured):
     ```
     ## Task List

     ### T1: <title>
     Files: <file paths>
     What: <what to change>
     Done when: <acceptance condition>

     ### T2: <title>
     Files: <file paths>
     What: <what to change>
     Done when: <acceptance condition>

     ...

     ## Order Rationale
     <why tasks are sequenced this way>
     ```

## Quality Bar

- Each task is independently reviewable (no "and also" tasks)
- Every spec acceptance criterion is covered by at least one task
- "Done when" conditions are testable