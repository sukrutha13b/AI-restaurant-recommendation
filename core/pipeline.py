"""
core/pipeline.py – Top-level orchestration of the recommendation pipeline.

The pipeline is intentionally kept thin: it delegates to filters and scoring
so each step can be tested in isolation.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from data.models import Restaurant
from core.filters import apply_all_filters
from core.preferences import UserPreferences
from core.scoring import rank_restaurants, score_restaurant

log = logging.getLogger(__name__)


def run_pipeline(
    restaurants: List[Restaurant],
    preferences: UserPreferences,
    llm_client: Optional["GeminiRecommender"] = None,
) -> List[Restaurant]:
    """
    Run the deterministic recommendation pipeline and optionally re-rank with LLM.

    Steps:
    1. Apply hard filters (city, price, rating, cuisine).
    2. Rank surviving candidates by composite statistical score (descending).
    3. If an LLM client is provided and a context_description exists:
       a. Pass up to 15 top candidates to the LLM.
       b. Yield the LLM's tailored top-N ranking (including reasoning).
    4. Fallback/Default: Return the top ``preferences.top_n`` statistically ranked results.
    """
    filtered = apply_all_filters(restaurants, preferences)
    ranked = rank_restaurants(filtered, preferences)
    
    # Attach statistical score to top candidates for later use in API
    for r in ranked[:max(preferences.top_n, 15)]:
        r.score = round(score_restaurant(r, preferences), 4)
    
    # Optional Phase 3: LLM Re-ranking
    if llm_client and ranked:
        # Give the LLM a reasonable shortlist so we don't blow token limits
        shortlist = ranked[:15]
        try:
            llm_recommendations = llm_client.re_rank_candidates(
                candidates=shortlist,
                preferences=preferences,
            )
            
            # Map LLM recommendations back to full Restaurant objects and attach reasoning
            final_ranked = []
            cand_dict = {str(r.id): r for r in shortlist}
            
            for llm_rec in llm_recommendations:
                if llm_rec.restaurant_id in cand_dict:
                    restaurant = cand_dict[llm_rec.restaurant_id]
                    # Attach LLM outputs to the object
                    restaurant.llm_explanation = llm_rec.explanation
                    restaurant.llm_score = llm_rec.score
                    final_ranked.append(restaurant)
                    
            if final_ranked:
                return final_ranked[: preferences.top_n]
                
        except Exception as e:
            # We catch all exceptions so the API remains resilient
            log.warning("LLM re-ranking failed, falling back to deterministic sort: %s", e)

    # Fallback / Phase 2 Deterministic Return
    return ranked[: preferences.top_n]
