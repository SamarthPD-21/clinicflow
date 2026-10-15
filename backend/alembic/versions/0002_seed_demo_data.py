"""seed demo doctors and patients so a fresh install is not empty

Revision ID: 0002_seed_demo_data
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_seed_demo_data"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

DOCTORS = [
    ("Dr. Ananya Rao", "General Medicine", "101"),
    ("Dr. Vikram Mehta", "Cardiology", "204"),
    ("Dr. Priya Nair", "Pediatrics", "110"),
    ("Dr. Arjun Iyer", "Dermatology", "305"),
]
PATIENTS = [
    ("Rohan Sharma", "+91 98450 11223", "rohan@example.com", "1990-04-12"),
    ("Meera Kapoor", "+91 99001 44556", "meera@example.com", "1985-11-03"),
    ("Kabir Singh", "+91 97311 77889", "", "2016-07-21"),
]


def upgrade():
    doctors = sa.table("doctors", sa.column("name"), sa.column("specialty"), sa.column("room"))
    patients = sa.table(
        "patients", sa.column("full_name"), sa.column("phone"), sa.column("email"), sa.column("date_of_birth")
    )
    op.bulk_insert(doctors, [{"name": n, "specialty": s, "room": r} for n, s, r in DOCTORS])
    op.bulk_insert(
        patients, [{"full_name": n, "phone": p, "email": e, "date_of_birth": d} for n, p, e, d in PATIENTS]
    )


def downgrade():
    op.execute(sa.text("DELETE FROM doctors WHERE name IN :names").bindparams(
        sa.bindparam("names", [d[0] for d in DOCTORS], expanding=True)))
    op.execute(sa.text("DELETE FROM patients WHERE full_name IN :names").bindparams(
        sa.bindparam("names", [p[0] for p in PATIENTS], expanding=True)))
