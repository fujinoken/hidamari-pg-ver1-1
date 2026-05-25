from sqlalchemy import (
    MetaData, Table, Column, String, Text, Float, Date, DateTime, Boolean, Integer
)
from datetime import datetime

metadata = MetaData()

staff_accounts = Table(
    "staff_accounts", metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("login_id", String, nullable=False, unique=True),
    Column("password", String, nullable=False),
    Column("display_name", String, nullable=False),
    Column("role", String, nullable=False, default="staff"),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

users = Table(
    "users", metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("user_code", String, nullable=False, unique=True),
    Column("user_name", String, nullable=False),
    Column("room", String),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

health_records = Table(
    "health_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("user_id", String, nullable=False),
    Column("record_date", Date, nullable=False),
    Column("temperature", Float),
    Column("blood_pressure_high", Float),
    Column("blood_pressure_low", Float),
    Column("pulse", Float),
    Column("spo2", Float),
    Column("weight", Float),
    Column("meal_rate", Float),
    Column("memo", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

excretion_records = Table(
    "excretion_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("user_id", String, nullable=False),
    Column("record_date", Date, nullable=False),
    Column("urination", String),
    Column("defecation", String),
    Column("memo", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
)

handover_records = Table(
    "handover_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("record_date", Date, nullable=False),
    Column("shift", String),
    Column("content", Text),
    Column("created_by", String),
    Column("created_at", DateTime, default=datetime.utcnow),
)
