def test_create_patient_and_search(client, patient):
    client.post("/api/patients", json={"full_name": "Zoya Khan", "phone": "+91 90000 00002"})
    results = client.get("/api/patients", params={"q": "asha"}).json()
    assert [p["full_name"] for p in results] == ["Asha Verma"]


def test_patient_phone_must_be_numeric(client):
    response = client.post("/api/patients", json={"full_name": "Bad Phone", "phone": "call me"})
    assert response.status_code == 422


def test_update_patient(client, patient):
    response = client.put(f"/api/patients/{patient['id']}", json={"email": "asha@example.com"})
    assert response.status_code == 200
    assert response.json()["email"] == "asha@example.com"
