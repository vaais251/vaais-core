
from typing import Callable

from app.schemas import AssistRequest, AssistResponse, LeadFields
from app.services.model_extraction import validate_extraction_payload
from app.providers.base import ExtractionProvider


def process_assistance(
    request: AssistRequest,
    provider: ExtractionProvider,
    request_id: str,
    agent_runner: Callable[..., dict] | None = None,
) -> AssistResponse:

    # 1. Extract and validate the customer inquiry
    raw_response = provider.extract(request.inquiry_text)

    response = validate_extraction_payload(
        raw_response.model_dump()
    )

    # 2. Preserve unknown fields
    parsed_fields = (
        response.leads[0]
        if response.leads
        else LeadFields(needs_review=True)
    )

    # 3. Determine whether human review is needed
    missing_fields = any(
        getattr(parsed_fields, field) is None
        for field in (
            "travelers",
            "dates",
            "location",
            "duration",
            "origin_country",
        )
    )

    needs_review = (
        not response.leads
        or bool(response.errors)
        or parsed_fields.needs_review is not False
        or missing_fields
    )

    # 4. Prepare the agent question
    question = request.inquiry_text

    if request.offering_id:
        question += f"\nOffering ID: {request.offering_id}"

    # 5. Handle an unavailable agent runner
    if agent_runner is None:
        return AssistResponse(
            answer=(
                "Inquiry received. Offering details "
                "have not been verified."
            ),
            parsed_fields=parsed_fields,
            tool_summary={
                "agent_status": "not_run",
                "tools_requested": [],
                "tool_results": [],
            },
            needs_review=True,
            request_id=request_id,
        )

    # 6. Run the existing bounded agent
    result = agent_runner(question=question)

    if not isinstance(result, dict):
        result = {
            "status": "agent_unavailable",
            "trace_events": [],
        }

    events = result.get("trace_events", []) or []
    agent_status = result.get("status", "unknown")

    # 7. Build a serializable tool summary
    tool_summary = {
        "agent_status": agent_status,
        "tools_requested": [
            event.tool_name
            for event in events
            if event.event == "tool_requested"
        ],
        "tool_results": [
            {
                "tool_name": event.tool_name,
                "status": event.status,
            }
            for event in events
            if event.actor == "tool"
        ],
    }

    # 8. Extract final answer safely
    interaction = result.get("interaction")
    final_text = getattr(interaction, "output_text", None)

    completed = (
        agent_status == "final"
        and isinstance(final_text, str)
        and bool(final_text.strip())
    )

    if completed:
        answer = final_text.strip()
    else:
        answer = (
            "The automated response could not be completed. "
            "Human review is required."
        )

    # 9. Return the typed API response
    return AssistResponse(
        answer=answer,
        parsed_fields=parsed_fields,
        tool_summary=tool_summary,
        needs_review=needs_review or not completed,
        request_id=request_id,
    )
