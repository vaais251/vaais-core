from app.schemas import ExtractionResponse


def validate_extraction_payload(payload: str | dict) -> ExtractionResponse:
    if isinstance(payload, str):
        response = ExtractionResponse.model_validate_json(payload)
    else:
        response = ExtractionResponse.model_validate(payload)

    for lead in response.leads:
        if lead.price is not None:
            raise ValueError(
                "price must be null until verified by an authorized business source"
            )

    return response