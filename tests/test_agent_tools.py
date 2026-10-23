from unittest.mock import patch

import pytest

from app.agent.tools import lookup_offering
from app.tools.look_up import lookup_offer


def test_successful_tool_call():
    assert lookup_offering({"offering_id": "101"}) == lookup_offer("101")


def test_unknown_tool_offering():
    assert lookup_offering({"offering_id": "999"}) == {"status": "not_found"}


@pytest.mark.parametrize(
    "arguments",
    [
        {"offering_id": 101},
        {"offering_id": "101", "path": "../.env"},
        {"path": "../.env"},
        {},
        {"offering_id": None},
        {"offering_id": ""},
        {"offering_id": "   "},
        {"offering_id": []},
        {"offering_id": {}},
        {"offering_id": True},
        None,
        [],
        '{"offering_id":',
    ],
)
def test_invalid_tool_arguments(arguments):
    with patch("app.agent.tools.lookup_offer") as lookup:
        assert lookup_offering(arguments) == {"status": "invalid_argument"}
        lookup.assert_not_called()
