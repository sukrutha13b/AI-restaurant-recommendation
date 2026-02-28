from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional

import diskcache
from google import genai
from google.genai import types

from core.preferences import UserPreferences
from data.models import Restaurant
from llm.parser import LLMRecommendationOut, LLMResponseEnvelope
from llm.prompts import (
    RECOMMENDATION_SYSTEM_INSTRUCTION,
    build_recommendation_prompt,
)

log = logging.getLogger(__name__)

class LLMError(Exception):
    """Raised when the LLM interaction fails, allowing the pipeline to fallback smoothly."""


class GeminiRecommender:
    """
    Client wrapper for invoking Google Gemini to re-rank restaurant candidates.
    Uses the new `google-genai` SDK and Structured Outputs.
    Includes Phase 5 persistent disk caching.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash", cache_dir: str = ".cache/llm"):
        """Initialize the client. Requires a valid api_key."""
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
        # Initialize disk cache
        os.makedirs(cache_dir, exist_ok=True)
        self.cache = diskcache.Cache(cache_dir)

    def _get_cache_key(self, candidates: List[Restaurant], preferences: UserPreferences) -> str:
        """Generate a stable cache key based on candidates and preferences."""
        # Use IDs and relevant preference fields
        data = {
            "ids": sorted([str(r.id) for r in candidates]),
            "cities": sorted(preferences.cities) if preferences.cities else [],
            "cuisines": sorted(preferences.cuisines) if preferences.cuisines else [],
            "min_rating": preferences.min_rating,
            "max_price": preferences.max_price_bucket,
            "top_n": preferences.top_n,
            "model": self.model_name
        }
        hasher = hashlib.md5()
        hasher.update(json.dumps(data, sort_keys=True).encode())
        return hasher.hexdigest()

    def _serialize_candidates(self, candidates: List[Restaurant], prefs: UserPreferences) -> str:
        """Serialize candidate data to minimal JSON for the LLM prompt."""
        simple_list = []
        for r in candidates:
            simple_list.append(
                {
                    "id": str(r.id),
                    "name": r.name,
                    "cuisines": r.cuisines,
                    "rating": r.rating,
                    "votes": r.votes,
                    "price_bucket": r.price_range,
                }
            )
        return json.dumps(simple_list, indent=2)

    def re_rank_candidates(
        self,
        candidates: List[Restaurant],
        preferences: UserPreferences,
    ) -> List[LLMRecommendationOut]:
        """
        Send candidates and search criteria to Gemini to get ranked recommendations.
        Results are cached to disk to improve performance and reduce costs.
        """
        if not candidates:
            return []

        # Phase 5: Check Cache
        cache_key = self._get_cache_key(candidates, preferences)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            log.info("Returning cached Gemini re-ranking for key: %s", cache_key)
            # Reconstruct LLMRecommendationOut objects from cached dicts
            return [LLMRecommendationOut.model_validate(r) for r in cached_result]

        criteria_parts = []
        if preferences.cities:
            criteria_parts.append(f"Cities: {', '.join(preferences.cities)}")
        if preferences.cuisines:
            criteria_parts.append(f"Cuisines: {', '.join(preferences.cuisines)}")
        if preferences.min_rating:
            criteria_parts.append(f"Minimum Rating: {preferences.min_rating}+")
        if preferences.max_price_bucket:
            criteria_parts.append(f"Max Price Bucket: {preferences.max_price_bucket}/4")
        
        preferences_summary = r"\n".join(criteria_parts) if criteria_parts else "General recommendation based on top scores."

        candidates_json = self._serialize_candidates(candidates, preferences)
        prompt = build_recommendation_prompt(preferences_summary, candidates_json)

        # Build schema forcing for the Gemini API
        system_instruction = RECOMMENDATION_SYSTEM_INSTRUCTION.format(
            top_n=preferences.top_n
        )

        log.info("Invoking Gemini API for re-ranking (Cache Miss: %s)", cache_key)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=LLMResponseEnvelope,
                    temperature=0.3, # low temp for more factual/focused reasoning
                ),
            )
            raw_text = response.text
            if not raw_text:
                raise LLMError("Received empty response from Gemini.")

        except Exception as e:
            raise LLMError(f"Gemini API invocation failed: {str(e)}") from e

        try:
            envelope_data = json.loads(raw_text)
            envelope = LLMResponseEnvelope.model_validate(envelope_data)
            
            # Phase 5: Store in Cache (convert models to dict for serialization)
            recs_dicts = [r.model_dump() for r in envelope.recommendations]
            self.cache.set(cache_key, recs_dicts, expire=3600 * 24) # 24h expiration
            
            return envelope.recommendations
        except Exception as e:
            raise LLMError(f"Failed to parse or validate LLM JSON output: {str(e)}") from e
