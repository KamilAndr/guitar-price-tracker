import psycopg2
from guitar_price_tracker.models.listing import Listing


class Repository:
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

    _MODEL_UPSERT_QUERY = """
        INSERT INTO models (model_name)
        VALUES (%(model_name)s)
        ON CONFLICT (model_name) DO UPDATE SET
            model_name = model_name
        RETURNING id, model_name;
    """

    _GET_UNMATCHED_LISTINGS_QUERY = """
        SELECT
          id,
          title,
          source_model
        FROM listings
        WHERE reference_model_id IS NULL
    """

    _UPDATE_UNMATCHED_LISTING_QUERY = """
        UPDATE listings
        SET reference_model_id = %(reference_model_id)s
        WHERE id = %(id)s
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

    def _upsert_model(self, cursor, model: str) -> tuple[int, str]:
        cursor.execute(self._MODEL_UPSERT_QUERY, model)
        return cursor.fetchone()

    def save_models(self, models: list[str]) -> list[tuple[int, str]]:
        try:
            with self.conn.cursor() as cursor:
                inserted_models = [
                    self._upsert_model(cursor, model) for model in models
                ]
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        return inserted_models

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

    def get_unmatched_listings(self) -> list[tuple[int, str, str | None]]:
        with self.conn.cursor() as cursor:
            cursor.execute(self._GET_UNMATCHED_LISTINGS_QUERY)
            return cursor.fetchall()

    def update_unmatched_listings(
        self, matched_listings: list[tuple[int, int]]
    ) -> None:
        try:
            with self.conn.cursor() as cursor:
                for listing_id, reference_model_id in matched_listings:
                    cursor.execute(
                        self._UPDATE_UNMATCHED_LISTING_QUERY,
                        {"id": listing_id, "reference_model_id": reference_model_id},
                    )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()
