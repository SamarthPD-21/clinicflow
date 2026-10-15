import os

# Point settings at SQLite before the app is imported so nothing ever touches Postgres.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def doctor(client):
    return client.post("/api/doctors", json={"name": "Dr. Test", "specialty": "General Medicine", "room": "1"}).json()


@pytest.fixture()
def patient(client):
    return client.post("/api/patients", json={"full_name": "Asha Verma", "phone": "+91 90000 00001"}).json()
