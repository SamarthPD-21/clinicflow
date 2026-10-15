from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Patient
from ..schemas import PatientCreate, PatientOut, PatientUpdate

router = APIRouter(prefix="/api/patients", tags=["patients"])


def get_patient_or_404(patient_id: int, db: Session) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("", response_model=list[PatientOut])
def list_patients(q: str | None = None, db: Session = Depends(get_db)):
    query = select(Patient).order_by(Patient.full_name)
    if q:
        like = f"%{q}%"
        query = query.where(or_(Patient.full_name.ilike(like), Patient.phone.ilike(like)))
    return list(db.scalars(query))


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    return get_patient_or_404(patient_id, db)


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    patient = get_patient_or_404(patient_id, db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db.delete(get_patient_or_404(patient_id, db))
    db.commit()
