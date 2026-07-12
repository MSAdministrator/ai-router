# ai-router

`ai-router` is a Python CLI that routes local prompts to available Ollama models using simple scoring heuristics.

## Highlights

- Local-first model routing
- Capability-based scoring
- Repo-aware context detection via `git diff`
- CLI commands for chat, model inspection, and diagnostics

## Quick Start

```bash
uv pip install -e .
ai-router chat "implement auth middleware"
```
