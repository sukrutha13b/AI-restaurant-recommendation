from __future__ import annotations
from functools import lru_cache

from typing import Any, Dict, List, Optional

from datasets import load_dataset

from .models import Restaurant

DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"
DEFAULT_SPLIT = "train"


def _parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text or text.upper() in {"NEW", "NAN", "NULL", "NA", "N/A", "-"}:
        return None

    # Some Zomato-style ratings look like "4.3/5"
    if "/" in text:
        text = text.split("/", 1)[0].strip()

    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)

    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _normalize_cuisines(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]

    parts = str(raw).split(",")
    return [part.strip() for part in parts if part.strip()]


def _derive_price_range(record: Dict[str, Any]) -> Optional[int]:
    """
    Try to derive a coarse price range bucket.

    Strategy:
    - Prefer explicit "price_range" if present.
    - Fall back to approximate cost, if available, and bucket:
      <= 500 -> 1, <= 1000 -> 2, <= 2000 -> 3, > 2000 -> 4.
    """
    if "price_range" in record:
        value = _parse_int(record.get("price_range"))
        if value is not None:
            return value

    approx_keys = [
        "approx_cost(for two people)",
        "approx_cost_for_two_people",
        "approx_cost",
    ]
    approx_value: Optional[int] = None
    for key in approx_keys:
        if key in record:
            approx_value = _parse_int(record.get(key))
            if approx_value is not None:
                break

    if approx_value is None:
        return None

    if approx_value <= 500:
        return 1
    if approx_value <= 1000:
        return 2
    if approx_value <= 2000:
        return 3
    return 4


def normalize_restaurant(record: Dict[str, Any], fallback_id: int) -> Restaurant:
    """
    Normalize a raw dataset record into a Restaurant domain model.

    This function is deterministic and used in tests; it does not perform any I/O.
    """
    # Try a few known id/name fields; fall back to index-based id.
    rid = (
        record.get("id")
        or record.get("restaurant_id")
        or record.get("url")  # sometimes URLs are unique identifiers
        or fallback_id
    )

    name = str(
        record.get("name")
        or record.get("restaurant_name")
        or "Unknown Restaurant"
    ).strip()

    # Zomato-style datasets often have both granular location and city columns.
    city = (
        record.get("city")
        or record.get("listed_in(city)")
        or record.get("city_name")
    )
    city_str = str(city).strip() if city is not None else None

    area = record.get("location") or record.get("address") or record.get("locality")
    area_str = str(area).strip() if area is not None else None

    cuisines = _normalize_cuisines(
        record.get("cuisines") or record.get("cuisine") or record.get("tags")
    )

    rating_raw = record.get("rating") or record.get("rate") or record.get("aggregate_rating")
    rating = _parse_float(rating_raw)

    votes_raw = record.get("votes") or record.get("rating_count") or record.get("review_count")
    votes = _parse_int(votes_raw)

    price_range = _derive_price_range(record)

    return Restaurant(
        id=rid,
        name=name,
        city=city_str,
        area=area_str,
        cuisines=cuisines,
        price_range=price_range,
        rating=rating,
        votes=votes,
    )


@lru_cache(maxsize=1)
def load_restaurants(limit: Optional[int] = None) -> List[Restaurant]:
    """
    Load restaurants from the Hugging Face dataset into normalized Restaurant objects.

    This function calls the Hugging Face `load_dataset` API and may require network
    access the first time it runs. For tests, prefer using `normalize_restaurant`
    directly with fixture records to avoid external dependencies.
    """
    dataset = load_dataset(DATASET_NAME, split=DEFAULT_SPLIT)

    restaurants: List[Restaurant] = []
    seen: set[tuple[str, Optional[str], Optional[str]]] = set()

    for idx, record in enumerate(dataset):
        restaurant = normalize_restaurant(record, fallback_id=idx)
        
        # Deduplication based on composite key (name, city, area)
        key = (restaurant.name.lower(), 
               restaurant.city.lower() if restaurant.city else None, 
               restaurant.area.lower() if restaurant.area else None)
        
        if key not in seen:
            seen.add(key)
            restaurants.append(restaurant)
            
        if limit is not None and len(restaurants) >= limit:
            break

    return restaurants

