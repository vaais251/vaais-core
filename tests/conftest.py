import pytest


@pytest.fixture(autouse=True)
def offline_provider(monkeypatch):
    """Keep normal tests independent of local .env and external API quotas."""
    monkeypatch.setenv("PROVIDER_MODE", "mock")
