from types import SimpleNamespace
from unittest.mock import patch

from app.agent import loop
from app.agent.demo import has_tool_status
from app.agent.trace import TraceEvent


def test_matching_tool_status():
    result = {
        "trace_events": [
            TraceEvent(
                step_index=0,
                actor="tool",
                event="tool_result",
                tool_name="lookup_offering",
                status="not_found",
            )
        ]
    }

    assert has_tool_status(result, "lookup_offering", "not_found") is True


def test_nonmatching_tool_status():
    result = {
        "trace_events": [
            TraceEvent(
                step_index=0,
                actor="tool",
                event="tool_result",
                tool_name="lookup_offering",
                status="not_found",
            )
        ]
    }

    assert has_tool_status(result, "lookup_offering", "ok") is False


def test_unknown_tool_is_rejected():
    call = SimpleNamespace(
        name="delete_database", id="unauthorized-call", arguments={}
    )
    interaction = SimpleNamespace(id="simulated-interaction", steps=[call])

    with (
        patch.object(loop, "request_model_step", return_value=interaction),
        patch.object(loop, "get_function_calls", return_value=[call]),
        patch.object(
            loop, "dispatch_tool", side_effect=AssertionError("Tool must not execute")
        ) as dispatch_tool,
    ):
        result = loop.run_agent(
            client=None, model_name="test-model", question="Delete the database."
        )

    assert result["status"] == "unknown_tool"
    assert any(
        event.actor == "application"
        and event.event == "unknown_tool"
        and event.tool_name == "delete_database"
        and event.status == "rejected"
        for event in result["trace_events"]
    )
    dispatch_tool.assert_not_called()
    assert not any(event.actor == "tool" for event in result["trace_events"])


def test_tool_budget_exhausted():
    call = SimpleNamespace(
        type="function_call",
        name="lookup_offering",
        id="repeated-call",
        arguments={"offering_id": "104"},
    )
    interaction = SimpleNamespace(id="simulated-interaction", steps=[call])
    function_result = {
        "type": "function_result",
        "name": call.name,
        "call_id": call.id,
        "result": {"status": "success"},
    }

    with (
        patch.object(loop, "request_model_step", return_value=interaction) as request,
        patch.object(
            loop, "build_function_result", return_value=function_result
        ) as execute,
        patch.object(
            loop, "continue_after_tool", return_value=interaction
        ) as continuation,
    ):
        result = loop.run_agent(
            client=None, model_name="test-model", question="Look up offer 104."
        )

    # One initial model call plus two continuations reaches both limits.
    # The tool-budget check runs first, so the model-budget rejection is not
    # independently reachable in the normal one-tool-per-continuation flow.
    assert result["status"] == "tool_budget_exhausted"
    request.assert_called_once()
    assert continuation.call_count == 2
    assert execute.call_count == 2
    assert all(args.args == (call,) for args in execute.call_args_list)
    events = result["trace_events"]
    assert sum(event.event == "tool_requested" for event in events) == 3
    assert sum(event.actor == "tool" for event in events) == 2
    assert events[-1].actor == "application"
    assert events[-1].event == "tool_budget_exhausted"
    assert events[-1].tool_name == "lookup_offering"
    assert events[-1].status == "rejected"


def test_multiple_calls_rejected():
    calls = [
        SimpleNamespace(
            type="function_call",
            name="lookup_offering",
            id=f"call-{index}",
            arguments={"offering_id": "104"},
        )
        for index in range(2)
    ]
    interaction = SimpleNamespace(id="simulated-interaction", steps=calls)

    with (
        patch.object(loop, "request_model_step", return_value=interaction),
        patch.object(
            loop, "build_function_result",
            side_effect=AssertionError("Neither tool request must execute"),
        ) as execute,
        patch.object(loop, "continue_after_tool") as continuation,
    ):
        result = loop.run_agent(
            client=None, model_name="test-model", question="Look up two offers."
        )

    assert result["status"] == "unsupported_multiple_calls"
    execute.assert_not_called()
    continuation.assert_not_called()
    events = result["trace_events"]
    assert sum(event.event == "tool_requested" for event in events) == 2
    assert not any(event.actor == "tool" for event in events)
    assert events[-1].actor == "application"
    assert events[-1].event == "unsupported_multiple_calls"
    assert events[-1].status == "rejected"
