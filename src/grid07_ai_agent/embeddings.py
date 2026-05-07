"""Deterministic local embeddings for the Milestone 1 router."""

from __future__ import annotations

import math
import re
from collections.abc import Iterable

import numpy as np


FEATURES: tuple[str, ...] = (
    "ai_technology",
    "crypto",
    "optimism",
    "space",
    "regulation",
    "capitalism",
    "monopoly",
    "skepticism",
    "privacy",
    "nature",
    "finance",
    "trading",
    "interest_rates",
    "roi",
    "social_media",
    "billionaires",
    "labor_impact",
)


KEYWORD_WEIGHTS: dict[str, tuple[tuple[str, float], ...]] = {
    "ai": (("ai_technology", 4.0),),
    "artificial": (("ai_technology", 3.0),),
    "intelligence": (("ai_technology", 3.0),),
    "openai": (("ai_technology", 5.0),),
    "model": (("ai_technology", 2.0),),
    "llm": (("ai_technology", 4.0),),
    "developer": (("ai_technology", 2.0), ("labor_impact", 2.0)),
    "developers": (("ai_technology", 2.0), ("labor_impact", 2.0)),
    "automation": (("ai_technology", 2.0), ("labor_impact", 2.0)),
    "replace": (("labor_impact", 3.0),),
    "jobs": (("labor_impact", 3.0),),
    "crypto": (("crypto", 5.0),),
    "bitcoin": (("crypto", 5.0), ("finance", 2.0)),
    "ethereum": (("crypto", 5.0), ("finance", 2.0)),
    "optimistic": (("optimism", 4.0),),
    "solve": (("optimism", 2.0),),
    "technology": (("ai_technology", 3.0), ("optimism", 1.0)),
    "elon": (("ai_technology", 1.0), ("space", 2.0), ("billionaires", 2.0)),
    "musk": (("ai_technology", 1.0), ("space", 2.0), ("billionaires", 2.0)),
    "space": (("space", 5.0),),
    "mars": (("space", 5.0),),
    "regulation": (("regulation", 4.0),),
    "regulatory": (("regulation", 4.0),),
    "capitalism": (("capitalism", 5.0), ("labor_impact", 2.0)),
    "monopolies": (("monopoly", 5.0),),
    "monopoly": (("monopoly", 5.0),),
    "critical": (("skepticism", 4.0),),
    "skeptic": (("skepticism", 4.0),),
    "skeptical": (("skepticism", 4.0),),
    "destroying": (("skepticism", 3.0), ("labor_impact", 3.0)),
    "scam": (("skepticism", 3.0),),
    "privacy": (("privacy", 5.0),),
    "surveillance": (("privacy", 4.0),),
    "nature": (("nature", 5.0),),
    "climate": (("nature", 3.0),),
    "social": (("social_media", 3.0),),
    "media": (("social_media", 3.0),),
    "billionaires": (("billionaires", 5.0),),
    "billionaire": (("billionaires", 5.0),),
    "markets": (("finance", 5.0),),
    "market": (("finance", 5.0),),
    "rates": (("interest_rates", 5.0),),
    "interest": (("interest_rates", 5.0),),
    "fed": (("interest_rates", 4.0), ("finance", 2.0)),
    "trading": (("trading", 5.0),),
    "algorithm": (("trading", 4.0),),
    "algorithms": (("trading", 4.0),),
    "money": (("finance", 3.0), ("roi", 2.0)),
    "roi": (("roi", 5.0),),
    "profit": (("finance", 2.0), ("roi", 3.0)),
    "etf": (("finance", 3.0), ("crypto", 2.0)),
}


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class DomainEmbeddingModel:
    """Small weighted concept embedder for deterministic prototype routing."""

    def __init__(self, features: Iterable[str] = FEATURES) -> None:
        self.features = tuple(features)
        self._index = {feature: position for position, feature in enumerate(self.features)}

    def embed(self, text: str) -> np.ndarray:
        vector = np.zeros(len(self.features), dtype=float)
        for token in TOKEN_PATTERN.findall(text.lower()):
            for feature, weight in KEYWORD_WEIGHTS.get(token, ()):
                vector[self._index[feature]] += weight

        norm = np.linalg.norm(vector)
        if math.isclose(norm, 0.0):
            return vector
        return vector / norm


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    """Return cosine similarity for normalized or unnormalized vectors."""

    left_norm = np.linalg.norm(left)
    right_norm = np.linalg.norm(right)
    if math.isclose(left_norm, 0.0) or math.isclose(right_norm, 0.0):
        return 0.0
    return float(np.dot(left, right) / (left_norm * right_norm))
