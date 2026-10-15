from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from prometheus_client import Counter
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..config import settings
from ..db import get_db
from ..models import Appointment, Doctor, Patient
from ..schemas import AppointmentCreate, AppointmentOut, AppointmentStatus, AppointmentUpdate, StatsOut

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

BOOKINGS = Counter("clinicflow_appointments_booked_total", "Appointments booked", ["specialty"])
CONFLICTS = Counter("clinicflow_booking_conflicts_total", "Bookings rejected because the doctor's slot was taken")

# Appointments in these states still occupy the doctor's slot.
BLOCKING_STATUSES = ("SCHEDULED", "CHECKED_IN")


def to_out(appt: Appointment) -> AppointmentOut:
    return AppointmentOut(
        id=appt.id,
        doctor_id=appt.doctor_id,
        patient_id=appt.patient_id,
        scheduled_at=appt.scheduled_at,
        reason=appt.reason,
        status=appt.status,
        created_at=appt.created_at,
        doctor_name=appt.doctor.name,
        doctor_specialty=appt.doctor.specialty,
        patient_name=appt.patient.full_name,
    )


def clinic_now() -> datetime:
    return datetime.now(ZoneInfo(settings.clinic_timezone)).replace(tzinfo=None)


def naive(dt: datetime) -> datetime:
    # The clinic works in local wall-clock time, so drop any offset the client sent.
    return dt.replace(tzinfo=None, second=0, microsecond=0)


def get_appointment_or_404(appointment_id: int, db: Session) -> Appointment:
    options = [joinedload(Appointment.doctor), joinedload(Appointment.patient)]
    appt = db.get(Appointment, appointment_id, options=options)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


def validate_refs(db: Session, doctor_id: int, patient_id: int) -> None:
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=422, detail="Doctor does not exist")
    if not doctor.active:
        raise HTTPException(status_code=422, detail="Doctor is not accepting appointments")
    if not db.get(Patient, patient_id):
        raise HTTPException(status_code=422, detail="Patient does not exist")


def ensure_slot_free(db: Session, doctor_id: int, scheduled_at: datetime, exclude_id: int | None = None) -> None:
    slot = timedelta(minutes=settings.slot_minutes)
    query = select(Appointment.id).where(
        Appointment.doctor_id == doctor_id,
        Appointment.status.in_(BLOCKING_STATUSES),
        Appointment.scheduled_at > scheduled_at - slot,
        Appointment.scheduled_at < scheduled_at + slot,
    )
    if exclude_id is not None:
        query = query.where(Appointment.id != exclude_id)
    if db.scalars(query).first() is not None:
        CONFLICTS.inc()
        raise HTTPException(status_code=409, detail="Doctor already has an appointment in this slot")


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    day: date | None = None,
    doctor_id: int | None = None,
    status: AppointmentStatus | None = None,
    db: Session = Depends(get_db),
):
    query = (
        select(Appointment)
        .options(joinedload(Appointment.doctor), joinedload(Appointment.patient))
        .order_by(Appointment.scheduled_at)
    )
    if day is not None:
        start = datetime.combine(day, time.min)
        query = query.where(Appointment.scheduled_at >= start, Appointment.scheduled_at < start + timedelta(days=1))
    if doctor_id is not None:
        query = query.where(Appointment.doctor_id == doctor_id)
    if status is not None:
        query = query.where(Appointment.status == status)
    return [to_out(a) for a in db.scalars(query)]


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    now = clinic_now()
    today_start = datetime.combine(now.date(), time.min)
    rows = db.execute(select(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status)).all()
    by_status = dict(rows)
    finished = by_status.get("COMPLETED", 0) + by_status.get("NO_SHOW", 0)
    return StatsOut(
        doctors=db.scalar(select(func.count(Doctor.id)).where(Doctor.active.is_(True))) or 0,
        patients=db.scalar(select(func.count(Patient.id))) or 0,
        appointments_today=db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.scheduled_at >= today_start,
                Appointment.scheduled_at < today_start + timedelta(days=1),
            )
        )
        or 0,
        upcoming=db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.scheduled_at >= now, Appointment.status.in_(BLOCKING_STATUSES)
            )
        )
        or 0,
        by_status=by_status,
        completion_rate=round(by_status.get("COMPLETED", 0) / finished, 2) if finished else 0.0,
    )


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return to_out(get_appointment_or_404(appointment_id, db))


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    validate_refs(db, payload.doctor_id, payload.patient_id)
    scheduled_at = naive(payload.scheduled_at)
    if payload.status in BLOCKING_STATUSES:
        ensure_slot_free(db, payload.doctor_id, scheduled_at)
    appt = Appointment(**payload.model_dump(exclude={"scheduled_at"}), scheduled_at=scheduled_at)
    db.add(appt)
    db.commit()
    out = to_out(get_appointment_or_404(appt.id, db))
    BOOKINGS.labels(specialty=out.doctor_specialty).inc()
    return out


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db)):
    appt = get_appointment_or_404(appointment_id, db)
    changes = payload.model_dump(exclude_unset=True)
    if "scheduled_at" in changes:
        changes["scheduled_at"] = naive(changes["scheduled_at"])

    doctor_id = changes.get("doctor_id", appt.doctor_id)
    patient_id = changes.get("patient_id", appt.patient_id)
    if "doctor_id" in changes or "patient_id" in changes:
        validate_refs(db, doctor_id, patient_id)
    slot_affected = {"doctor_id", "scheduled_at", "status"} & changes.keys()
    if slot_affected and changes.get("status", appt.status) in BLOCKING_STATUSES:
        ensure_slot_free(db, doctor_id, changes.get("scheduled_at", appt.scheduled_at), exclude_id=appt.id)

    for key, value in changes.items():
        setattr(appt, key, value)
    db.commit()
    db.expire_all()
    return to_out(get_appointment_or_404(appointment_id, db))


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db.delete(get_appointment_or_404(appointment_id, db))
    db.commit()
