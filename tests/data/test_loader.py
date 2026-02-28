from data.loader import normalize_restaurant


def test_normalize_restaurant_basic_fields() -> None:
    raw = {
        "id": 123,
        "name": "Test Restaurant",
        "location": "HSR Layout",
        "listed_in(city)": "Bangalore",
        "cuisines": "North Indian, Chinese",
        "rate": "4.3/5",
        "votes": "1,234",
        "approx_cost(for two people)": "700",
    }

    restaurant = normalize_restaurant(raw, fallback_id=0)

    assert restaurant.id == 123
    assert restaurant.name == "Test Restaurant"
    assert restaurant.city == "Bangalore"
    assert restaurant.area == "HSR Layout"
    assert restaurant.cuisines == ["North Indian", "Chinese"]
    assert restaurant.rating is not None and abs(restaurant.rating - 4.3) < 1e-6
    assert restaurant.votes == 1234
    # 700 should fall into price bucket 2 (501-1000)
    assert restaurant.price_range == 2


def test_normalize_restaurant_handles_missing_optional_fields() -> None:
    raw = {
        "name": "Nameless City Restaurant",
        "cuisines": None,
        "rate": "NEW",
        "votes": None,
    }

    restaurant = normalize_restaurant(raw, fallback_id=42)

    assert restaurant.id == 42
    assert restaurant.name == "Nameless City Restaurant"
    assert restaurant.city is None
    assert restaurant.area is None
    assert restaurant.cuisines == []
    assert restaurant.rating is None
    assert restaurant.votes is None
    assert restaurant.price_range is None

