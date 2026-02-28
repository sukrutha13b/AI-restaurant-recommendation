from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union


RestaurantId = Union[int, str]


@dataclass(slots=True)
class Restaurant:
    id: RestaurantId
    name: str
    city: Optional[str]
    area: Optional[str]
    cuisines: List[str]
    price_range: Optional[int]
    rating: Optional[float]
    votes: Optional[int]
    # Phase 5: Cacheable computed fields
    score: Optional[float] = None
    llm_score: Optional[float] = None
    llm_explanation: Optional[str] = None

