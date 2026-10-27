from pydantic import ValidationError
from app.services.model_extraction import validate_extraction_payload
from app.schemas import ExtractionResponse
from app.providers.base import ProviderOutputError, ProviderUnavailableError
from app.prompts import EXTRACTION_SYSTEM_PROMPT


class GeminiProvider:
    def __init__(self, api_key: str, model: str, client=None):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required in gemini mode")
        self.model = model
        if client is None:
            from google import genai
            client = genai.Client(api_key=api_key)
        self.client = client

    def extract(self, raw_text: str) -> ExtractionResponse:
        try:
            result = self.client.models.generate_content(
                model=self.model,
                contents=raw_text,
                config={
                    "system_instruction": EXTRACTION_SYSTEM_PROMPT,
                    "response_mime_type": "application/json",
                    # Preserve Pydantic constraints without converting to the
                    # SDK's narrower Schema model (no exclusiveMinimum).
                    "response_json_schema": ExtractionResponse.model_json_schema(),
                },
            )
        except Exception:
            # Deliberately hide SDK exception contents; they may contain secrets.
            raise ProviderUnavailableError(
                "Gemini API request failed") from None

        try:
            if result.parsed is not None:
                return validate_extraction_payload(result.parsed)
            if not result.text:
                raise ValueError("No structured response")
            return validate_extraction_payload(result.text)
        except (ValidationError, ValueError, TypeError, AttributeError):
            raise ProviderOutputError(
                "Gemini returned invalid structured output") from None
