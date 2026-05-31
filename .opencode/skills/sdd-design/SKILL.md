---
name: sdd-design
description: "Write the technical design for a planned change: components, interfaces, data flows, edge cases."
compatibility: opencode
when_to_use: "After sdd-spec. Reads spec and proposal from memory, produces a technical design."
allowed-tools:
  - Read
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_save
model: medium
effort: medium
user-invocable: false
---

## Goal

Produce a technical design that tells an implementer *how* to build what the spec describes.
Bridge between the spec's *what* and the code's *how*.

## Steps

1. Load spec: `memory_recall(topic_key="sdd-<change_id>-spec")`
2. Load proposal: `memory_recall(topic_key="sdd-<change_id>-proposal")`
3. Read relevant source files to ground the design in the existing codebase
4. Write the technical design
5. Save to memory:
   - title: `SDD Design: <change_id>`
   - topic_key: `sdd-<change_id>-design`
   - type: `architecture`
   - content (structured):
     ```
     ## Components
     <new or modified modules, classes, functions>

     ## Interfaces
     <public API changes, function signatures, data models>

     ## Data Flow
     <how data moves through the system for this change>

     ## Error Handling
     <failure modes and how they are handled>

     ## Edge Cases
     <boundary conditions, concurrency, empty input, large input>

     ## Dependencies
     <new packages, external services, migration requirements>

     ## Testing Strategy
     <unit tests needed, integration tests, fixtures>
     ```

## Constraints

- Design must be traceable to spec acceptance criteria
- No code snippets beyond signatures/pseudocode — the implementer fills in the bodies