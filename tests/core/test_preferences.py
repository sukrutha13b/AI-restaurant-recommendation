"""
tests/core/test_preferences.py – Unit tests for UserPreferences normalization and validation.
"""
import pytest

from core.preferences import UserPreferences


# ---------------------------------------------------------------------------
# Normalization tests
# ---------------------------------------------------------------------------

def test_from_raw_normalizes_city_to_lowercase() -> None:
    prefs = UserPreferences.from_raw(cities=["  Bangalore  "])
    assert prefs.cities == ["bangalore"]


def test_from_raw_city_none_returns_none() -> None:
    prefs = UserPreferences.from_raw(cities=None)
    assert prefs.cities == []


def test_from_raw_empty_city_string_becomes_none() -> None:
    prefs = UserPreferences.from_raw(cities="   ")
    assert prefs.cities == []


def test_from_raw_normalizes_cuisines_to_lowercase() -> None:
    prefs = UserPreferences.from_raw(cuisines=["North Indian", "  Chinese  "])
    assert prefs.cuisines == ["north indian", "chinese"]


def test_from_raw_drops_empty_cuisine_strings() -> None:
    prefs = UserPreferences.from_raw(cuisines=["North Indian", "", "  "])
    assert prefs.cuisines == ["north indian"]


def test_from_raw_none_cuisines_becomes_empty_list() -> None:
    prefs = UserPreferences.from_raw(cuisines=None)
    assert prefs.cuisines == []


def test_from_raw_top_n_clamped_below_minimum() -> None:
    prefs = UserPreferences.from_raw(top_n=0)
    assert prefs.top_n == 1


def test_from_raw_top_n_clamped_above_maximum() -> None:
    prefs = UserPreferences.from_raw(top_n=999)
    assert prefs.top_n == 50


def test_from_raw_top_n_valid_value_preserved() -> None:
    prefs = UserPreferences.from_raw(top_n=15)
    assert prefs.top_n == 15


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

def test_validate_min_rating_above_5_raises() -> None:
    with pytest.raises(ValueError, match="min_rating"):
        UserPreferences.from_raw(min_rating=5.1)


def test_validate_min_rating_below_0_raises() -> None:
    with pytest.raises(ValueError, match="min_rating"):
        UserPreferences.from_raw(min_rating=-0.1)


def test_validate_min_rating_boundary_values_are_valid() -> None:
    assert UserPreferences.from_raw(min_rating=0.0).min_rating == 0.0
    assert UserPreferences.from_raw(min_rating=5.0).min_rating == 5.0


def test_validate_max_price_bucket_zero_raises() -> None:
    with pytest.raises(ValueError, match="max_price_bucket"):
        UserPreferences.from_raw(max_price_bucket=0)


def test_validate_max_price_bucket_five_raises() -> None:
    with pytest.raises(ValueError, match="max_price_bucket"):
        UserPreferences.from_raw(max_price_bucket=5)


def test_validate_max_price_bucket_valid_values() -> None:
    for bucket in (1, 2, 3, 4):
        prefs = UserPreferences.from_raw(max_price_bucket=bucket)
        assert prefs.max_price_bucket == bucket


def test_validate_none_optional_fields_pass() -> None:
    """All optional fields as None should always be valid."""
    prefs = UserPreferences.from_raw()
    assert prefs.cities == []
    assert prefs.cuisines == []
    assert prefs.min_rating is None
    assert prefs.max_price_bucket is None
    assert prefs.top_n == 10
