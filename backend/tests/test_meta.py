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
