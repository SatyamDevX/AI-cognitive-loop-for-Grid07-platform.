# Engineering Plan

## Assignment Understanding

The Grid07 AI assignment asks for the core cognitive loop of a bot platform:

1. Route new posts only to bot personas that care about the topic.
2. Let bots create original posts through a LangGraph workflow that searches for current context before drafting.
3. Let bots reply inside deep human threads using full argument context while resisting prompt injection.

## User Stories

- As a platform operator, I want posts routed by persona relevance so that bots only engage when their interests match the topic.
- As a bot persona, I want my profile embedded and searchable so that I can be selected through semantic similarity instead of manual keyword rules.
- As a content bot, I want to research a topic before posting so that generated posts reference plausible real-world context.
- As a platform operator, I want generated posts returned as strict JSON so downstream services can parse them safely.
- As a debating bot, I want the full parent post and comment history in my reply prompt so I can answer the actual argument.
- As a platform operator, I want prompt-injection defenses so a hostile user cannot override the bot persona or system instructions.
- As an engineer, I want reproducible tests and execution logs so each assignment phase can be reviewed independently.

## Functional Requirements

- Provide three default personas: Tech Maximalist, Doomer / Skeptic, and Finance Bro.
- Implement `route_post_to_bots(post_content: str, threshold: float = 0.85)`.
- Store persona embeddings in an in-memory vector store for the prototype.
- Use cosine similarity for routing decisions.
- Provide a mock `mock_searxng_search(query: str)` tool in the content milestone.
- Build a LangGraph state machine with `Decide Search`, `Web Search`, and `Draft Post` nodes.
- Enforce generated post output as `{"bot_id": "...", "topic": "...", "post_content": "..."}`.
- Implement `generate_defense_reply(bot_persona, parent_post, comment_history, human_reply)`.
- Include prompt-injection resistant system instructions in the defense workflow.
- Provide execution logs for all three phases.

## Non-Functional Requirements

- Keep secrets out of Git and provide `.env.example`.
- Keep code typed, modular, and testable.
- Prefer deterministic behavior in tests.
- Keep milestone commits focused and descriptive.
- Update README and documentation after each milestone.
- Validate code before every commit.

## Technology Decisions

- Language: Python, matching the assignment and AI tooling ecosystem.
- Milestone 1 vector layer: local in-memory `numpy` vector index for a fast prototype.
- Future vector store options: ChromaDB or FAISS locally; pgvector for production parity.
- Future orchestration: LangGraph.
- Future LLM providers: Ollama for local runs, Groq or OpenAI for hosted model access.
- Testing: Python `unittest` for Milestone 1; pytest can be introduced when dependency installation is part of the workflow.
- Packaging: `src/` layout to avoid accidental imports from the project root.

## Milestones

### Milestone 1: Foundation + Persona Router

Deliverables:

- Git repository initialized with a milestone branch.
- `src/` project structure.
- Deterministic in-memory vector store.
- Default personas and `route_post_to_bots`.
- CLI demo for Phase 1.
- Unit tests for topic routing and threshold behavior.
- README, engineering plan, and execution log.

Validation:

- Run `python -m unittest discover -s tests`.
- Run CLI examples and record output in `docs/execution_logs.md`.

### Milestone 2: LangGraph Content Engine Prototype

Deliverables:

- `mock_searxng_search(query: str)` tool.
- LangGraph nodes for deciding search, web search, and drafting.
- Strict JSON output schema.
- Tests using fake or deterministic LLM responses.
- README and execution log updates.

Validation:

- Unit tests for graph state transitions.
- CLI demo showing valid JSON.

Status: complete. The implementation uses LangGraph when installed and a local sequential runner when optional LangGraph dependencies are not available in the current environment.

### Milestone 3: Deep Thread RAG + Injection Defense

Deliverables:

- Thread context data model.
- `generate_defense_reply` implementation.
- Prompt template with system-level persona preservation and injection handling.
- Tests covering normal replies and injection attempts.
- Execution log showing defense against the provided attack string.

Validation:

- Unit tests for prompt assembly and guarded behavior.
- CLI demo for the provided EV battery scenario.

### Milestone 4: Production Hardening

Deliverables:

- Configurable LLM provider.
- Optional ChromaDB or FAISS adapter.
- Structured logging and error handling.
- Expanded test coverage.
- Setup and operations documentation.

Validation:

- Full test suite.
- Manual end-to-end smoke run across all phases.

## Milestone 1 Notes

The first milestone intentionally avoids network calls and paid APIs. Its embedding model is not a replacement for production embeddings; it is a deterministic prototype that preserves the assignment's cosine-similarity contract and can be swapped behind the same router interface. The assignment function keeps `threshold=0.85`, while local demos use `0.35` because the prototype concept vectors are sparse compared with production sentence embeddings.
