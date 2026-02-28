"""
tests/core/test_pipeline.py – Unit tests for run_pipeline end-to-end consistency.
"""
from typing import List

from core.pipeline import run_pipeline
from core.preferences import UserPreferences
from data.models import Restaurant


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_restaurant(
    *,
    id: int,
    city: str | None = "Bangalore",
    cuisines: List[str] | None = None,
    price_range: int | None = 2,
    rating: float | None = 4.0,
    votes: int | None = 200,
) -> Restaurant:
    return Restaurant(
        id=id,
        name=f"Restaurant {id}",
        city=city,
        area="Area",
        cuisines=cuisines or [],
        price_range=price_range,
        rating=rating,
        votes=votes,
    )


CATALOGUE = [
    make_restaurant(id=1, city="Bangalore", cuisines=["North Indian"], price_range=1, rating=3.5, votes=50),
    make_restaurant(id=2, city="Bangalore", cuisines=["Chinese", "Thai"], price_range=2, rating=4.2, votes=250),
    make_restaurant(id=3, city="Bangalore", cuisines=["Pizza"], price_range=2, rating=4.0, votes=100),
    make_restaurant(id=4, city="Mumbai", cuisines=["Continental"], price_range=3, rating=4.7, votes=800),
    make_restaurant(id=5, city="Bangalore", cuisines=["Cafe"], price_range=None, rating=None, votes=None),
]


# ---------------------------------------------------------------------------
# Pipeline tests
# ---------------------------------------------------------------------------

def test_pipeline_no_filters_returns_top_n() -> None:
    prefs = UserPreferences.from_raw(top_n=3)
    results = run_pipeline(CATALOGUE, prefs)
    # Should return 3 restaurants ranked by score.
    assert len(results) == 3


def test_pipeline_respects_top_n_exactly() -> None:
    prefs = UserPreferences.from_raw(top_n=2)
    results = run_pipeline(CATALOGUE, prefs)
    assert len(results) == 2


def test_pipeline_top_n_larger_than_catalogue_returns_all() -> None:
    prefs = UserPreferences.from_raw(top_n=50)
    results = run_pipeline(CATALOGUE, prefs)
    assert len(results) == len(CATALOGUE)


def test_pipeline_city_filter_applied() -> None:
    prefs = UserPreferences.from_raw(cities=["Mumbai"], top_n=10)
    results = run_pipeline(CATALOGUE, prefs)
    assert all(r.city and r.city.lower() == "mumbai" for r in results)
    assert {r.id for r in results} == {4}


def test_pipeline_city_and_rating_filter() -> None:
    prefs = UserPreferences.from_raw(cities=["Bangalore"], min_rating=4.0, top_n=10)
    results = run_pipeline(CATALOGUE, prefs)
    assert {r.id for r in results} == {2, 3}


def test_pipeline_city_price_and_cuisine_filter() -> None:
    prefs = UserPreferences.from_raw(
        cities=["Bangalore"],
        max_price_bucket=2,
        cuisines=["Thai"],
        top_n=10,
    )
    results = run_pipeline(CATALOGUE, prefs)
    assert {r.id for r in results} == {2}


def test_pipeline_zero_matches_returns_empty() -> None:
    prefs = UserPreferences.from_raw(cities=["Delhi"], top_n=10)
    results = run_pipeline(CATALOGUE, prefs)
    assert results == []


def test_pipeline_results_ordered_by_score_descending() -> None:
    """Highest-rated/most-voted restaurants should appear first."""
    prefs = UserPreferences.from_raw(cities=["Bangalore"], min_rating=3.5, top_n=10)
    results = run_pipeline(CATALOGUE, prefs)
    # id=2 has rating=4.2, votes=250 – should beat id=3 (rating=4.0, votes=100)
    # which should beat id=1 (rating=3.5, votes=50).
    assert results[0].id == 2
    assert results[1].id == 3
    assert results[2].id == 1


def test_pipeline_does_not_mutate_input_catalogue() -> None:
    """run_pipeline must not modify the original catalogue list."""
    prefs = UserPreferences.from_raw(top_n=3)
    original_ids = [r.id for r in CATALOGUE]
    run_pipeline(CATALOGUE, prefs)
    assert [r.id for r in CATALOGUE] == original_ids
