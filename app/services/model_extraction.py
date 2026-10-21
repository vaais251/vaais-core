from app.schemas import ExtractionResponse
def validate_extraction_payload(payload: str | dict) -> ExtractionResponse:
    if isinstance(payload,str):
        return ExtractionResponse.model_validate_json(payload)
    return ExtractionResponse.model_validate(payload)