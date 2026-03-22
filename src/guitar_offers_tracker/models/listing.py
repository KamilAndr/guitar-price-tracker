from datetime import datetime
from enum import Enum
from pydantic import BaseModel, field_validator


class GuitarCondition(str, Enum):
    BRAND_NEW = "brand-new"
    MINT = "mint"
    EXCELLENT = "excellent"
    VERY_GOOD = "very-good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NON_FUNCTIONING = "non-functioning"


class Source(str, Enum):
    REVERB = "reverb"
    EBAY = "ebay"
    THOMANN = "thomann"


class Listing(BaseModel):
    source_id: str
    source: Source
    link: str
    make: str
    title: str
    year: str | None
    condition: GuitarCondition
    price: float
    shipping_cost: float | None
    currency: str
    tax_included: bool | None
    created_at: datetime | None

    @field_validator("year", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str | None) -> str | None:
        if v == "":
            return None
        return v
