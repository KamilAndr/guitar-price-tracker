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
        guitar_models = yaml.safe_load(f)["guitar_models"]

    repo = Repository(database_url)

    for model in guitar_models:
        listings = get_listings(model["reference_model"], token)
        repo.save_listings(listings)

    inserted_models = repo.save_models([model["reference_model"] for model in guitar_models])

    #TODO: add matching logic

    repo.close()