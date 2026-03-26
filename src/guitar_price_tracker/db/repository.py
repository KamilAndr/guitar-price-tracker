import psycopg2
from guitar_price_tracker.models.listing import Listing


class ListingRepository:
    _LISTING_UPSERT_QUERY = """
        INSERT INTO listings (source_id, source, link, make, title, year, condition, listed_at)
        VALUES (%(source_id)s, %(source)s, %(link)s, %(make)s, %(title)s, %(year)s, %(condition)s, %(listed_at)s)
        ON CONFLICT (source_id, source) DO UPDATE SET
            link = EXCLUDED.link,
            make = EXCLUDED.make,
            title = EXCLUDED.title,
            year = EXCLUDED.year,
            condition = EXCLUDED.condition,
            listed_at = EXCLUDED.listed_at,
            updated_at = now()
        RETURNING id;
        """

    _PRICE_OBS_INSERT_QUERY = """
        INSERT INTO price_observations (listing_id, price, shipping_cost, currency, tax_included)
        VALUES (%(listing_id)s, %(price)s, %(shipping_cost)s, %(currency)s, %(tax_included)s)
        ON CONFLICT (listing_id, observed_date) DO UPDATE SET
            price = EXCLUDED.price,
            shipping_cost = EXCLUDED.shipping_cost,
            currency = EXCLUDED.currency,
            tax_included = EXCLUDED.tax_included;
        """

    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = psycopg2.connect(database_url)

    def _upsert_listing(self, cursor, listing: Listing) -> int:
        data = listing.model_dump()
        cursor.execute(self._LISTING_UPSERT_QUERY, data)
        listing_id = cursor.fetchone()[0]
        return listing_id

    def _insert_price_observation(
        self, cursor, listing_id: int, listing: Listing
    ) -> None:
        data = listing.model_dump()
        data["listing_id"] = listing_id
        cursor.execute(self._PRICE_OBS_INSERT_QUERY, data)

    def save_listings(self, listings: list[Listing]) -> None:
        try:
            with self.conn.cursor() as cursor:
                for listing in listings:
                    listing_id = self._upsert_listing(cursor, listing)
                    self._insert_price_observation(cursor, listing_id, listing)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()
