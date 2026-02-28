"""
llm/parser.py – Pydantic models for structured LLM output generation and parsing.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class LLMRecommendationOut(BaseModel):
    """
    A single restaurant recommendation returned by the LLM.

    The LLM is instructed to return an array of these objects via Gemini's
    response_schema functionality.
    """

    restaurant_id: str = Field(
        description="The exact 'id' string from the provided candidate list."
    )
    explanation: str = Field(
        description="A 1-3 sentence explanation of why this restaurant fits the user's specific context."
    )
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="The LLM's confidence score (0.0 to 1.0) for this recommendation based on the context.",
    )


class LLMResponseEnvelope(BaseModel):
    """
    Root schema for the LLM output.

    We use an envelope object to make the JSON structure strictly deterministic
    for the Gemini generation config.
    """

    recommendations: List[LLMRecommendationOut] = Field(
        description="List of re-ranked and explained recommendations."
    )
