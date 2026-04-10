CREATE TABLE reference_models (
    id SERIAL PRIMARY KEY,
    reference_model TEXT NOT NULL,
    UNIQUE(reference_model)
);

ALTER TABLE listings
ADD COLUMN source_model TEXT,
ADD COLUMN reference_model_id INT
    CONSTRAINT fk_ref_model REFERENCES reference_models(id)
    ON DELETE SET NULL;