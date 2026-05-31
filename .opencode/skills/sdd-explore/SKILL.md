---
name: sdd-explore
description: "Explore the codebase to build context for a planned change. First phase of the SDD workflow."
compatibility: opencode
when_to_use: "At the start of an SDD workflow, before proposing any solution. Read-only investigation."
allowed-tools:
  - Read
  - Glob
  - Grep
  - mcp__n3rv-memory__memory_search
  - mcp__n3rv-memory__memory_recall
  - mcp__n3rv-memory__memory_save
model: low
effort: low
user-invocable: false
---

## Goal

Understand the current state of the codebase as it relates to the requested change.
Do NOT propose solutions — only observe and report.

## Steps

1. Search memory for prior context on this topic:
   `memory_search(query="<change description>")`
2. Identify which files, modules, and directories are relevant to this change
3. Read the most relevant files — focus on interfaces, not implementation details
4. Note: existing patterns, naming conventions, dependencies, test coverage, edge cases, known risks
5. Save findings to memory:
   - title: `SDD Explore: <change_id>`
   - topic_key: `sdd-<change_id>-context`
   - type: `context`
   - content (structured):
     ```
     ## Relevant Files
     <file paths and their role>

     ## Key Patterns
     <naming, structure, conventions observed>

     ## Dependencies
     <what this change depends on or affects>

     ## Test Coverage
     <existing tests relevant to this change>

     ## Risks
     <potential pitfalls, breaking changes>
     ```

## Output

A structured context document saved to memory. Write no source code.