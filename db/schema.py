from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from utils.time_utils import now_jst_dt

Base = declarative_base()


class Facility(Base):
    __tablename__ = "facilities"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, default="ひだまり")
    memo = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=now_jst_dt)
    updated_at = Column(DateTime(timezone=True), default=now_jst_dt, onupdate=now_jst_dt)


class StaffAccount(Base):
    __tablename__ = "staff_accounts"
    id = Column(Integer, primary_key=True)
    login_id = Column(String(80), unique=True, nullable=False, index=True)
    display_name = Column(String(120), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="staff")
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_jst_dt)
    updated_at = Column(DateTime(timezone=True), default=now_jst_dt, onupdate=now_jst_dt)
    last_login_at = Column(DateTime(timezone=True), nullable=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_code = Column(String(40), unique=True, nullable=False, index=True)
    display_name = Column(String(120), nullable=False, index=True)
    is_visible = Column(Boolean, default=True)
    basic_info = Column(Text, default="")
    living_status = Column(Text, default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=now_jst_dt)
    updated_at = Column(DateTime(timezone=True), default=now_jst_dt, onupdate=now_jst_dt)

    health_records = relationship("HealthRecord", back_populates="user")
    excretion_records = relationship("ExcretionRecord", back_populates="user")


class HealthRecord(Base):
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True)
    record_date = Column(Date, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    temperature = Column(Float, nullable=True)
    bp_high = Column(Integer, nullable=True)
    bp_low = Column(Integer, nullable=True)
    pulse = Column(Integer, nullable=True)
    spo2 = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    breakfast_rate = Column(Integer, nullable=True)
    lunch_rate = Column(Integer, nullable=True)
    dinner_rate = Column(Integer, nullable=True)
    water_ml = Column(Integer, nullable=True)
    family_note = Column(Text, default="")
    change_note = Column(Text, default="")
    input_by = Column(String(120), default="")
    created_at = Column(DateTime(timezone=True), default=now_jst_dt)
    updated_at = Column(DateTime(timezone=True), default=now_jst_dt, onupdate=now_jst_dt)

    user = relationship("User", back_populates="health_records")
    __table_args__ = (UniqueConstraint("record_date", "user_id", name="uq_health_record_date_user"),)


class ExcretionRecord(Base):
    __tablename__ = "excretion_records"
    id = Column(Integer, primary_key=True)
    record_date = Column(Date, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    slot = Column(String(30), nullable=False)
    slot_hint = Column(String(60), default="")
    urine_amount = Column(String(30), default="なし")
    urine_type = Column(String(30), default="なし")
    stool_amount = Column(String(30), default="なし")
    stool_type = Column(String(30), default="なし")
    memo = Column(Text, default="")
    input_by = Column(String(120), default="")
    created_at = Column(DateTime(timezone=True), default=now_jst_dt)
    updated_at = Column(DateTime(timezone=True), default=now_jst_dt, onupdate=now_jst_dt)

    user = relationship("User", back_populates="excretion_records")
    __table_args__ = (UniqueConstraint("record_date", "user_id", "slot", name="uq_excretion_date_user_slot"),)


class HandoverLog(Base):
    __tablename__ = "handover_logs"
    id = Column(Integer, primary_key=True)
    record_date = Column(Date, nullable=False, index=True)
    shift = Column(String(30), nullable=False)
    writer = Column(String(120), default="")
    fact_text = Column(Text, default="")
    notice_text = Column(Text, default="")
    next_watch_text = Column(Text, default="")
    priority = Column(String(30), default="通常")
    status = Column(String(30), default="観察継続")
    created_at = Column(DateTime(timezone=True), default=now_jst_dt)
    updated_at = Column(DateTime(timezone=True), default=now_jst_dt, onupdate=now_jst_dt)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=now_jst_dt, index=True)
    login_id = Column(String(80), default="")
    role = Column(String(30), default="")
    action = Column(String(120), nullable=False)
    target_table = Column(String(120), default="")
    target_id = Column(String(120), default="")
    summary = Column(Text, default="")
    before_text = Column(Text, default="")
    after_text = Column(Text, default="")
