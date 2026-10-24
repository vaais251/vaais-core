from app.agent.tool_schemas import LOOKUP_OFFERING_SCHEMA
from app.agent.tools import lookup_offering
import json
from app.agent.trace import TraceEvent


def request_model_step(
    client,
    model_name: str,
    question: str
):
    internation = client.interactions.create(
        model=model_name,
        input=question,
        tools=[LOOKUP_OFFERING_SCHEMA]
    )
    return internation


def get_function_calls(interaction) -> list:
    return [
        step
        for step in interaction.steps
        if step.type == "function_call"
    ]


def dispatch_tool(call) -> dict:
    if call.name == "lookup_offering":
        return lookup_offering(call.arguments)
    else:
        return {"status": "unknown_tool"}


def run_agent(client, model_name: str, question: str):
    model_calls = 0
    tool_steps = 0
    trace_events = []

    interaction = request_model_step(client, model_name, question)
    model_calls += 1

    while True:
        calls = get_function_calls(interaction)

        if len(calls) == 0:
            trace_events.append(
                TraceEvent(
                    step_index=len(trace_events),
                    actor="model",
                    event="final_answer",
                    status="completed",
                )
            )
            return {
                "status": "final",
                "interaction": interaction,
                "trace_events": trace_events,
            }

        for call in calls:
            trace_events.append(
                TraceEvent(
                    step_index=len(trace_events),
                    actor="model",
                    event="tool_requested",
                    tool_name=call.name,
                    status="requested",
                )
            )

        if len(calls) > 1:
            trace_events.append(
                TraceEvent(
                    step_index=len(trace_events),
                    actor="application",
                    event="unsupported_multiple_calls",
                    status="rejected",
                )
            )
            return {
                "status": "unsupported_multiple_calls",
                "trace_events": trace_events,
            }

        call = calls[0]

        if call.name != "lookup_offering":
            trace_events.append(
                TraceEvent(
                    step_index=len(trace_events),
                    actor="application",
                    event="unknown_tool",
                    tool_name=call.name,
                    status="rejected",
                )
            )
            return {
                "status": "unknown_tool",
                "trace_events": trace_events,
            }

        if tool_steps >= 2:
            trace_events.append(
                TraceEvent(
                    step_index=len(trace_events),
                    actor="application",
                    event="tool_budget_exhausted",
                    tool_name=call.name,
                    status="rejected",
                )
            )
            return {
                "status": "tool_budget_exhausted",
                "trace_events": trace_events,
            }

        if model_calls >= 3:
            trace_events.append(
                TraceEvent(
                    step_index=len(trace_events),
                    actor="application",
                    event="model_budget_exhausted",
                    tool_name=call.name,
                    status="rejected",
                )
            )
            return {
                "status": "model_budget_exhausted",
                "trace_events": trace_events,
            }

        result = build_function_result(call)
        trace_events.append(
            TraceEvent(
                step_index=len(trace_events),
                actor="tool",
                event="tool_result",
                tool_name=result["name"],
                status=result["result"].get("status", "success"),
            )
        )
        tool_steps += 1

        interaction = continue_after_tool(
            client, model_name, interaction, result
        )
        model_calls += 1


def build_function_result(call) -> dict:
    result = dispatch_tool(call)
    return {
        "type": "function_result",
        "name": call.name,
        "call_id": call.id,
        "result": result
    }


def continue_after_tool(
    client,
    model_name: str,
    interaction,
    function_result: dict
):
    return client.interactions.create(
        model=model_name,
        previous_interaction_id=interaction.id,
        input=[function_result],
        tools=[LOOKUP_OFFERING_SCHEMA]
    )
