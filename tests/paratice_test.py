from app.schemas import LeadFields
from pydantic import ValidationError

payload = {
    "travelers": 4,
    "location": "Skardu",
    "approved_discount": 30
}
try:
    LeadFields.model_validate(payload)
except ValidationError as e:
    print(e)