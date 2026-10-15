def test_create_and_list_doctors(client):
    created = client.post("/api/doctors", json={"name": "Dr. Kumar", "specialty": "ENT", "room": "12"})
    assert created.status_code == 201
    assert created.json()["active"] is True

    listed = client.get("/api/doctors").json()
    assert [d["name"] for d in listed] == ["Dr. Kumar"]


def test_doctor_validation_rejects_empty_name(client):
    response = client.post("/api/doctors", json={"name": "", "specialty": "ENT"})
    assert response.status_code == 422


def test_update_and_filter_inactive_doctor(client, doctor):
    response = client.put(f"/api/doctors/{doctor['id']}", json={"active": False})
    assert response.status_code == 200
    assert response.json()["active"] is False
    assert client.get("/api/doctors", params={"active": True}).json() == []


def test_delete_doctor_then_404(client, doctor):
    assert client.delete(f"/api/doctors/{doctor['id']}").status_code == 204
    assert client.get(f"/api/doctors/{doctor['id']}").status_code == 404
