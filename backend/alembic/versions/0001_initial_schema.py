"""initial schema: doctors, patients, appointments

Revision ID: 0001_initial_schema
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("specialty", sa.String(80), nullable=False),
        sa.Column("room", sa.String(20), nullable=False, server_default=""),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(120), nullable=False, server_default=""),
        sa.Column("date_of_birth", sa.String(10), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="SCHEDULED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_scheduled_at", "appointments", ["scheduled_at"])


def downgrade():
    op.drop_table("appointments")
    op.drop_table("patients")
    op.drop_table("doctors")
