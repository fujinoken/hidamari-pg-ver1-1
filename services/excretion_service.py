
from __future__ import annotations
import uuid
import pandas as pd
from sqlalchemy import select, insert, update, delete, or_
from db.connection import get_engine
from db.schema import excretion_records, users
from config.settings import DEFAULT_FACILITY_ID
from utils.time_utils import now_jst_dt
from services.audit_service import add_audit_log

def create_excretion_record(data: dict, actor: dict):
    rid = str(uuid.uuid4())
    row = dict(data)
    row.update({
        "id": rid,
        "facility_id": DEFAULT_FACILITY_ID,
        "created_by": actor.get("login_id", ""),
        "updated_by": actor.get("login_id", ""),
    })
    with get_engine().begin() as conn:
        conn.execute(insert(excretion_records).values(**row))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "排泄記録登録", "excretion_records", rid, after=row)
    return rid

def search_excretion_records(start_date=None, end_date=None, user_id=None, keyword="") -> pd.DataFrame:
    with get_engine().begin() as conn:
        stmt = select(excretion_records, users.c.user_name.label("user_name")).join(users, users.c.id == excretion_records.c.user_id).where(excretion_records.c.facility_id == DEFAULT_FACILITY_ID)
        if start_date:
            stmt = stmt.where(excretion_records.c.record_date >= start_date)
        if end_date:
            stmt = stmt.where(excretion_records.c.record_date <= end_date)
        if user_id:
            stmt = stmt.where(excretion_records.c.user_id == user_id)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(excretion_records.c.memo.ilike(like), users.c.user_name.ilike(like)))
        stmt = stmt.order_by(excretion_records.c.record_date.desc(), excretion_records.c.created_at.desc()).limit(500)
        rows = conn.execute(stmt).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def get_excretion_record(record_id: str) -> dict | None:
    with get_engine().begin() as conn:
        row = conn.execute(select(excretion_records).where(excretion_records.c.id == record_id)).mappings().first()
    return dict(row) if row else None

def update_excretion_record(record_id: str, data: dict, actor: dict, expected_updated_at: str | None):
    before = get_excretion_record(record_id)
    if not before:
        raise ValueError("対象記録が見つかりません。")
    if expected_updated_at and expected_updated_at != str(before.get("updated_at")):
        raise RuntimeError("他の端末で更新されています。画面を再読み込みしてから再度確認してください。")
    row = dict(data)
    row["updated_by"] = actor.get("login_id", "")
    row["updated_at"] = now_jst_dt()
    with get_engine().begin() as conn:
        conn.execute(update(excretion_records).where(excretion_records.c.id == record_id).values(**row))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "排泄記録更新", "excretion_records", record_id, before=before, after=row)

def delete_excretion_record(record_id: str, actor: dict, expected_updated_at: str | None):
    before = get_excretion_record(record_id)
    if not before:
        raise ValueError("対象記録が見つかりません。")
    if expected_updated_at and expected_updated_at != str(before.get("updated_at")):
        raise RuntimeError("他の端末で更新されています。画面を再読み込みしてから再度確認してください。")
    with get_engine().begin() as conn:
        conn.execute(delete(excretion_records).where(excretion_records.c.id == record_id))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "排泄記録削除", "excretion_records", record_id, before=before)
