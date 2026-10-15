def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_root_identifies_service(client):
    assert client.get("/").json()["service"] == "ClinicFlow API"


def test_metrics_exposed_in_prometheus_format(client):
    client.get("/api/doctors")
    body = client.get("/metrics").text
    assert "http_requests_total" in body
    assert 'handler="/api/doctors"' in body


def test_booking_metrics_are_counted(client, doctor, patient):
    body = {"doctor_id": doctor["id"], "patient_id": patient["id"], "scheduled_at": "2030-02-01T10:00:00"}
    client.post("/api/appointments", json=body)
    client.post("/api/appointments", json=body)  # same slot -> conflict
    metrics = client.get("/metrics").text
    assert 'clinicflow_appointments_booked_total{specialty="General Medicine"}' in metrics
    assert "clinicflow_booking_conflicts_total" in metrics
