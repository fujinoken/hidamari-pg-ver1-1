
from __future__ import annotations
from sqlalchemy import MetaData, Table, Column, String, Text, Date, DateTime, Float, Integer, Boolean, Index, UniqueConstraint
from sqlalchemy.sql import func

metadata = MetaData()

facilities = Table(
    "facilities", metadata,
    Column("id", String(64), primary_key=True),
    Column("name", String(120), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

staff_accounts = Table(
    "staff_accounts", metadata,
    Column("id", String(64), primary_key=True),
    Column("facility_id", String(64), nullable=False, index=True),
    Column("login_id", String(80), nullable=False),
    Column("display_name", String(120), nullable=False),
    Column("password_hash", Text, nullable=False),
    Column("role", String(32), nullable=False, default="staff"),
    Column("active", Boolean, nullable=False, default=True),
    Column("must_change_password", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("facility_id", "login_id", name="uq_staff_facility_login"),
)

users = Table(
    "users", metadata,
    Column("id", String(64), primary_key=True),
    Column("facility_id", String(64), nullable=False, index=True),
    Column("user_name", String(120), nullable=False),
    Column("display_flag", Boolean, nullable=False, default=True),
    Column("memo", Text, default=""),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("facility_id", "user_name", name="uq_users_facility_name"),
)

health_records = Table(
    "health_records", metadata,
    Column("id", String(64), primary_key=True),
    Column("facility_id", String(64), nullable=False, index=True),
    Column("record_date", Date, nullable=False, index=True),
    Column("user_id", String(64), nullable=False, index=True),
    Column("temperature", Float),
    Column("bp_high", Integer),
    Column("bp_low", Integer),
    Column("pulse", Integer),
    Column("spo2", Integer),
    Column("weight", Float),
    Column("water_ml", Integer),
    Column("breakfast", Integer),
    Column("lunch", Integer),
    Column("dinner", Integer),
    Column("family_note", Text, default=""),
    Column("change_note", Text, default=""),
    Column("created_by", String(64), default=""),
    Column("updated_by", String(64), default=""),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("facility_id", "record_date", "user_id", name="uq_health_facility_date_user"),
)
Index("ix_health_search", health_records.c.facility_id, health_records.c.record_date, health_records.c.user_id)

excretion_records = Table(
    "excretion_records", metadata,
    Column("id", String(64), primary_key=True),
    Column("facility_id", String(64), nullable=False, index=True),
    Column("record_date", Date, nullable=False, index=True),
    Column("user_id", String(64), nullable=False, index=True),
    Column("time_slot", String(32), nullable=False),
    Column("urine_amount", String(32), default="なし"),
    Column("urine_type", String(32), default="なし"),
    Column("stool_amount", String(32), default="なし"),
    Column("stool_type", String(32), default="なし"),
    Column("memo", Text, default=""),
    Column("created_by", String(64), default=""),
    Column("updated_by", String(64), default=""),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint("facility_id", "record_date", "user_id", "time_slot", name="uq_excretion_facility_date_user_slot"),
)
Index("ix_excretion_search", excretion_records.c.facility_id, excretion_records.c.record_date, excretion_records.c.user_id)

handover_logs = Table(
    "handover_logs", metadata,
    Column("id", String(64), primary_key=True),
    Column("facility_id", String(64), nullable=False, index=True),
    Column("record_date", Date, nullable=False, index=True),
    Column("shift", String(32), nullable=False),
    Column("writer", String(120), default=""),
    Column("fact", Text, default=""),
    Column("notice", Text, default=""),
    Column("next_watch", Text, default=""),
    Column("priority", String(32), default="通常"),
    Column("status", String(32), default="観察継続"),
    Column("created_by", String(64), default=""),
    Column("updated_by", String(64), default=""),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now()),
)
Index("ix_handover_search", handover_logs.c.facility_id, handover_logs.c.record_date, handover_logs.c.shift)

audit_logs = Table(
    "audit_logs", metadata,
    Column("id", String(64), primary_key=True),
    Column("facility_id", String(64), nullable=False, index=True),
    Column("login_id", String(80), default=""),
    Column("role", String(32), default=""),
    Column("action", String(120), nullable=False),
    Column("target_table", String(120), default=""),
    Column("target_id", String(64), default=""),
    Column("summary", Text, default=""),
    Column("before_json", Text, default=""),
    Column("after_json", Text, default=""),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
Index("ix_audit_search", audit_logs.c.facility_id, audit_logs.c.created_at, audit_logs.c.action)

backup_logs = Table(
    "backup_logs", metadata,
    Column("id", String(64), primary_key=True),
    Column("facility_id", String(64), nullable=False, index=True),
    Column("backup_type", String(64), nullable=False),
    Column("summary", Text, default=""),
    Column("created_by", String(64), default=""),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
