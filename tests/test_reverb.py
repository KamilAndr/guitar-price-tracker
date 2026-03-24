import pytest
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from guitar_price_tracker.ingestion.reverb import _parse_raw_listing, get_listings


@pytest.fixture
def raw_listing():
    path = Path(__file__).parent / "fixtures" / "reverb_listing.json"
    return json.loads(path.read_text())


def test_parse_raw_listing_maps_fields_correctly(raw_listing):
    listing = _parse_raw_listing(raw_listing)
    assert listing.source_id == "91572606"
    assert listing.source == "reverb"
    assert (
        listing.link
        == "https://reverb.com/item/91572606-fender-american-professional-ii-stratocaster-brand-new-left-hand-lh-olympic-white-usa-lefty-handed-strat-electric-guitar"
    )
    assert listing.make == "Fender"
    assert (
        listing.title
        == "Fender American Professional II Stratocaster BRAND NEW LEFT HAND LH Olympic White USA Lefty Handed Strat Electric Guitar"
    )
    assert listing.year == "2022"
    assert listing.condition == "mint"
    assert listing.price == 2199.00
    assert listing.shipping_cost == 85.00
    assert listing.currency == "EUR"
    assert listing.tax_included is False
    assert listing.created_at == datetime(
        2025, 7, 27, 14, 31, 16, tzinfo=timezone(timedelta(hours=-5))
    )


def test_shipping_cost_none_when_no_matching_region(raw_listing):
    raw_listing["shipping"]["rates"] = [
        {"region_code": "US", "rate": {"amount": "200.0"}}
    ]
    listing = _parse_raw_listing(raw_listing)
    assert listing.shipping_cost is None


def test_shipping_prefers_pl_over_eu(raw_listing):
    raw_listing["shipping"]["rates"] = [
        {"region_code": "EUR_EU", "rate": {"amount": "85.00"}},
        {"region_code": "PL", "rate": {"amount": "40.00"}},
    ]
    listing = _parse_raw_listing(raw_listing)
    assert listing.shipping_cost == 40.00


def test_empty_year_becomes_none(raw_listing):
    raw_listing["year"] = ""
    listing = _parse_raw_listing(raw_listing)
    assert listing.year is None


@patch("guitar_price_tracker.ingestion.reverb._fetch_raw_listings")
def test_get_listings_empty_response(mock_fetch):
    mock_fetch.return_value = {"listings": [], "_links": {}}
    result = get_listings("query", "token")
    assert result == []
