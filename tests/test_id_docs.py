import pytest

@pytest.mark.asyncio
async def test_id_verify(client):
    d = await client.post("/api/documents", json={"raw_text": "name: Jane Doe; dob: 1990-01-01; id: XY-9"})
    did = d.json()["id"]
    f = await client.get(f"/api/documents/{did}/fields")
    assert f.status_code == 200
    v = await client.post(f"/api/documents/{did}/verify", json={"approve": True})
    assert v.json()["verification_status"] in ("verified", "manual_review")
