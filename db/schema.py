from sqlalchemy import (
    MetaData, Table, Column, String, Text, Date, DateTime, Float, Boolean, Integer
)
from sqlalchemy.sql import func

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("user_code", String, nullable=False, default=""),
    Column("user_name", String, nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, server_default=func.now()),
)

staff_accounts = Table(
    "staff_accounts",
    metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("login_id", String, nullable=False, unique=True),
    Column("password", String, nullable=False),
    Column("role", String, nullable=False, default="admin"),
    Column("display_name", String, nullable=False, default="管理者"),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, server_default=func.now()),
)

health_records = Table(
    "health_records",
    metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("record_date", Date, nullable=False),
    Column("user_id", String, nullable=False),
    Column("temperature", Float),
    Column("bp_high", Float),
    Column("bp_low", Float),
    Column("pulse", Float),
    Column("spo2", Float),
    Column("weight", Float),
    Column("meal_rate", Float),
    Column("memo", Text),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

excretion_records = Table(
    "excretion_records",
    metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("record_date", Date, nullable=False),
    Column("user_id", String, nullable=False),
    Column("urination", String),
    Column("defecation", String),
    Column("memo", Text),
    Column("created_at", DateTime, server_default=func.now()),
)

handovers = Table(
    "handovers",
    metadata,
    Column("id", String, primary_key=True),
    Column("facility_id", String, nullable=False, default="default"),
    Column("record_date", Date, nullable=False),
    Column("shift", String, nullable=False),
    Column("content", Text),
    Column("staff_name", String),
    Column("created_at", DateTime, server_default=func.now()),
)
