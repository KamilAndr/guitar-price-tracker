import requests
import structlog
from guitar_price_tracker.models.listing import Listing, Source


logger = structlog.get_logger(__name__)


def _fetch_raw_listings(query: str, token: str, per_page: int = 50) -> dict:
    response = requests.get(
        "https://api.reverb.com/api/listings",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/hal+json",
            "Accept-Version": "3.0",
            "X-Display-Currency": "EUR",
        },
        params={
            "query": query,
            "exclude_auctions": "true",
            "per_page": per_page,
        },
    )
    response.raise_for_status()
    data = response.json()
    logger.info(
        "reverb_fetch_complete",
        query=query,
        total=data.get("total"),
        page=data.get("current_page"),
        per_page=per_page,
    )
    return data


def _extract_shipping_cost(rates: list[dict]) -> float | None:
    eu_rate = None
    for rate in rates:
        if rate["region_code"] == "PL":
            return float(rate["rate"]["amount"])
        if rate["region_code"] == "EUR_EU":
            eu_rate = float(rate["rate"]["amount"])
    return eu_rate


def _parse_raw_listing(raw: dict) -> Listing:
    shipping_cost = _extract_shipping_cost(raw["shipping"]["rates"])
    return Listing.model_validate(
        {
            "source_id": str(raw["id"]),
            "source": Source.REVERB,
            "link": raw["_links"]["web"]["href"],
            "make": raw["make"],
            "title": raw["title"],
            "year": raw["year"],
            "condition": raw["condition"]["slug"],
            "price": float(raw["buyer_price"]["amount"]),
            "shipping_cost": shipping_cost,
            "currency": raw["buyer_price"]["currency"],
            "tax_included": raw["buyer_price"]["tax_included"],
            "created_at": raw["created_at"],
        }
    )


def get_listings(query: str, token: str, per_page: int = 50) -> list[Listing]:
    raw_listings: list[dict] = _fetch_raw_listings(query, token, per_page)["listings"]
    parsed_listings: list[Listing] = [
        _parse_raw_listing(listing) for listing in raw_listings
    ]
    logger.info(
        "reverb_parse_complete",
        query=query,
        fetched=len(raw_listings),
        parsed=len(parsed_listings),
    )
    return parsed_listings
