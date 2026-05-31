---
name: sdd-propose
description: "Propose 2–3 solution approaches for a planned change, evaluating trade-offs and recommending one."
compatibility: opencode
when_to_use: "After sdd-explore completes. Reads context from memory, proposes approaches."
allowed-tools:
  - Read
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_search
  - mcp__n3rv-memory__memory_save
model: medium
effort: medium
user-invocable: false
---

## Goal

Generate 2–3 concrete approaches to the planned change, evaluate trade-offs, and commit to one recommendation.

## Steps

1. Load context: `memory_recall(topic_key="sdd-<change_id>-context")`
2. Generate 2–3 distinct approaches — include the obvious path and at least one alternative
3. For each approach evaluate: implementation complexity, reversibility, blast radius, testability
4. Select the recommended approach with a clear rationale
5. Save to memory:
   - title: `SDD Proposal: <change_id>`
   - topic_key: `sdd-<change_id>-proposal`
   - type: `decision`
   - content (structured):
     ```
     ## Approach A: <name>
     <description, pros, cons>

     ## Approach B: <name>
     <description, pros, cons>

     ## Approach C: <name> (if applicable)
     <description, pros, cons>

     ## Recommended: <Approach X>
     <rationale — why this one, why not the others>
     ```

## Constraints

- No implementation code in this phase
- Each approach must be genuinely distinct (not variations of the same idea)
- The recommendation must be unambiguous — one winner