from data.models import Restaurant
from data.repository import RestaurantRepository


def make_restaurant(
    *,
    id: int,
    name: str,
    city: str | None,
    area: str | None,
    cuisines: list[str],
    price_range: int | None,
    rating: float | None,
    votes: int | None,
) -> Restaurant:
    return Restaurant(
        id=id,
        name=name,
        city=city,
        area=area,
        cuisines=cuisines,
        price_range=price_range,
        rating=rating,
        votes=votes,
    )


def build_repository() -> RestaurantRepository:
    restaurants = [
        make_restaurant(
            id=1,
            name="Budget Bites",
            city="Bangalore",
            area="HSR",
            cuisines=["North Indian"],
            price_range=1,
            rating=3.8,
            votes=100,
        ),
        make_restaurant(
            id=2,
            name="Midrange Meals",
            city="Bangalore",
            area="Koramangala",
            cuisines=["Chinese", "Thai"],
            price_range=2,
            rating=4.2,
            votes=250,
        ),
        make_restaurant(
            id=3,
            name="Premium Platter",
            city="Mumbai",
            area="Bandra",
            cuisines=["Italian"],
            price_range=4,
            rating=4.8,
            votes=500,
        ),
        make_restaurant(
            id=4,
            name="Unrated Spot",
            city="Bangalore",
            area="Indiranagar",
            cuisines=["Cafe"],
            price_range=None,
            rating=None,
            votes=None,
        ),
    ]
    return RestaurantRepository(restaurants=restaurants)


def test_filter_by_city_matches_city_case_insensitively() -> None:
    repo = build_repository()
    results = repo.filter_by_city("bangalore")
    assert {r.id for r in results} == {1, 2, 4}


def test_filter_by_min_rating_excludes_lower_rated() -> None:
    repo = build_repository()
    results = repo.filter_by_min_rating(4.0)
    assert {r.id for r in results} == {2, 3}


def test_filter_by_cuisine_matches_any_cuisine() -> None:
    repo = build_repository()
    results = repo.filter_by_cuisine("Chinese")
    assert {r.id for r in results} == {2}


def test_filter_by_price_range_respects_bounds() -> None:
    repo = build_repository()
    results = repo.filter_by_price_range(min_bucket=2, max_bucket=4)
    assert {r.id for r in results} == {2, 3}


def test_query_combines_multiple_criteria() -> None:
    repo = build_repository()
    results = repo.query(
        city="Bangalore",
        min_rating=4.0,
        cuisines=["Thai"],
        min_price_bucket=2,
        max_price_bucket=3,
    )
    # Only "Midrange Meals" should satisfy all these conditions.
    assert {r.id for r in results} == {2}

