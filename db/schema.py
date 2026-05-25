from sqlalchemy import MetaData, Table, Column, String, Integer, Float, Date, DateTime, Text, Boolean
from datetime import datetime

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", String, primary_key=True),
    Column("login_id", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("name", String, nullable=False),
    Column("role", String, nullable=False, default="staff"),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, default=datetime.now),
)

residents = Table(
    "residents", metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("room", String, default=""),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, default=datetime.now),
)

health_records = Table(
    "health_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("record_date", Date, nullable=False),
    Column("resident_id", String, nullable=False),
    Column("resident_name", String, nullable=False),
    Column("temperature", Float),
    Column("blood_pressure_high", Integer),
    Column("blood_pressure_low", Integer),
    Column("pulse", Integer),
    Column("spo2", Float),
    Column("weight", Float),
    Column("meal_rate", Float),
    Column("memo", Text, default=""),
    Column("staff_name", String, default=""),
    Column("created_at", DateTime, default=datetime.now),
)

excretion_records = Table(
    "excretion_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("record_date", Date, nullable=False),
    Column("resident_id", String, nullable=False),
    Column("resident_name", String, nullable=False),
    Column("urination", String, default=""),
    Column("bowel_movement", String, default=""),
    Column("memo", Text, default=""),
    Column("staff_name", String, default=""),
    Column("created_at", DateTime, default=datetime.now),
)

handover_records = Table(
    "handover_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("record_date", Date, nullable=False),
    Column("shift", String, default="日勤"),
    Column("content", Text, default=""),
    Column("staff_name", String, default=""),
    Column("created_at", DateTime, default=datetime.now),
)
