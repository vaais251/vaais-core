import pytest
from app.providers.factory import get_provider
from unittest.mock import MagicMock
from app.providers.base import ProviderOutputError
from app.providers.gemini import GeminiProvider
# from fastapi.testclient import TestClient


fake_client=MagicMock()

fake_client.models.generate_content.return_value.parsed = None
fake_client.models.generate_content.return_value.text = '{"leads": [invalid json}'

prov=GeminiProvider("fake api key","test",fake_client)

def test_out():
    with pytest.raises(ProviderOutputError):
        prov.extract("fake test")
    
