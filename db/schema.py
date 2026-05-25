from sqlalchemy import MetaData, Table, Column, String, Integer, Float, Text, DateTime
from sqlalchemy.sql import func

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", String(64), primary_key=True),
    Column("facility_id", String(64), nullable=False, default="default"),
    Column("login_id", String(64), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column("name", String(100), nullable=False),
    Column("role", String(32), nullable=False, default="staff"),
    Column("created_at", DateTime, server_default=func.now()),
)

health_records = Table(
    "health_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", String(64), nullable=False, default="default"),
    Column("user_id", String(64), nullable=False),
    Column("user_name", String(100), nullable=False),
    Column("record_date", String(20), nullable=False),
    Column("temperature", Float),
    Column("blood_pressure_high", Float),
    Column("blood_pressure_low", Float),
    Column("pulse", Float),
    Column("spo2", Float),
    Column("weight", Float),
    Column("meal_rate", Float),
    Column("memo", Text),
    Column("created_by", String(100)),
    Column("created_at", DateTime, server_default=func.now()),
)

excretion_records = Table(
    "excretion_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", String(64), nullable=False, default="default"),
    Column("user_id", String(64), nullable=False),
    Column("user_name", String(100), nullable=False),
    Column("record_date", String(20), nullable=False),
    Column("urination", Integer, default=0),
    Column("defecation", Integer, default=0),
    Column("memo", Text),
    Column("created_by", String(100)),
    Column("created_at", DateTime, server_default=func.now()),
)

handover_records = Table(
    "handover_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", String(64), nullable=False, default="default"),
    Column("record_date", String(20), nullable=False),
    Column("shift", String(20), nullable=False),
    Column("content", Text, nullable=False),
    Column("created_by", String(100)),
    Column("created_at", DateTime, server_default=func.now()),
)
