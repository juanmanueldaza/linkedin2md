---
description: Create an agent handoff document
agent: n3rv
subtask: true
---
Create a handoff document for: $ARGUMENTS

Include:
1. What was accomplished
2. Current state
3. Known issues / blockers
4. Next steps
5. Relevant files

Save to memory for future session context: `memory_save(type="context", title="Handoff: $ARGUMENTS", ...)`