"""
tests/core/test_scoring.py – Unit tests for score_restaurant and rank_restaurants.
"""
from typing import List

from core.preferences import UserPreferences
from core.scoring import rank_restaurants, score_restaurant
from data.models import Restaurant


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_restaurant(
    *,
    id: int,
    rating: float | None = None,
    votes: int | None = None,
    price_range: int | None = None,
    name: str = "Test",
) -> Restaurant:
    return Restaurant(
        id=id,
        name=name,
        city=None,
        area=None,
        cuisines=[],
        rating=rating,
        votes=votes,
        price_range=price_range,
    )


# ---------------------------------------------------------------------------
# score_restaurant
# ---------------------------------------------------------------------------

def test_score_perfect_restaurant_near_one() -> None:
    """Max rating + max votes + matching price bucket → close to 1.0."""
    r = make_restaurant(id=1, rating=5.0, votes=5000, price_range=3)
    prefs = UserPreferences.from_raw(max_price_bucket=3)
    score = score_restaurant(r, prefs)
    assert abs(score - 1.0) < 1e-6


def test_score_zero_when_all_fields_missing() -> None:
    r = make_restaurant(id=1, rating=None, votes=None, price_range=None)
    prefs = UserPreferences.from_raw()
    assert score_restaurant(r, prefs) == 0.0


def test_score_rating_only_contributes_60_percent() -> None:
    """Rating=5.0, no votes, no price match → 0.6."""
    r = make_restaurant(id=1, rating=5.0, votes=None, price_range=None)
    prefs = UserPreferences.from_raw()
    score = score_restaurant(r, prefs)
    assert abs(score - 0.6) < 1e-6


def test_score_votes_only_contributes_30_percent_at_max() -> None:
    """No rating, max votes (≥5000), no price match → 0.3."""
    r = make_restaurant(id=1, rating=None, votes=5000, price_range=None)
    prefs = UserPreferences.from_raw()
    score = score_restaurant(r, prefs)
    assert abs(score - 0.3) < 1e-6


def test_score_price_bonus_only_contributes_10_percent() -> None:
    """No rating, no votes, price match → 0.1."""
    r = make_restaurant(id=1, rating=None, votes=None, price_range=2)
    prefs = UserPreferences.from_raw(max_price_bucket=2)
    score = score_restaurant(r, prefs)
    assert abs(score - 0.1) < 1e-6


def test_score_no_price_bonus_when_no_preference() -> None:
    """Price bonus is 0 when max_price_bucket is not set."""
    r = make_restaurant(id=1, rating=None, votes=None, price_range=2)
    prefs = UserPreferences.from_raw(max_price_bucket=None)
    score = score_restaurant(r, prefs)
    assert score == 0.0


def test_score_no_price_bonus_when_price_does_not_match() -> None:
    r = make_restaurant(id=1, rating=None, votes=None, price_range=1)
    prefs = UserPreferences.from_raw(max_price_bucket=3)
    assert score_restaurant(r, prefs) == 0.0


def test_score_votes_capped_at_5000() -> None:
    """Votes beyond 5000 don't increase the score further."""
    r_capped = make_restaurant(id=1, rating=None, votes=5000, price_range=None)
    r_over = make_restaurant(id=2, rating=None, votes=100_000, price_range=None)
    prefs = UserPreferences.from_raw()
    assert abs(score_restaurant(r_capped, prefs) - score_restaurant(r_over, prefs)) < 1e-9


def test_score_partial_votes_scales_linearly() -> None:
    """2500 votes → votes_score=0.5 → contribution=0.3*0.5=0.15."""
    r = make_restaurant(id=1, rating=None, votes=2500, price_range=None)
    prefs = UserPreferences.from_raw()
    assert abs(score_restaurant(r, prefs) - 0.15) < 1e-9


# ---------------------------------------------------------------------------
# rank_restaurants
# ---------------------------------------------------------------------------

def test_rank_restaurants_orders_by_score_descending() -> None:
    restaurants = [
        make_restaurant(id=1, rating=3.0, votes=100),
        make_restaurant(id=2, rating=4.5, votes=1000),
        make_restaurant(id=3, rating=5.0, votes=5000),
    ]
    prefs = UserPreferences.from_raw()
    ranked = rank_restaurants(restaurants, prefs)
    assert [r.id for r in ranked] == [3, 2, 1]


def test_rank_restaurants_equal_scores_preserve_relative_order() -> None:
    """When scores are equal, original relative order is preserved (stable sort)."""
    restaurants = [
        make_restaurant(id=1, rating=None, votes=None),
        make_restaurant(id=2, rating=None, votes=None),
    ]
    prefs = UserPreferences.from_raw()
    ranked = rank_restaurants(restaurants, prefs)
    assert [r.id for r in ranked] == [1, 2]


def test_rank_restaurants_returns_all_items() -> None:
    restaurants = [make_restaurant(id=i) for i in range(5)]
    prefs = UserPreferences.from_raw()
    ranked = rank_restaurants(restaurants, prefs)
    assert len(ranked) == 5
