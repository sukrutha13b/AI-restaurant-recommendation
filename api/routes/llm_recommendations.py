"""
api/routes/llm_recommendations.py – Production endpoint using Gemini.

POST /recommendations
    Accepts a JSON payload of user preferences including free-text context.
    Invokes the Phase 3 recommendation pipeline.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from api.routes.recommendations import _get_restaurants
from api.schemas import CandidateResponse, RecommendationRequest, RestaurantOut
from config.settings import Settings, get_settings
from core.pipeline import run_pipeline
from core.preferences import UserPreferences
from llm.client import GeminiRecommender

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_llm_client(api_key: str, model_name: str) -> GeminiRecommender:
    """Helper to build a Gemini client."""
    return GeminiRecommender(
        api_key=api_key,
        model_name=model_name,
    )


@router.post(
    "",
    response_model=CandidateResponse,
    summary="Get personalized culinary recommendations",
)
async def create_recommendations(
    request: RecommendationRequest,
    settings: Settings = Depends(get_settings),
) -> CandidateResponse:
    """
    Search for restaurants using hard filters and optionally re-rank using AI.

    If ``context_description`` is provided and the server is configured with
    a Gemini API key, the top candidates will be re-ranked by the LLM to find
    the perfect match for your specific occasion, and an explanation will be
    provided for each.
    """
    if not settings.gemini_api_key:
        llm_client = None
    else:
        llm_client = get_llm_client(settings.gemini_api_key, request.model_name)

    try:
        preferences = UserPreferences.from_raw(
            cities=request.cities,
            cuisines=request.cuisines,
            min_rating=request.min_rating,
            max_price_bucket=request.max_price_bucket,
            top_n=request.top_n,
            model_name=request.model_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    all_restaurants = _get_restaurants()
    candidates = run_pipeline(all_restaurants, preferences, llm_client=llm_client)

    restaurant_out = []
    for r in candidates:
        r_out = RestaurantOut(
            id=str(r.id),
            name=r.name,
            city=r.city,
            area=r.area,
            cuisines=r.cuisines,
            price_range=r.price_range,
            rating=r.rating,
            votes=r.votes,
            score=r.score,
            llm_score=r.llm_score,
            explanation=r.llm_explanation,
        )
        restaurant_out.append(r_out)

    filters_applied = request.model_dump(exclude_unset=True)

    return CandidateResponse(
        count=len(restaurant_out),
        filters_applied=filters_applied,
        restaurants=restaurant_out,
    )
