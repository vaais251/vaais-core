from types import SimpleNamespace
from app.agent.loop import dispatch_tool
import pytest
call = SimpleNamespace(
    name="lookup_offering",
    arguments={"offering_id": "104"}
)

@pytest.mark.parametrize("call",[SimpleNamespace(
    name="lookup_offering",
    arguments={"offering_id": "104"}
),SimpleNamespace(
    name="lookup_offering",
    arguments={"offering_id": 123}
),SimpleNamespace(
    name="delete_database",
    arguments={"offering_id": "14"}
)])
def test_tools(call):
    out=dispatch_tool(call)
    if call.arguments["offering_id"]=="104":
        assert out["offer_id"]=='104'
    elif call.arguments["offering_id"]==123:
        assert out=={"status": "invalid_argument"}
    elif call.name=='delete_database':
        assert out=={"status": "unknown_tool"}
