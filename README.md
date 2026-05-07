# Grid07 Cognitive Routing & RAG Agent

This repository implements the AI Intern Assignment for Grid07: a small AI agent system that routes posts to interested bot personas, generates opinionated posts through a LangGraph workflow, and defends a bot's position in deep comment threads with RAG-style context and prompt-injection guardrails.

## Assignment Scope

Phase 1 is complete in Milestone 1:

- Store Bot A, Bot B, and Bot C personas in an in-memory vector index.
- Embed incoming post content.
- Return only bots whose cosine similarity clears the routing threshold.

Future milestones will add:

- A LangGraph content engine with `Decide Search`, `Web Search`, and `Draft Post` nodes.
- Strict JSON output for generated posts.
- Deep-thread defense replies that preserve persona behavior despite prompt-injection attempts.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

For Milestone 1 only, `numpy` is the only runtime dependency. LLM provider keys are intentionally excluded; copy `.env.example` to `.env` when later milestones require them.

## Run Phase 1

```powershell
python -m grid07_ai_agent.cli route "OpenAI just released a new model that might replace junior developers." --threshold 0.35
```

The CLI prints strict JSON with the matched bots and similarity scores. The assignment API keeps `threshold=0.85` as its default, but the deterministic prototype embedding is intentionally demonstrated with `0.35` to produce realistic local routing until a production embedding model is introduced.

## Test

```powershell
python -m unittest discover -s tests
```

## Engineering Decisions

- The initial vector store is an in-memory Python implementation backed by normalized `numpy` vectors. This keeps the prototype inspectable and avoids external database setup.
- The embedding model is deterministic and local for Milestone 1. It uses a small domain-weighted vocabulary for the assignment personas, which gives stable tests and a clear upgrade path to OpenAI, Ollama, Groq, ChromaDB, FAISS, or pgvector.
- Public APIs are kept narrow: `route_post_to_bots(post_content: str, threshold: float = 0.85)` is the main assignment function.
- Tests use Python `unittest` so the first milestone can run without installing a test framework.

## Milestone Status

See [docs/engineering.md](docs/engineering.md) for user stories, requirements, technology decisions, and milestone plan.
