"""
core/scoring.py – Scoring and ranking logic for the recommendation pipeline.

Scoring formula (composite, range 0.0–1.0):
  score = rating_score * 0.6
        + votes_score  * 0.3
        + price_bonus  * 0.1

Where:
  rating_score  = rating / 5.0          (clamped to [0, 1])
  votes_score   = min(votes / 5000, 1.0)
  price_bonus   = 1.0 if restaurant.price_range == preferences.max_price_bucket
                  else 0.0

Missing fields contribute 0 to their component (no penalty beyond the zero
contribution, which preserves relative ordering among known restaurants).
"""
from __future__ import annotations

from typing import List

from data.models import Restaurant
from core.preferences import UserPreferences

# Weights must sum to 1.0
_WEIGHT_RATING = 0.6
_WEIGHT_VOTES = 0.3
_WEIGHT_PRICE_BONUS = 0.1

# Normalisation denominators
_MAX_RATING = 5.0
_VOTES_SCALE = 5_000  # votes beyond this are not rewarded further


def score_restaurant(restaurant: Restaurant, preferences: UserPreferences) -> float:
    """
    Compute a composite relevance score in [0.0, 1.0] for *restaurant*.

    Parameters
    ----------
    restaurant:
        The candidate restaurant to score.
    preferences:
        The user preferences used for contextual scoring (price bonus).

    Returns
    -------
    float
        Composite score, higher is better.
    """
    # --- Rating contribution ---
    if restaurant.rating is not None:
        rating_score = max(0.0, min(restaurant.rating / _MAX_RATING, 1.0))
    else:
        rating_score = 0.0

    # --- Votes/popularity contribution ---
    if restaurant.votes is not None:
        votes_score = min(restaurant.votes / _VOTES_SCALE, 1.0)
    else:
        votes_score = 0.0

    # --- Price proximity bonus ---
    if (
        preferences.max_price_bucket is not None
        and restaurant.price_range is not None
        and restaurant.price_range == preferences.max_price_bucket
    ):
        price_bonus = 1.0
    else:
        price_bonus = 0.0

    return (
        rating_score * _WEIGHT_RATING
        + votes_score * _WEIGHT_VOTES
        + price_bonus * _WEIGHT_PRICE_BONUS
    )


def rank_restaurants(
    restaurants: List[Restaurant], preferences: UserPreferences
) -> List[Restaurant]:
    """
    Return *restaurants* sorted by :func:`score_restaurant` in descending order.

    This is a stable sort: restaurants with equal scores keep their original
    relative order (useful for deterministic tests).
    """
    return sorted(
        restaurants,
        key=lambda r: score_restaurant(r, preferences),
        reverse=True,
    )
