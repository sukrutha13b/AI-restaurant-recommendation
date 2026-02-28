"""
core/filters.py – Hard-filter functions for the recommendation pipeline.

All functions are pure (no side-effects) and operate on plain lists of
Restaurant objects.  They are intentionally simple and composable.
"""
from __future__ import annotations

from typing import List

from data.models import Restaurant
from core.preferences import UserPreferences


def filter_by_cities(restaurants: List[Restaurant], cities: List[str]) -> List[Restaurant]:
    """Return restaurants whose city matches any of *cities* (any-match, case-insensitive)."""
    if not cities:
        return list(restaurants)
    
    needles = {c.strip().lower() for c in cities if c.strip()}
    if not needles:
        return list(restaurants)

    return [
        r
        for r in restaurants
        if r.city is not None and r.city.strip().lower() in needles
    ]


def filter_by_price(
    restaurants: List[Restaurant], max_bucket: int
) -> List[Restaurant]:
    """
    Return restaurants with price_range ≤ max_bucket.

    Restaurants whose price_range is None are excluded when a max_bucket is
    specified, because we cannot verify they are within budget.
    """
    return [
        r
        for r in restaurants
        if r.price_range is not None and r.price_range <= max_bucket
    ]


def filter_by_rating(
    restaurants: List[Restaurant], min_rating: float
) -> List[Restaurant]:
    """Return restaurants with rating ≥ min_rating.  Unrated entries are excluded."""
    return [
        r for r in restaurants if r.rating is not None and r.rating >= min_rating
    ]


def filter_by_cuisines(
    restaurants: List[Restaurant], cuisines: List[str]
) -> List[Restaurant]:
    """
    Return restaurants that serve at least one cuisine in *cuisines*.

    Comparison is case-insensitive.  An empty *cuisines* list returns all
    restaurants unchanged (no cuisine preference).
    """
    if not cuisines:
        return list(restaurants)

    needles = {c.strip().lower() for c in cuisines if c.strip()}
    if not needles:
        return list(restaurants)

    return [
        r
        for r in restaurants
        if any(c.strip().lower() in needles for c in r.cuisines)
    ]


def apply_all_filters(
    restaurants: List[Restaurant], preferences: UserPreferences
) -> List[Restaurant]:
    """
    Apply all hard filters derived from *preferences* in sequence.

    Filter order:
    1. City (most selective first).
    2. Max price bucket.
    3. Min rating.
    4. Cuisines (any-match).
    """
    results = list(restaurants)

    if preferences.cities:
        results = filter_by_cities(results, preferences.cities)

    if preferences.max_price_bucket is not None:
        results = filter_by_price(results, preferences.max_price_bucket)

    if preferences.min_rating is not None:
        results = filter_by_rating(results, preferences.min_rating)

    if preferences.cuisines:
        results = filter_by_cuisines(results, preferences.cuisines)

    return results
