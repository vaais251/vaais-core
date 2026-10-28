import csv
from io import StringIO

from fastapi.testclient import TestClient
from app.main import app
from app.storage import demo_store

client = TestClient(app)

FIELDS = [
    "lead_id", "destination", "travelers",
    "date", "needs_review", "status"
]


def test_leads_pagination():
    all_leads = client.get("/leads").json()

    response = client.get("/leads?limit=1&offset=1")

    assert response.status_code == 200
    assert response.json() == all_leads[1:2]

    response = client.get("/leads?offset=999")
    assert response.status_code == 200
    assert response.json() == []


def test_invalid_pagination():
    assert client.get("/leads?limit=0").status_code == 422
    assert client.get("/leads?limit=101").status_code == 422
    assert client.get("/leads?offset=-1").status_code == 422


def test_csv_export():
    response = client.get("/leads/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]

    reader = csv.DictReader(StringIO(response.text))
    rows = list(reader)

    assert reader.fieldnames == FIELDS

    leads = client.get("/leads?limit=100").json()
    assert len(rows) == len(leads)

    for row, lead in zip(rows, leads):
        for field in FIELDS:
            expected = lead.get(field)
            assert row[field] == (
                "" if expected is None else str(expected)
            )


def test_csv_special_characters():
    special = {
        "lead_id": 9999,
        "destination": 'Skardu, "Upper"\nValley',
        "travelers": None,
        "date": None,
        "needs_review": True,
        "status": "new",
    }

    demo_store.DEMO_LEADS.append(special)
    try:
        response = client.get("/leads/export")
        assert response.status_code == 200

        rows = list(csv.DictReader(StringIO(response.text)))

        assert rows[-1]["destination"] == special["destination"]
        assert rows[-1]["travelers"] == ""
        assert rows[-1]["date"] == ""
    finally:
        demo_store.DEMO_LEADS.pop()
