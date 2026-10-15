from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AppointmentStatus = Literal["SCHEDULED", "CHECKED_IN", "COMPLETED", "CANCELLED", "NO_SHOW"]


class DoctorBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    specialty: str = Field(min_length=1, max_length=80)
    room: str = Field(default="", max_length=20)
    active: bool = True


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    specialty: str | None = Field(default=None, min_length=1, max_length=80)
    room: str | None = Field(default=None, max_length=20)
    active: bool | None = None


class DoctorOut(DoctorBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PatientBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=5, max_length=20, pattern=r"^[0-9+\-\s()]+$")
    email: str = Field(default="", max_length=120)
    date_of_birth: str = Field(default="", pattern=r"^(\d{4}-\d{2}-\d{2})?$")


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: str | None = Field(default=None, min_length=5, max_length=20, pattern=r"^[0-9+\-\s()]+$")
    email: str | None = Field(default=None, max_length=120)
    date_of_birth: str | None = Field(default=None, pattern=r"^(\d{4}-\d{2}-\d{2})?$")


class PatientOut(PatientBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    scheduled_at: datetime
    reason: str = Field(default="", max_length=500)
    status: AppointmentStatus = "SCHEDULED"


class AppointmentUpdate(BaseModel):
    doctor_id: int | None = None
    patient_id: int | None = None
    scheduled_at: datetime | None = None
    reason: str | None = Field(default=None, max_length=500)
    status: AppointmentStatus | None = None


class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    scheduled_at: datetime
    reason: str
    status: AppointmentStatus
    created_at: datetime
    doctor_name: str
    doctor_specialty: str
    patient_name: str


class StatsOut(BaseModel):
    doctors: int
    patients: int
    appointments_today: int
    upcoming: int
    by_status: dict[str, int]
    completion_rate: float
