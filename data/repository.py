from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .models import Restaurant


@dataclass
class RestaurantRepository:
    """In-memory repository for restaurant queries.

    This is intentionally simple for Phase 1 and is backed by a list.
    """

    restaurants: List[Restaurant]

    def all(self) -> List[Restaurant]:
        return list(self.restaurants)

    def filter_by_city(self, city: str) -> List[Restaurant]:
        needle = city.strip().lower()
        return [
            r
            for r in self.restaurants
            if r.city is not None and r.city.strip().lower() == needle
        ]

    def filter_by_min_rating(self, min_rating: float) -> List[Restaurant]:
        return [
            r for r in self.restaurants if r.rating is not None and r.rating >= min_rating
        ]

    def filter_by_cuisine(self, cuisine: str) -> List[Restaurant]:
        needle = cuisine.strip().lower()
        return [
            r
            for r in self.restaurants
            if any(c.lower() == needle for c in r.cuisines)
        ]

    def filter_by_price_range(
        self,
        min_bucket: Optional[int] = None,
        max_bucket: Optional[int] = None,
    ) -> List[Restaurant]:
        def matches(r: Restaurant) -> bool:
            if r.price_range is None:
                return False
            if min_bucket is not None and r.price_range < min_bucket:
                return False
            if max_bucket is not None and r.price_range > max_bucket:
                return False
            return True

        return [r for r in self.restaurants if matches(r)]

    def query(
        self,
        city: Optional[str] = None,
        min_rating: Optional[float] = None,
        cuisines: Optional[Iterable[str]] = None,
        min_price_bucket: Optional[int] = None,
        max_price_bucket: Optional[int] = None,
    ) -> List[Restaurant]:
        """Basic multi-criteria query helper for later phases."""
        results = self.restaurants

        if city:
            results = self.filter_by_city(city)

        if min_rating is not None:
            results = [r for r in results if r.rating is not None and r.rating >= min_rating]

        if cuisines:
            cuisine_needles = {c.strip().lower() for c in cuisines if c.strip()}

            def has_any_cuisine(r: Restaurant) -> bool:
                return any(c.lower() in cuisine_needles for c in r.cuisines)

            results = [r for r in results if has_any_cuisine(r)]

        if min_price_bucket is not None or max_price_bucket is not None:
            results = [
                r
                for r in results
                if r.price_range is not None
                and (min_price_bucket is None or r.price_range >= min_price_bucket)
                and (max_price_bucket is None or r.price_range <= max_price_bucket)
            ]

        return list(results)

