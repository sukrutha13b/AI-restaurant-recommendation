"""
core/preferences.py – UserPreferences model with normalization and validation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserPreferences:
    """
    Encapsulates a user's restaurant search preferences.

    All string fields are stored in their normalized (stripped / lower-cased)
    form.  Call :meth:`from_raw` to build from raw user input, or use the
    constructor directly when you already have clean values.
    """

    cities: List[str] = field(default_factory=list)
    cuisines: List[str] = field(default_factory=list)
    min_rating: Optional[float] = None  # inclusive, 0.0–5.0
    max_price_bucket: Optional[int] = None  # inclusive, 1–4
    top_n: int = 10  # 1–50
    model_name: str = "gemini-1.5-flash"

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_raw(
        cls,
        cities: Optional[List[str] | str] = None,
        cuisines: Optional[List[str] | str] = None,
        min_rating: Optional[float] = None,
        max_price_bucket: Optional[int] = None,
        top_n: int = 10,
        model_name: str = "gemini-1.5-flash",
    ) -> "UserPreferences":
        """
        Build a UserPreferences from raw (potentially un-normalized) inputs.

        Normalization applied:
        - city and cuisine strings are stripped and lower-cased.
        - Empty strings are dropped.
        - top_n is clamped to [1, 50].
        - None values are preserved (meaning "no preference").
        """
        norm_cities = []
        if isinstance(cities, str):
            norm_cities = [c.strip().lower() for c in cities.split(",") if c.strip()]
        elif isinstance(cities, list):
            norm_cities = [c.strip().lower() for c in cities if c.strip()]

        norm_cuisines = []
        if isinstance(cuisines, str):
            norm_cuisines = [c.strip().lower() for c in cuisines.split(",") if c.strip()]
        elif isinstance(cuisines, list):
            norm_cuisines = [c.strip().lower() for c in cuisines if c.strip()]

        prefs = cls(
            cities=norm_cities,
            cuisines=norm_cuisines,
            min_rating=min_rating,
            max_price_bucket=max_price_bucket,
            top_n=max(1, min(50, int(top_n))),
            model_name=model_name,
        )
        prefs.validate()
        return prefs

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Raise ValueError if any field has a logically invalid value.
        This is called automatically by :meth:`from_raw`.
        """
        if self.min_rating is not None:
            try:
                val = float(self.min_rating)
                if not (0.0 <= val <= 5.0):
                    raise ValueError(
                        f"min_rating must be between 0.0 and 5.0, got {self.min_rating!r}"
                    )
            except (TypeError, ValueError):
                raise ValueError(f"min_rating must be a number, got {self.min_rating!r}")
        if self.max_price_bucket is not None:
            if self.max_price_bucket not in (1, 2, 3, 4):
                raise ValueError(
                    f"max_price_bucket must be 1–4, got {self.max_price_bucket!r}"
                )
        if not (1 <= self.top_n <= 50):
            raise ValueError(f"top_n must be between 1 and 50, got {self.top_n!r}")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_str(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip().lower()
        return stripped if stripped else None
