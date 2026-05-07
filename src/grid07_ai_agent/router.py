"""Persona routing using an in-memory vector index."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from grid07_ai_agent.embeddings import DomainEmbeddingModel, cosine_similarity
from grid07_ai_agent.personas import DEFAULT_PERSONAS, BotPersona


@dataclass(frozen=True)
class RouteMatch:
    """A routed bot and its similarity score."""

    bot_id: str
    name: str
    similarity: float


class InMemoryVectorStore:
    """Minimal vector store that supports cosine search over bot personas."""

    def __init__(self, embedding_model: DomainEmbeddingModel) -> None:
        self.embedding_model = embedding_model
        self._records: list[tuple[BotPersona, np.ndarray]] = []

    def add_persona(self, persona: BotPersona) -> None:
        self._records.append((persona, self.embedding_model.embed(persona.description)))

    def search(self, text: str, threshold: float) -> list[RouteMatch]:
        query_vector = self.embedding_model.embed(text)
        matches = [
            RouteMatch(
                bot_id=persona.bot_id,
                name=persona.name,
                similarity=cosine_similarity(query_vector, persona_vector),
            )
            for persona, persona_vector in self._records
        ]
        return sorted(
            (match for match in matches if match.similarity > threshold),
            key=lambda match: match.similarity,
            reverse=True,
        )


def build_default_vector_store() -> InMemoryVectorStore:
    """Create the assignment's default in-memory persona index."""

    store = InMemoryVectorStore(DomainEmbeddingModel())
    for persona in DEFAULT_PERSONAS:
        store.add_persona(persona)
    return store


def route_post_to_bots(post_content: str, threshold: float = 0.85) -> list[dict[str, object]]:
    """Route a post to bots whose persona similarity is above the threshold."""

    store = build_default_vector_store()
    return [
        {
            "bot_id": match.bot_id,
            "name": match.name,
            "similarity": round(match.similarity, 4),
        }
        for match in store.search(post_content, threshold)
    ]

