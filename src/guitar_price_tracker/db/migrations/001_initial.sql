CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    source_id TEXT NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('reverb', 'ebay', 'thomann')),
    link TEXT NOT NULL,
    make TEXT NOT NULL,
    title TEXT NOT NULL,
    year TEXT,
    condition TEXT NOT NULL,
    listed_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(source_id, source)
);

CREATE TABLE price_observations (
    id SERIAL PRIMARY KEY,
    listing_id INT NOT NULL,
    observed_date DATE NOT NULL DEFAULT CURRENT_DATE,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    price NUMERIC(10, 2) NOT NULL CHECK(price > 0),
    shipping_cost NUMERIC(10, 2) CHECK(shipping_cost >= 0),
    currency VARCHAR(3) NOT NULL,
    tax_included BOOLEAN NOT NULL,
    CONSTRAINT fk_listing
        FOREIGN KEY(listing_id)
        REFERENCES listings(id),
    UNIQUE(listing_id, observed_date)
);