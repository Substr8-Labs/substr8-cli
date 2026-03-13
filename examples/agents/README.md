# Example Agents

Pre-built FDAA agents to learn from and customize.

## Available Agents

| Agent | Purpose | Complexity |
|-------|---------|------------|
| [hello-world](./hello-world/) | Simplest possible agent | ⭐ |
| [research-agent](./research-agent/) | Web search and synthesis | ⭐⭐ |
| [writer](./writer/) | Content creation | ⭐⭐ |
| [reviewer](./reviewer/) | Quality validation | ⭐⭐ |
| [planner](./planner/) | Multi-agent orchestration | ⭐⭐⭐ |

## Quick Start

```bash
# 1. Copy an agent
cp -r examples/agents/hello-world ./my-agent

# 2. Customize it
# Edit IDENTITY.md and SOUL.md

# 3. Validate
substr8 fdaa validate my-agent

# 4. Test locally
substr8 fdaa chat my-agent

# 5. Push to TowerHQ
substr8 fdaa push my-agent --url https://towerhq.io --token YOUR_TOKEN
```

## Agent Structure

Every FDAA agent needs at minimum:

```
my-agent/
├── IDENTITY.md   # Who the agent is (required)
└── SOUL.md       # How it behaves (required)
```

Optional files:
- `TOOLS.md` — Available tools
- `MEMORY.md` — Persistent notes
- `MODEL.md` — Model preferences
- `POLICY.md` — Constraints and rules

## Learning Path

1. **Start with hello-world** — Understand the basics
2. **Try research-agent** — Learn tool integration
3. **Use planner** — Explore multi-agent workflows

## Multi-Agent Workflow

The planner agent coordinates other agents:

```
planner (orchestrator)
 ├── research-agent (gathers info)
 ├── writer (creates content)
 └── reviewer (validates quality)
```

To set up the full workflow:

```bash
# Push all agents
for agent in planner research-agent writer reviewer; do
  substr8 fdaa push examples/agents/$agent --url https://towerhq.io --token YOUR_TOKEN
done
```

Then run the planner from TowerHQ with a complex task.
