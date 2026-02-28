"""
api/schemas.py – Pydantic request/response schemas for the recommendation API.
Uses Pydantic V2 style.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    """Query parameters that drive the recommendation pipeline."""

    cities: Optional[List[str]] = Field(
        default=None,
        description="List of cities to search in (e.g. ['Bangalore', 'Mumbai']).",
        json_schema_extra={"example": ["Bangalore"]},
    )
    cuisines: Optional[List[str]] = Field(
        default=None,
        description="List of cuisine types; any-match (e.g. ['North Indian', 'Thai']).",
        json_schema_extra={"example": ["North Indian"]},
    )
    min_rating: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=5.0,
        description="Minimum accepted restaurant rating (0.0–5.0).",
        json_schema_extra={"example": 4.0},
    )
    max_price_bucket: Optional[int] = Field(
        default=None,
        ge=1,
        le=4,
        description=(
            "Maximum price bucket (1=budget ≤₹500, 2=mid ≤₹1000, "
            "3=upscale ≤₹2000, 4=premium >₹2000)."
        ),
        json_schema_extra={"example": 3},
    )
    top_n: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of recommendations to return.",
        json_schema_extra={"example": 5},
    )
    model_name: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model to use for re-ranking.",
        json_schema_extra={"example": "gemini-1.5-pro"},
    )

    @field_validator("cuisines", "cities", mode="before")
    @classmethod
    def _normalise_list(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            # Accept a single comma-separated string for convenience.
            return [c.strip() for c in v.split(",") if c.strip()]
        return v


class RestaurantOut(BaseModel):
    """Serialisable view of a restaurant returned by the API."""

    id: str
    name: str
    city: Optional[str] = None
    area: Optional[str] = None
    cuisines: List[str]
    price_range: Optional[int] = None
    rating: Optional[float] = None
    votes: Optional[int] = None
    score: Optional[float] = Field(
        default=None,
        description="Composite relevance score (0.0–1.0). Higher is better.",
    )
    explanation: Optional[str] = Field(
        default=None,
        description="LLM-generated reasoning tailored to the user's specific context.",
    )
    llm_score: Optional[float] = Field(
        default=None,
        description="LLM-assigned confidence score specifically for how well it matches the text context.",
    )


class CandidateResponse(BaseModel):
    """Envelope returned by the debug /candidates endpoint."""

    count: int = Field(description="Number of restaurants returned.")
    filters_applied: dict = Field(
        description="Echo of the filters/preferences used to produce this result."
    )
    restaurants: List[RestaurantOut]
