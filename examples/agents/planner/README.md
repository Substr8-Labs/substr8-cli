# Planner Agent

A workflow orchestrator that coordinates multi-agent tasks.

## Quick Start

```bash
# Copy this agent
cp -r examples/agents/planner ./my-planner

# Validate it
substr8 fdaa validate my-planner

# Push to TowerHQ (along with worker agents)
substr8 fdaa push my-planner --url https://towerhq.io --token YOUR_TOKEN
substr8 fdaa push examples/agents/research-agent --url https://towerhq.io --token YOUR_TOKEN
substr8 fdaa push examples/agents/writer --url https://towerhq.io --token YOUR_TOKEN
substr8 fdaa push examples/agents/reviewer --url https://towerhq.io --token YOUR_TOKEN
```

## Files

| File | Purpose |
|------|---------|
| `IDENTITY.md` | Agent identity, role as orchestrator |
| `SOUL.md` | Planning process, delegation rules |
| `TOOLS.md` | Spawn tool for delegation |
| `README.md` | This documentation |

## How It Works

```
User Request
    ↓
Planner analyzes task
    ↓
Planner decomposes into subtasks
    ↓
┌─────────────────────────────┐
│  Spawn: research-agent      │ → Research results
│  Spawn: writer              │ → Draft content
│  Spawn: reviewer            │ → Review feedback
└─────────────────────────────┘
    ↓
Planner synthesizes final result
    ↓
User receives output
```

## Workflow Lineage

Every spawn creates a child run:

```
planner (root, depth 0)
 ├── research-agent (depth 1)
 ├── writer (depth 1)
 └── reviewer (depth 1)
```

All runs are linked and verified via RunProof.

## What It Demonstrates

1. **Multi-agent orchestration** — Coordinating specialized agents
2. **Task decomposition** — Breaking complex work into subtasks
3. **Workflow lineage** — Parent-child run relationships
4. **Result synthesis** — Combining outputs into final deliverable

## Customization

- Edit `IDENTITY.md` to change spawnable agents
- Edit `SOUL.md` to change planning strategy
- Add more specialized workers as needed
