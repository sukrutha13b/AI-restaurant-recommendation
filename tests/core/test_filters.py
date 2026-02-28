"""
tests/core/test_filters.py – Unit tests for core filter functions.
"""
from typing import List

import pytest

from core.filters import (
    apply_all_filters,
    filter_by_cities,
    filter_by_cuisines,
    filter_by_price,
    filter_by_rating,
)
from core.preferences import UserPreferences
from data.models import Restaurant


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_restaurant(
    *,
    id: int,
    name: str = "Test",
    city: str | None = "Bangalore",
    area: str | None = "Koramangala",
    cuisines: List[str] | None = None,
    price_range: int | None = 2,
    rating: float | None = 4.0,
    votes: int | None = 200,
) -> Restaurant:
    return Restaurant(
        id=id,
        name=name,
        city=city,
        area=area,
        cuisines=cuisines or [],
        price_range=price_range,
        rating=rating,
        votes=votes,
    )


RESTAURANTS = [
    make_restaurant(id=1, city="Bangalore", cuisines=["North Indian"], price_range=1, rating=3.5),
    make_restaurant(id=2, city="Bangalore", cuisines=["Chinese", "Thai"], price_range=2, rating=4.2),
    make_restaurant(id=3, city="Mumbai", cuisines=["Italian"], price_range=4, rating=4.8),
    make_restaurant(id=4, city="Bangalore", cuisines=["Cafe"], price_range=None, rating=None),
    make_restaurant(id=5, city=None, cuisines=["Continental"], price_range=3, rating=3.0),
]


# ---------------------------------------------------------------------------
# filter_by_cities
# ---------------------------------------------------------------------------

def test_filter_by_cities_returns_matching_city() -> None:
    results = filter_by_cities(RESTAURANTS, ["Bangalore"])
    assert {r.id for r in results} == {1, 2, 4}


def test_filter_by_cities_case_insensitive() -> None:
    results = filter_by_cities(RESTAURANTS, ["bangalore"])
    assert {r.id for r in results} == {1, 2, 4}


def test_filter_by_cities_strips_whitespace() -> None:
    results = filter_by_cities(RESTAURANTS, ["  Mumbai  "])
    assert {r.id for r in results} == {3}


def test_filter_by_cities_excludes_none_city() -> None:
    results = filter_by_cities(RESTAURANTS, ["Bangalore"])
    assert 5 not in {r.id for r in results}


def test_filter_by_cities_no_match_returns_empty() -> None:
    assert filter_by_cities(RESTAURANTS, ["Delhi"]) == []


def test_filter_by_cities_multiple_returns_matches() -> None:
    results = filter_by_cities(RESTAURANTS, ["Bangalore", "Mumbai"])
    assert {r.id for r in results} == {1, 2, 3, 4}


# ---------------------------------------------------------------------------
# filter_by_price
# ---------------------------------------------------------------------------

def test_filter_by_price_max_bucket_2_excludes_higher() -> None:
    results = filter_by_price(RESTAURANTS, max_bucket=2)
    assert {r.id for r in results} == {1, 2}


def test_filter_by_price_excludes_restaurants_with_none_price() -> None:
    results = filter_by_price(RESTAURANTS, max_bucket=4)
    assert 4 not in {r.id for r in results}


def test_filter_by_price_max_bucket_1_returns_cheapest_only() -> None:
    results = filter_by_price(RESTAURANTS, max_bucket=1)
    assert {r.id for r in results} == {1}


def test_filter_by_price_exact_bucket_included() -> None:
    results = filter_by_price(RESTAURANTS, max_bucket=3)
    assert 5 in {r.id for r in results}


# ---------------------------------------------------------------------------
# filter_by_rating
# ---------------------------------------------------------------------------

def test_filter_by_rating_excludes_below_min() -> None:
    results = filter_by_rating(RESTAURANTS, min_rating=4.0)
    assert {r.id for r in results} == {2, 3}


def test_filter_by_rating_excludes_none_rated() -> None:
    results = filter_by_rating(RESTAURANTS, min_rating=0.0)
    assert 4 not in {r.id for r in results}


def test_filter_by_rating_exact_boundary_included() -> None:
    results = filter_by_rating(RESTAURANTS, min_rating=4.2)
    assert 2 in {r.id for r in results}


# ---------------------------------------------------------------------------
# filter_by_cuisines
# ---------------------------------------------------------------------------

def test_filter_by_cuisines_any_match() -> None:
    results = filter_by_cuisines(RESTAURANTS, ["Chinese"])
    assert {r.id for r in results} == {2}


def test_filter_by_cuisines_case_insensitive() -> None:
    results = filter_by_cuisines(RESTAURANTS, ["north indian"])
    assert {r.id for r in results} == {1}


def test_filter_by_cuisines_multiple_values_any_match() -> None:
    results = filter_by_cuisines(RESTAURANTS, ["Italian", "Cafe"])
    assert {r.id for r in results} == {3, 4}


def test_filter_by_cuisines_empty_list_returns_all() -> None:
    results = filter_by_cuisines(RESTAURANTS, [])
    assert len(results) == len(RESTAURANTS)


# ---------------------------------------------------------------------------
# apply_all_filters (combined pipeline)
# ---------------------------------------------------------------------------

def test_apply_all_filters_city_and_rating() -> None:
    prefs = UserPreferences.from_raw(cities=["Bangalore"], min_rating=4.0)
    results = apply_all_filters(RESTAURANTS, prefs)
    assert {r.id for r in results} == {2}


def test_apply_all_filters_city_and_price() -> None:
    prefs = UserPreferences.from_raw(cities=["Bangalore"], max_price_bucket=2)
    results = apply_all_filters(RESTAURANTS, prefs)
    assert {r.id for r in results} == {1, 2}


def test_apply_all_filters_no_filters_returns_all() -> None:
    prefs = UserPreferences.from_raw()
    results = apply_all_filters(RESTAURANTS, prefs)
    assert len(results) == len(RESTAURANTS)


def test_apply_all_filters_impossible_combo_returns_empty() -> None:
    prefs = UserPreferences.from_raw(cities=["Bangalore"], min_rating=4.9)
    results = apply_all_filters(RESTAURANTS, prefs)
    assert results == []


def test_apply_all_filters_city_cuisine_and_price() -> None:
    prefs = UserPreferences.from_raw(
        cities=["Bangalore"], cuisines=["Chinese"], max_price_bucket=3
    )
    results = apply_all_filters(RESTAURANTS, prefs)
    assert {r.id for r in results} == {2}
