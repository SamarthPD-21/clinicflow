from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .routers import appointments, doctors, patients

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Appointment scheduling for small clinics: doctors, patients and bookings.",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)

# Request count / latency histograms per route, scraped by Prometheus.
Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)


@app.get("/", tags=["meta"])
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["meta"])
def health():
    """Liveness: the process is up and serving requests."""
    return {"status": "UP"}


@app.get("/ready", tags=["meta"])
def ready(db: Session = Depends(get_db)):
    """Readiness: the database is reachable, so traffic can be routed here."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "READY"}
