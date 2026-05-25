from __future__ import annotations
from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, Date, DateTime, Float, Boolean, UniqueConstraint

metadata = MetaData()

staff_accounts = Table(
    "staff_accounts", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("login_id", String(100), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column("staff_name", String(100), nullable=False),
    Column("role", String(50), nullable=False, default="staff"),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_code", String(50), nullable=False, unique=True),
    Column("user_name", String(100), nullable=False),
    Column("room", String(50), nullable=True),
    Column("birth_date", Date, nullable=True),
    Column("gender", String(20), nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("memo", Text, nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
    Column("updated_at", DateTime, nullable=False, default=datetime.utcnow),
)

health_records = Table(
    "health_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("record_date", Date, nullable=False),
    Column("user_id", Integer, nullable=False),
    Column("temperature", Float, nullable=True),
    Column("blood_pressure_high", Integer, nullable=True),
    Column("blood_pressure_low", Integer, nullable=True),
    Column("pulse", Integer, nullable=True),
    Column("spo2", Integer, nullable=True),
    Column("weight", Float, nullable=True),
    Column("meal_rate", Integer, nullable=True),
    Column("water_amount", Integer, nullable=True),
    Column("family_memo", Text, nullable=True),
    Column("staff_memo", Text, nullable=True),
    Column("staff_name", String(100), nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
    Column("updated_at", DateTime, nullable=False, default=datetime.utcnow),
    UniqueConstraint("record_date", "user_id", name="uq_health_record_date_user"),
)

excretion_records = Table(
    "excretion_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("record_date", Date, nullable=False),
    Column("user_id", Integer, nullable=False),
    Column("stool_count", Integer, nullable=True),
    Column("urine_count", Integer, nullable=True),
    Column("memo", Text, nullable=True),
    Column("staff_name", String(100), nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

handovers = Table(
    "handovers", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("record_date", Date, nullable=False),
    Column("shift", String(20), nullable=False),
    Column("title", String(200), nullable=True),
    Column("body", Text, nullable=True),
    Column("staff_name", String(100), nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)
