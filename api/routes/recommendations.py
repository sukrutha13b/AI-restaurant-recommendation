"""
api/routes/recommendations.py – Debug endpoint for Phase 2.

GET /candidates
    Returns the raw candidate list produced by the recommendation pipeline
    so developers can inspect filtering and scoring behaviour without an LLM.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from fastapi import APIRouter, Query

from api.schemas import CandidateResponse, RecommendationRequest, RestaurantOut
from core.pipeline import run_pipeline
from core.preferences import UserPreferences
from core.scoring import score_restaurant
from data.loader import load_restaurants
from data.models import Restaurant

router = APIRouter(prefix="/candidates", tags=["recommendations"])


# ---------------------------------------------------------------------------
# Data cache – loaded once per process on first request
# ---------------------------------------------------------------------------

def _get_restaurants() -> List[Restaurant]:
    """Load and cache the full restaurant catalogue via central loader."""
    return load_restaurants()


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("", response_model=CandidateResponse, summary="Debug: raw candidate list")
async def get_candidates(
    cities: Optional[str] = Query(default=None, description="Comma-separated cities to filter by."),
    cuisines: Optional[str] = Query(
        default=None,
        description="Comma-separated cuisine types, e.g. 'North Indian,Thai'.",
    ),
    min_rating: Optional[float] = Query(
        default=None, ge=0.0, le=5.0, description="Minimum rating (inclusive)."
    ),
    max_price_bucket: Optional[int] = Query(
        default=None,
        ge=1,
        le=4,
        description="Maximum price bucket (1–4).",
    ),
    top_n: int = Query(
        default=10, ge=1, le=50, description="Number of results to return."
    ),
) -> CandidateResponse:
    """
    Run the Phase-2 recommendation pipeline and return the raw top-N list.

    This endpoint is intentionally *not* behind auth and is intended for
    development / debugging.  It will be superseded by ``POST /recommendations``
    in Phase 4.
    """
    cuisine_list = (
        [c.strip() for c in cuisines.split(",") if c.strip()] if cuisines else None
    )

    req = RecommendationRequest(
        cities=cities,
        cuisines=cuisine_list,
        min_rating=min_rating,
        max_price_bucket=max_price_bucket,
        top_n=top_n,
    )

    preferences = UserPreferences.from_raw(
        cities=req.cities,
        cuisines=req.cuisines,
        min_rating=req.min_rating,
        max_price_bucket=req.max_price_bucket,
        top_n=req.top_n,
    )

    all_restaurants = _get_restaurants()
    candidates = run_pipeline(all_restaurants, preferences)

    restaurant_out = [
        RestaurantOut(
            id=str(r.id),
            name=r.name,
            city=r.city,
            area=r.area,
            cuisines=r.cuisines,
            price_range=r.price_range,
            rating=r.rating,
            votes=r.votes,
            score=r.score,
        )
        for r in candidates
    ]

    filters_applied = {
        "cities": req.cities,
        "cuisines": req.cuisines,
        "min_rating": req.min_rating,
        "max_price_bucket": req.max_price_bucket,
        "top_n": req.top_n,
    }

    return CandidateResponse(
        count=len(restaurant_out),
        filters_applied=filters_applied,
        restaurants=restaurant_out,
    )
