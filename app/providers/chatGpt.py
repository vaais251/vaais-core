from app.schemas import ExtractionResponse
# from pydantic import ValidationError

def validate_extraction_payload(payload: dict) -> ExtractionResponse:
    
    return ExtractionResponse.model_validate(payload)
    