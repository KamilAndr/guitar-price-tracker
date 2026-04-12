import requests
import structlog
from guitar_price_tracker.models.listing import Listing, Source


logger = structlog.get_logger(__name__)
REVERB_MAX_PAGES = 50
CONDITION_MAP = {
    "mint-inventory": "mint",
}


def _fetch_raw_listings(
    query: str, token: str, page: int = 1, per_page: int = 50
) -> dict:
    response = requests.get(
        "https://api.reverb.com/api/listings?category_uuid=dfd39027-d134-4353-b9e4-57dc6be791b9",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/hal+json",
            "Accept-Version": "3.0",
            "X-Display-Currency": "EUR",
        },
        params={
            "query": query,
            "exclude_auctions": "true",
            "page": page,
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


def _normalize_condition(slug: str) -> str:
    return CONDITION_MAP.get(slug, slug)


def _parse_raw_listing(raw: dict) -> Listing:
    shipping_cost = _extract_shipping_cost(raw["shipping"]["rates"])
    return Listing.model_validate(
        {
            "source_id": str(raw["id"]),
            "source": Source.REVERB,
            "link": raw["_links"]["web"]["href"],
            "make": raw["make"],
            "source_model": raw["model"],
            "title": raw["title"],
            "year": raw["year"],
            "condition": _normalize_condition(raw["condition"]["slug"]),
            "price": float(raw["buyer_price"]["amount"]),
            "shipping_cost": shipping_cost,
            "currency": raw["buyer_price"]["currency"],
            "tax_included": raw["buyer_price"]["tax_included"],
            "created_at": raw["created_at"],
        }
    )


def get_listings(query: str, token: str, per_page: int = 50) -> list[Listing]:
    parsed_listings = []
    for page in range(1, REVERB_MAX_PAGES + 1):
        raw_listings = _fetch_raw_listings(query, token, page, per_page)
        for raw in raw_listings["listings"]:
            try:
                parsed_listings.append(_parse_raw_listing(raw))
            except Exception as e:
                logger.warning(
                    "reverb_parse_failed", listing_id=raw.get("id"), error=str(e)
                )
        if "next" not in raw_listings.get("_links", {}):
            break
    return parsed_listings


# if __name__ == "__main__":
#     import os
#     from dotenv import load_dotenv
#     load_dotenv()
#     token = os.getenv("REVERB_API_TOKEN")
#     listings = get_listings("American Professional II Stratocaster", token, per_page=50)
#     print(f"Total listings fetched: {len(listings)}")
#     print(f"First: {listings[0].title} - {listings[0].price} {listings[0].currency}")
#     print(f"Last: {listings[-1].title} - {listings[-1].price} {listings[-1].currency}")
