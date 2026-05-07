"""Autonomous content engine for Milestone 2."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Callable, TypedDict

from grid07_ai_agent.personas import DEFAULT_PERSONAS, BotPersona

try:
    from langchain_core.tools import tool
except ImportError:  # pragma: no cover - exercised when optional deps are absent

    def tool(func: Callable[..., str]) -> Callable[..., str]:
        """Fallback decorator with the same call shape used in tests."""

        return func


class ContentGraphState(TypedDict, total=False):
    """State passed through the content graph nodes."""

    bot: BotPersona
    topic: str
    search_query: str
    search_results: str
    post_content: str
    output: dict[str, str]


@dataclass(frozen=True)
class GeneratedPost:
    """Strict JSON-compatible content engine output."""

    bot_id: str
    topic: str
    post_content: str


@tool
def mock_searxng_search(query: str) -> str:
    """Return deterministic recent-news context for assignment demos."""

    normalized = query.lower()
    if "crypto" in normalized or "bitcoin" in normalized:
        return "Bitcoin hits new all-time high amid regulatory ETF approvals."
    if "ai" in normalized or "openai" in normalized or "developer" in normalized:
        return "OpenAI releases a faster coding model as companies rethink junior developer workflows."
    if "market" in normalized or "rates" in normalized or "fed" in normalized:
        return "Markets rally after the Fed signals interest-rate cuts may arrive sooner than expected."
    if "privacy" in normalized or "social" in normalized:
        return "New privacy report warns social platforms are expanding AI-driven user profiling."
    return "Technology leaders debate whether automation is creating more leverage or more social risk."


def find_persona(bot_id: str) -> BotPersona:
    """Find a default persona by bot id."""

    for persona in DEFAULT_PERSONAS:
        if persona.bot_id == bot_id:
            return persona
    raise ValueError(f"Unknown bot_id: {bot_id}")


def decide_search(state: ContentGraphState) -> ContentGraphState:
    """Choose a topic and search query from the bot persona."""

    bot = state["bot"]
    if bot.bot_id == "bot_a":
        topic = "AI coding acceleration"
        query = "OpenAI AI developer productivity latest news"
    elif bot.bot_id == "bot_b":
        topic = "AI labor displacement and tech monopoly power"
        query = "AI replacing junior developers monopoly privacy latest news"
    else:
        topic = "Fed rates and market ROI"
        query = "Fed interest rates markets trading ROI latest news"

    return {**state, "topic": topic, "search_query": query}


def run_web_search(state: ContentGraphState) -> ContentGraphState:
    """Execute the mock search tool."""

    search_callable = getattr(mock_searxng_search, "invoke", mock_searxng_search)
    result = search_callable(state["search_query"])
    return {**state, "search_results": str(result)}


def draft_post(state: ContentGraphState) -> ContentGraphState:
    """Draft a persona-specific 280-character post from search context."""

    bot = state["bot"]
    context = state["search_results"]

    if bot.bot_id == "bot_a":
        post = (
            "OpenAI shipping faster coding models is exactly the compounding curve. "
            "Junior dev workflows will evolve, not vanish. More leverage, more builders, more future."
        )
    elif bot.bot_id == "bot_b":
        post = (
            "The AI coding headline is not magic, it is labor leverage for monopolies. "
            "Ask who owns the model, who loses bargaining power, and who gets surveilled."
        )
    else:
        post = (
            "Fed cut signals plus automation hype is a classic multiple-expansion setup. "
            "Follow rates, liquidity, and ROI. Narrative is cute; cash flow clears."
        )

    if len(post) > 280:
        post = post[:277].rstrip() + "..."

    generated = GeneratedPost(
        bot_id=bot.bot_id,
        topic=state["topic"],
        post_content=f"{post} Context: {context}"[:280],
    )
    return {**state, "post_content": generated.post_content, "output": asdict(generated)}


class LocalContentGraph:
    """Small sequential graph runner used when LangGraph is unavailable."""

    def invoke(self, initial_state: ContentGraphState) -> ContentGraphState:
        state = decide_search(initial_state)
        state = run_web_search(state)
        return draft_post(state)


def build_content_graph() -> Any:
    """Build the content graph, using LangGraph when it is installed."""

    try:
        from langgraph.graph import END, StateGraph
    except ImportError:
        return LocalContentGraph()

    graph = StateGraph(ContentGraphState)
    graph.add_node("decide_search", decide_search)
    graph.add_node("web_search", run_web_search)
    graph.add_node("draft_post", draft_post)
    graph.set_entry_point("decide_search")
    graph.add_edge("decide_search", "web_search")
    graph.add_edge("web_search", "draft_post")
    graph.add_edge("draft_post", END)
    return graph.compile()


def generate_opinionated_post(bot_id: str) -> dict[str, str]:
    """Run the content engine and return strict assignment JSON."""

    graph = build_content_graph()
    result = graph.invoke({"bot": find_persona(bot_id)})
    output = result["output"]
    _validate_generated_post(output)
    return output


def generate_opinionated_post_json(bot_id: str) -> str:
    """Return the generated post as strict JSON text."""

    return json.dumps(generate_opinionated_post(bot_id), indent=2)


def _validate_generated_post(output: dict[str, str]) -> None:
    required_keys = {"bot_id", "topic", "post_content"}
    if set(output) != required_keys:
        raise ValueError(f"Generated post must contain exactly {sorted(required_keys)}")
    if len(output["post_content"]) > 280:
        raise ValueError("Generated post exceeds 280 characters")
    for key in required_keys:
        if not isinstance(output[key], str) or not output[key].strip():
            raise ValueError(f"Generated post field is empty: {key}")

