import pytest

from app.services.model_extraction import validate_extraction_payload


def test_reject_unverified_price():
    payload = {
        "leads": [
            {
                "travelers": 4,
                "location": "Skardu",
                "price": 120000,
                "needs_review": False,
            }
        ],
        "errors": [],
    }

    with pytest.raises(ValueError):
        validate_extraction_payload(payload)
