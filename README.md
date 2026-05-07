# Grid07 Cognitive Routing & RAG Agent

This repository implements the AI Intern Assignment for Grid07: a small AI agent system that routes posts to interested bot personas, generates opinionated posts through a LangGraph workflow, and defends a bot's position in deep comment threads with RAG-style context and prompt-injection guardrails.

## Assignment Scope

Phase 1 is complete in Milestone 1:

- Store Bot A, Bot B, and Bot C personas in an in-memory vector index.
- Embed incoming post content.
- Return only bots whose cosine similarity clears the routing threshold.

Future milestones will add:

- Production LLM provider wiring for real hosted or local model calls.

## Setup

WSL / Ubuntu:

```bash
cd /mnt/d/AI_Agents/1rag_ai_agent
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
```

Run install commands from the repository root, not from `src`. LLM provider keys are intentionally excluded; copy `.env.example` to `.env` when later milestones require them.

## Run Phase 1

```powershell
python -m grid07_ai_agent.cli route "OpenAI just released a new model that might replace junior developers." --threshold 0.35
```

The CLI prints strict JSON with the matched bots and similarity scores. The assignment API keeps `threshold=0.85` as its default, but the deterministic prototype embedding is intentionally demonstrated with `0.35` to produce realistic local routing until a production embedding model is introduced.

## Run Phase 2

```powershell
python -m grid07_ai_agent.cli generate-post bot_b
```

The content engine has three nodes: `Decide Search`, `Web Search`, and `Draft Post`. It uses LangGraph when installed; otherwise it runs the same nodes through a local sequential graph runner so tests and demos remain deterministic.

## Run Phase 3

```powershell
python -m grid07_ai_agent.cli defend-thread bot_a
```

The defense workflow builds a RAG-style prompt with the parent post, comment history, and latest human reply. User-controlled thread text is treated as untrusted data, so prompt-injection attempts are rejected while the bot stays in persona.

## Check Config

```bash
python3 -m grid07_ai_agent.cli config-check
```

To enable a hosted model later, copy `.env.example` to `.env`, set `LLM_PROVIDER`, and add the matching API key manually. The config check only prints whether keys are present; it never prints secret values.

## Test

```powershell
python -m unittest discover -s tests
```

## Engineering Decisions

- The initial vector store is an in-memory Python implementation backed by normalized `numpy` vectors. This keeps the prototype inspectable and avoids external database setup.
- The embedding model is deterministic and local for Milestone 1. It uses a small domain-weighted vocabulary for the assignment personas, which gives stable tests and a clear upgrade path to OpenAI, Ollama, Groq, ChromaDB, FAISS, or pgvector.
- Public APIs are kept narrow: `route_post_to_bots(post_content: str, threshold: float = 0.85)` is the main assignment function.
- Phase 2 exposes `generate_opinionated_post(bot_id: str)` and validates the required JSON keys: `bot_id`, `topic`, and `post_content`.
- Phase 3 exposes `generate_defense_reply(...)` and `build_defense_prompt(...)` for future LLM-backed replies.
- Runtime config is loaded from `.env` when available and can be inspected with `config-check` without exposing secrets.
- Tests use Python `unittest` so the first milestone can run without installing a test framework.

## Milestone Status

See [docs/engineering.md](docs/engineering.md) for user stories, requirements, technology decisions, and milestone plan.
