from __future__ import annotations

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Text,
    Integer,
    Numeric,
    Date,
    Boolean,
    DateTime,
    func,
)

metadata = MetaData()

# 施設
# id は TEXT で固定
facilities = Table(
    "facilities",
    metadata,
    Column("id", Text, primary_key=True),
    Column("name", Text, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

# 職員・ログインユーザー
# id は TEXT で固定
# user_name は過去互換用。新規機能では login_id を使用。
users = Table(
    "users",
    metadata,
    Column("id", Text, primary_key=True),
    Column("facility_id", Text, nullable=False, default="facility_default"),
    Column("login_id", Text, nullable=False, unique=True),
    Column("user_name", Text, nullable=True),
    Column("display_name", Text, nullable=False),
    Column("role", Text, nullable=False, default="staff"),
    Column("password_hash", Text, nullable=False),
    Column("must_change_password", Boolean, nullable=False, default=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

# 利用者マスタ
residents = Table(
    "residents",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", Text, nullable=False, default="facility_default"),
    Column("name", Text, nullable=False),
    Column("is_visible", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

# 健康記録
health_records = Table(
    "health_records",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", Text, nullable=False, default="facility_default"),
    Column("resident_id", Integer),
    Column("resident_name", Text),
    Column("record_date", Date),
    Column("temperature", Numeric),
    Column("bp_high", Integer),
    Column("bp_low", Integer),
    Column("pulse", Integer),
    Column("spo2", Integer),
    Column("weight", Numeric),
    Column("water_ml", Integer),
    Column("breakfast", Integer),
    Column("lunch", Integer),
    Column("dinner", Integer),
    Column("family_note", Text),
    Column("change_note", Text),
    Column("input_by", Text),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

# 排泄記録
excretion_records = Table(
    "excretion_records",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", Text, nullable=False, default="facility_default"),
    Column("resident_id", Integer),
    Column("resident_name", Text),
    Column("record_date", Date),
    Column("time_slot", Text),
    Column("urine_amount", Text),
    Column("urine_status", Text),
    Column("stool_amount", Text),
    Column("stool_status", Text),
    Column("memo", Text),
    Column("input_by", Text),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

# 業務申し送り
handover_records = Table(
    "handover_records",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", Text, nullable=False, default="facility_default"),
    Column("record_date", Date),
    Column("shift", Text),
    Column("writer", Text),
    Column("fact", Text),
    Column("notice", Text),
    Column("next_watch", Text),
    Column("priority", Text),
    Column("status", Text),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

# 監査ログ
audit_logs = Table(
    "audit_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", Text, nullable=False, default="facility_default"),
    Column("login_id", Text),
    Column("role", Text),
    Column("action", Text),
    Column("table_name", Text),
    Column("target_id", Text),
    Column("summary", Text),
    Column("created_at", DateTime, server_default=func.now()),
)

# バックアップログ
backup_logs = Table(
    "backup_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("facility_id", Text, nullable=False, default="facility_default"),
    Column("backup_type", Text),
    Column("file_name", Text),
    Column("memo", Text),
    Column("created_by", Text),
    Column("created_at", DateTime, server_default=func.now()),
)
