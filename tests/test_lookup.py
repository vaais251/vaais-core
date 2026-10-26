# Verify that duration_days equals 15.
# Verify that destination equals "skardu"
import pytest
from app.tools.look_up import lookup_offer


def test_lookup_offer_104():
    result = lookup_offer('104')
    assert result["offer_id"] == '104'
    assert result["destination"] == "skardu"
    assert result["duration_days"] == 15


def test_lookup_unknown_offer():
    result = lookup_offer("999")
    assert result["status"] == 'not_found'


def test_lookup_unavailable_offer():
    result = lookup_offer("103")
    assert result["offer_id"] == "103"
    assert result["status"] == "unavailable"


@pytest.mark.parametrize("invalid_id", [101, None, "", "   ", "101", "../.env"]
                         )
def test_invalid_offer_id(invalid_id):
    offer = lookup_offer(invalid_id)
    if invalid_id in [101, None, "", "   ",]:
        assert offer["status"] == "invalid_argument"
    elif invalid_id == "101":
        assert offer["status"] == "available"
    elif invalid_id == "../.env":
        assert offer["status"] == "not_found"
