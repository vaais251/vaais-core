from app.services.model_extraction import validate_extraction_payload
from app.schemas import LeadFields, AssistResponse


def process_assistance(request, provider, request_id, agent_runner=None,):

    unvalidate_response = provider.extract(request.inquiry_text)
    response = validate_extraction_payload(unvalidate_response)

    if response.leads:
        parsed_fields = response.leads[0]
    else:
        parsed_fields = LeadFields(needs_review=True)
    question = request.inquiry_text

    question = request.inquiry_text

    if request.offering_id:
        question += f"\nOffering ID: {request.offering_id}"

    result = agent_runner(question=question)
    if result is not None:

        tools_requested = [
            item.tool_name
            for item in result.get("trace_events", [])
            if item.event == "tool_requested"
        ]
        tool_summary = {
            "tools_requested": tools_requested,
            "agent_status": result["status"]
        }
        interaction = result.get("interaction")
        answer = getattr(interaction, "output_text", None)

        return_response = AssistResponse(answer=answer,
                                         parsed_fields=parsed_fields,
                                         tool_summary=tool_summary,
                                         request_id=request_id)
        return return_response
    else:
        AssistResponse(answer="Agent failed to run",
                       request_id=request_id)
