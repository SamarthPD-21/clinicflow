from datetime import datetime, timedelta

SLOT = "2030-01-15T10:00:00"


def book(client, doctor, patient, when=SLOT, **extra):
    return client.post(
        "/api/appointments",
        json={"doctor_id": doctor["id"], "patient_id": patient["id"], "scheduled_at": when, **extra},
    )


def test_book_appointment_returns_names(client, doctor, patient):
    response = book(client, doctor, patient, reason="Fever")
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "SCHEDULED"
    assert body["doctor_name"] == "Dr. Test"
    assert body["patient_name"] == "Asha Verma"


def test_double_booking_same_slot_is_rejected(client, doctor, patient):
    assert book(client, doctor, patient).status_code == 201
    clash = book(client, doctor, patient, when="2030-01-15T10:15:00")
    assert clash.status_code == 409


def test_back_to_back_slots_are_allowed(client, doctor, patient):
    assert book(client, doctor, patient).status_code == 201
    assert book(client, doctor, patient, when="2030-01-15T10:30:00").status_code == 201


def test_cancelled_appointment_frees_the_slot(client, doctor, patient):
    first = book(client, doctor, patient).json()
    client.put(f"/api/appointments/{first['id']}", json={"status": "CANCELLED"})
    assert book(client, doctor, patient).status_code == 201


def test_booking_unknown_doctor_is_422(client, patient):
    response = book(client, {"id": 999}, patient)
    assert response.status_code == 422


def test_inactive_doctor_cannot_be_booked(client, doctor, patient):
    client.put(f"/api/doctors/{doctor['id']}", json={"active": False})
    assert book(client, doctor, patient).status_code == 422


def test_filter_appointments_by_day_and_status(client, doctor, patient):
    book(client, doctor, patient)
    book(client, doctor, patient, when="2030-01-16T09:00:00")
    assert len(client.get("/api/appointments", params={"day": "2030-01-15"}).json()) == 1
    assert len(client.get("/api/appointments", params={"status": "SCHEDULED"}).json()) == 2


def test_reschedule_into_taken_slot_conflicts(client, doctor, patient):
    book(client, doctor, patient)
    second = book(client, doctor, patient, when="2030-01-15T11:00:00").json()
    response = client.put(f"/api/appointments/{second['id']}", json={"scheduled_at": SLOT})
    assert response.status_code == 409


def test_delete_appointment(client, doctor, patient):
    appt = book(client, doctor, patient).json()
    assert client.delete(f"/api/appointments/{appt['id']}").status_code == 204
    assert client.get(f"/api/appointments/{appt['id']}").status_code == 404


def test_stats_counts_today_and_completion_rate(client, doctor, patient):
    today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    done = book(client, doctor, patient, when=today.isoformat()).json()
    book(client, doctor, patient, when=(today + timedelta(hours=1)).isoformat(), status="NO_SHOW")
    client.put(f"/api/appointments/{done['id']}", json={"status": "COMPLETED"})

    stats = client.get("/api/appointments/stats").json()
    assert stats["doctors"] == 1
    assert stats["patients"] == 1
    assert stats["appointments_today"] == 2
    assert stats["by_status"] == {"COMPLETED": 1, "NO_SHOW": 1}
    assert stats["completion_rate"] == 0.5
