import json
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "catalog.json"


def load_catalog() -> list:
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        offers = json.load(f)
    return offers

def lookup_offer(offer_id:str)->dict:
    if not isinstance(offer_id,str) or not offer_id or not offer_id.strip():
        return {"status":"invalid_argument"}
    offers=load_catalog()

    for offer in offers:
        if offer.get("offer_id") == offer_id:
            return offer
    
    return  {"status": "not_found"}

        