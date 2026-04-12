import os
import yaml
from dotenv import load_dotenv
from guitar_price_tracker.db.repository import Repository
from guitar_price_tracker.matching.keywords import match_guitar_model
from guitar_price_tracker.ingestion.reverb import get_listings

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("REVERB_API_TOKEN")
    database_url = os.getenv("DATABASE_URL")

    with open("./config/guitar_models.yaml") as f:
        guitar_models_config = yaml.safe_load(f)
        global_must_exclude = guitar_models_config["global_must_exclude"]
        guitar_models = guitar_models_config["guitar_models"]

    repo = Repository(database_url)

    for model in guitar_models:
        model["must_exclude"] += global_must_exclude
        listings = get_listings(model["reference_model"], token)
        repo.save_listings(listings)

    inserted_models = repo.save_models(
        [model["reference_model"] for model in guitar_models]
    )
    reference_models = {
        reference_model: model_id for model_id, reference_model in inserted_models
    }

    unmatched_listings = repo.get_unmatched_listings()
    matched_listings = []
    for listing in unmatched_listings:
        listing_id, title, source_model = listing
        matched_model = match_guitar_model(title, source_model, guitar_models)
        if matched_model:
            matched_listings.append(
                (listing_id, reference_models[matched_model["reference_model"]])
            )

    repo.update_unmatched_listings(matched_listings)

    repo.close()
