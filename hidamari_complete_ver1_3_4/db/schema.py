# DB定義完全統一版
# facility_id = TEXT / users.id = TEXT / login_id = TEXT
# 旧コード互換のため SQLAlchemy Table 名(users/health_records/excretion_records)も定義します。
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, Float, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Text, primary_key=True),
    Column("facility_id", Text, nullable=False),
    Column("login_id", Text, nullable=False, unique=True),
    Column("password", Text, nullable=False),
    Column("display_name", Text, nullable=False),
    Column("user_name", Text, nullable=True),  # 旧コード互換用。新規処理では使用しない。
    Column("role", Text, nullable=False, default="staff"),
    Column("is_active", Integer, nullable=False, default=1),
    Column("created_at", DateTime, server_default=func.current_timestamp()),
)

health_records = Table(
    "health_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", Text, nullable=False),
    Column("user_id", Text, ForeignKey("users.id"), nullable=False),
    Column("record_date", Text, nullable=False),
    Column("temperature", Float),
    Column("blood_pressure_high", Integer),
    Column("blood_pressure_low", Integer),
    Column("pulse", Integer),
    Column("spo2", Float),
    Column("weight", Float),
    Column("meal_rate", Float),
    Column("memo", Text),
    Column("created_by", Text),
    Column("created_at", DateTime, server_default=func.current_timestamp()),
    Column("updated_at", DateTime),
    UniqueConstraint("facility_id", "user_id", "record_date", name="uq_health_facility_user_date"),
)

excretion_records = Table(
    "excretion_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", Text, nullable=False),
    Column("user_id", Text, ForeignKey("users.id"), nullable=False),
    Column("record_date", Text, nullable=False),
    Column("urine_count", Integer, default=0),
    Column("stool_count", Integer, default=0),
    Column("stool_status", Text),
    Column("memo", Text),
    Column("created_by", Text),
    Column("created_at", DateTime, server_default=func.current_timestamp()),
    Column("updated_at", DateTime),
    UniqueConstraint("facility_id", "user_id", "record_date", name="uq_excretion_facility_user_date"),
)
