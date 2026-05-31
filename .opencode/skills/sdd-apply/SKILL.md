---
name: sdd-apply
description: "Implement the SDD task list. Read tasks and design from memory, write code, run tests."
compatibility: opencode
when_to_use: "After sdd-tasks. Reads tasks, spec, and design from memory, implements each task in order."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_save
model: high
effort: high
user-invocable: false
hub-skill-ids: [implementation, plan-execution]
---

## Goal

Implement all tasks from the task list, in order, verifying each one before moving to the next.

## Steps

1. Load tasks: `memory_recall(topic_key="sdd-<change_id>-tasks")`
2. Load design: `memory_recall(topic_key="sdd-<change_id>-design")`
3. Load spec: `memory_recall(topic_key="sdd-<change_id>-spec")`
4. For each task:
   a. Implement the change in the specified files
   b. Run the project test suite — fix failures before moving on
   c. Verify the task's "Done when" condition is met
5. After all tasks complete, save implementation notes to memory:
   - title: `SDD Apply: <change_id>`
   - topic_key: `sdd-<change_id>-impl`
   - type: `context`
   - content: summary of what was changed, any deviations from the design, and test results

## Rules

- Do not add features beyond the task list — stay in scope
- Run tests after every task, not just at the end
- If a task conflicts with the design, note the deviation in the impl summary — do not silently deviate
- Keep commits atomic: one task per commit