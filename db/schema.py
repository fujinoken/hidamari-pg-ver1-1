from __future__ import annotations

from sqlalchemy import (
    MetaData, Table, Column, String, Text, Integer, Float, Date, DateTime, Boolean,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.sql import func

metadata = MetaData()

# 方針固定:
# facility_id = TEXT(String)
# users.id = TEXT(String)
# login_id = TEXT(String)
# user_name は互換用の任意列

facilities = Table(
    "facilities", metadata,
    Column("id", String, primary_key=True),
    Column("name", Text, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

users = Table(
    "users", metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("login_id", String, nullable=False, unique=True),
    Column("password", Text, nullable=False),
    Column("display_name", Text, nullable=False),
    Column("user_name", Text, nullable=True),  # 互換用。新規機能では基本使わない
    Column("role", Text, nullable=False, default="staff"),  # admin/staff
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, server_default=func.now()),
)

residents = Table(
    "residents", metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("name", Text, nullable=False),
    Column("room", Text, nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, server_default=func.now()),
)

health_records = Table(
    "health_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("resident_id", String, nullable=False),
    Column("record_date", Date, nullable=False),
    Column("temperature", Float, nullable=True),
    Column("blood_pressure_high", Integer, nullable=True),
    Column("blood_pressure_low", Integer, nullable=True),
    Column("pulse", Integer, nullable=True),
    Column("spo2", Integer, nullable=True),
    Column("weight", Float, nullable=True),
    Column("meal_rate", Float, nullable=True),
    Column("water_ml", Integer, nullable=True),
    Column("memo", Text, nullable=True),
    Column("staff_id", String, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    UniqueConstraint("facility_id", "resident_id", "record_date", name="uq_health_daily"),
)

excretion_records = Table(
    "excretion_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("resident_id", String, nullable=False),
    Column("record_date", Date, nullable=False),
    Column("urination_count", Integer, nullable=True),
    Column("defecation_count", Integer, nullable=True),
    Column("stool_condition", Text, nullable=True),
    Column("memo", Text, nullable=True),
    Column("staff_id", String, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    UniqueConstraint("facility_id", "resident_id", "record_date", name="uq_excretion_daily"),
)
