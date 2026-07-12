# ai-router

ai-router is a python cli tool to route local models based on your local system specifications. Underneath, ai-router uses Ollama and scores/ranks installed models against prompt-derived features, then runs the prompt with the highest-ranked model.

## What It Does Today

- Loads model definitions from `src/config/models.yaml`
- Detects installed Ollama models via `ollama list`
- Builds request features from:
	- prompt token count (`len(prompt.split())`)
	- whether `git diff` is non-empty
	- simple keyword-based capability inference
- Selects one model using capability/context/priority scoring
- Streams generation output from `ollama run <model>`

## Requirements

- Python
- Ollama CLI available on PATH

If Ollama is missing, ai-router attempts to install it automatically using the official installer script on macOS/Linux.

## Install

```bash
uv pip install -e .
```

Entry point:

```bash
ai-router
```

## CLI Commands

### Chat

Route a prompt to the best available configured model and stream output.

```bash
ai-router chat "implement a CQRS system"
ai-router chat "review this diff" --verbose
```

Options:

- `--verbose`: prints selected model name before streaming

### Models

Show installed Ollama models.

```bash
ai-router models
```

### Install Models

Pull all models declared in `src/config/models.yaml`.

```bash
ai-router install_models
```

### Explain

Show routing features and selected model without running generation.

```bash
ai-router explain "refactor auth system"
```

### Doctor

Basic environment report (currently installed Ollama models).

```bash
ai-router doctor
```

## Routing Logic

Current capability inference in prompts is keyword-based:

- `security` -> `security`
- `refactor` -> `architecture`
- `implement` -> `coding`
- non-empty `git diff` -> `repository`

Model scoring currently adds:

- `+30` per matching inferred capability
- `+25` if request is repo-aware and model has `repository`
- `+20` if prompt token count is greater than half the model `max_context`
- `+priority` from model config

The highest score wins.

## Model Configuration

Configured models live in:

- `src/config/models.yaml`

Schema:

```yaml
models:
	key:
		name: <ollama-model-name>
		provider: ollama
		capabilities: [cap1, cap2]
		max_context: 32768
		priority: 90
```

Only models that are both:

- present in this config, and
- currently installed in Ollama

are considered for routing.

## Notes And Limitations

- Capability inference is case-sensitive and rule-based.
- `ai-router doctor` is intentionally minimal right now.
- If no configured model is installed, chat reports no available model.
- A root-level `config/` directory is not used by the current loader; runtime config is read from `src/config/models.yaml`.
