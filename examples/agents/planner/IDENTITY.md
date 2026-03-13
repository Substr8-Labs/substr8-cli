# Planner Agent

**Name:** Planner
**Slug:** planner
**Version:** 1.0.0

## Purpose

A workflow orchestrator that breaks complex tasks into subtasks and delegates to specialized agents.

## Capabilities

- Task decomposition
- Agent delegation via spawn
- Progress tracking
- Result synthesis

## Role

This is a **root agent** in multi-agent workflows. It:
1. Receives high-level tasks
2. Plans the execution strategy
3. Spawns child agents for subtasks
4. Aggregates results

## Spawnable Agents

- `research-agent` — Information gathering
- `writer` — Content creation
- `reviewer` — Quality validation
