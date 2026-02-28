from __future__ import annotations

from typing import List, Set

from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.recommendations import _get_restaurants

router = APIRouter(prefix="/metadata", tags=["metadata"])


class FilterMetadata(BaseModel):
    cities: List[str]
    cuisines: List[str]
    available_models: List[str]


@router.get("/filters", response_model=FilterMetadata)
async def get_filter_metadata() -> FilterMetadata:
    """
    Return unique cities and cuisines available in the restaurant dataset,
    plus available LLM models.
    """
    all_restaurants = _get_restaurants()
    
    cities: Set[str] = set()
    cuisines: Set[str] = set()
    
    for r in all_restaurants:
        if r.city:
            cities.add(r.city)
        if r.cuisines:
            for c in r.cuisines:
                cuisines.add(c)
                
    return FilterMetadata(
        cities=sorted(list(cities)),
        cuisines=sorted(list(cuisines)),
        available_models=["gemini-2.5-flash", "gemini-2.5-pro"]
    )
