# Research Agent

A research assistant that uses web search to gather and synthesize information.

## Quick Start

```bash
# Copy this agent
cp -r examples/agents/research-agent ./my-researcher

# Validate it
substr8 fdaa validate my-researcher

# Chat with it
substr8 fdaa chat my-researcher

# Push to TowerHQ
substr8 fdaa push my-researcher --url https://towerhq.io --token YOUR_TOKEN
```

## Files

| File | Purpose |
|------|---------|
| `IDENTITY.md` | Agent identity and capabilities |
| `SOUL.md` | Behavior, process, output format |
| `TOOLS.md` | Available tools (web_search, web_fetch) |
| `README.md` | This documentation |

## Example Usage

```
You: Research the current state of autonomous vehicle regulations in the EU

Agent: ## Summary
The EU has been actively developing regulations for autonomous vehicles...

## Key Findings
- Finding 1 (Source: europa.eu)
- ...

## Sources
1. [EU Autonomous Vehicle Framework](https://europa.eu/...)
```

## What It Demonstrates

1. **Tool integration** — How to define tools in TOOLS.md
2. **Structured output** — Consistent response format
3. **Process-driven behavior** — Step-by-step research methodology

## Customization

- Edit `SOUL.md` to change the output format
- Edit `TOOLS.md` to add/remove available tools
- Edit `IDENTITY.md` to specialize for a domain (e.g., "Legal Research Agent")
