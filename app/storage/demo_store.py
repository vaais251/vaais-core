DEMO_LEADS = [
    {"lead_id": 1001, "destination": "skardu", "date": "2026-11-10",
        "travelers": 2, "needs_review": True, "status": "new"},
    {"lead_id": 1002, "destination": "hunzad", "date": "2026-10-10",
        "travelers": 4, "needs_review": False, "status": "reviewed"},
    {"lead_id": 1003, "destination": "shigar", "date": "2026-11-10",
        "travelers": 3, "needs_review": True, "status": "pending_review"}
]


def list_leads(limit: int, offset: int):
    return [lead.copy() for lead in DEMO_LEADS[offset: offset + limit]]
