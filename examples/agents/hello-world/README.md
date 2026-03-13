# Hello World Agent

The simplest FDAA agent — perfect for learning the basics.

## Quick Start

```bash
# Copy this agent
cp -r examples/agents/hello-world ./my-agent

# Validate it
substr8 fdaa validate my-agent

# Chat with it (requires OPENAI_API_KEY or ANTHROPIC_API_KEY)
substr8 fdaa chat my-agent

# Push to TowerHQ
substr8 fdaa push my-agent --url https://towerhq.io --token YOUR_TOKEN
```

## Files

| File | Purpose |
|------|---------|
| `IDENTITY.md` | Who the agent is |
| `SOUL.md` | How the agent behaves |
| `README.md` | This documentation |

## What It Demonstrates

1. **Minimal structure** — Only IDENTITY.md and SOUL.md are required
2. **Clear identity** — Name, slug, version, purpose
3. **Behavioral instructions** — How to respond, examples, constraints

## Next Steps

Once you understand this agent, check out:
- `research-agent` — Uses web search tools
- `planner` — Orchestrates multiple agents
