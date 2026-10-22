import json

import pytest

from app.services.model_extraction import validate_extraction_payload


@pytest.mark.parametrize("as_json", [False, True])
@pytest.mark.parametrize("price", [None, 2000.0])
def test_price_policy_for_each_payload_format(as_json, price):
    payload = {"leads": [{"price": None}, {"price": price}], "errors": []}
    if as_json:
        payload = json.dumps(payload)

    if price is not None:
        with pytest.raises(ValueError, match="price must be null"):
            validate_extraction_payload(payload)
    else:
        response = validate_extraction_payload(payload)
        assert len(response.leads) == 2
        assert all(lead.price is None for lead in response.leads)
