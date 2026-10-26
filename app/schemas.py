from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, ConfigDict


class ExtractRequest(BaseModel):
    text: str = Field(min_length=10, max_length=1000)


class LeadFields(BaseModel):
    model_config = ConfigDict(extra='forbid')
    travelers: Optional[int] = Field(default=None, gt=0)
    dates: Optional[date] = None
    location: Optional[str] = None
    duration: Optional[int] = Field(default=None, gt=0)
    origin_country: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    needs_review: Optional[bool] = True


class ExtractionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    leads: list[LeadFields]
    errors: list[str] = Field(default_factory=list)


class AssistRequest(BaseModel):
    inquiry_text: str = Field(min_length=10, max_length=1000)
    offering_id: Optional[str] = None
    model_config = ConfigDict(extra='forbid')


class AssistResponse(BaseModel):
    answer: str
    parsed_fields: LeadFields
    tool_summary: Optional[dict] = None
    needs_review: bool = False
    request_id: str
