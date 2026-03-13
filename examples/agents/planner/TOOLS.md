# Tools

## spawn

Delegate a task to another agent.

**When to use:** When a subtask is better handled by a specialized agent.

**Parameters:**
- `agent` (string, required): Agent slug to spawn
- `task` (string, required): Task description for the agent
- `wait` (boolean, optional): Wait for completion (default: true)

**Example:**
```json
{
  "tool": "spawn",
  "agent": "research-agent",
  "task": "Research current AI governance frameworks",
  "wait": true
}
```

**Returns:**
```json
{
  "run_id": "run_abc123",
  "status": "completed",
  "output": "... agent's response ..."
}
```

## Available Agents

| Agent | Purpose |
|-------|---------|
| `research-agent` | Web search and information synthesis |
| `writer` | Content creation and drafting |
| `reviewer` | Quality review and feedback |

## Notes

- Spawned agents inherit your workflow context
- Each spawn creates a child run in the lineage tree
- Results are verified via RunProof
- Keep spawns focused — one clear task per agent
