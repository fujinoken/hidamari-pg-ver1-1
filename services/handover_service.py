
from __future__ import annotations
import uuid
import pandas as pd
from sqlalchemy import select, insert, update, delete, or_
from db.connection import get_engine
from db.schema import handover_logs
from config.settings import DEFAULT_FACILITY_ID
from utils.time_utils import now_jst_dt
from services.audit_service import add_audit_log

def create_handover(data: dict, actor: dict):
    rid = str(uuid.uuid4())
    row = dict(data)
    row.update({
        "id": rid,
        "facility_id": DEFAULT_FACILITY_ID,
        "created_by": actor.get("login_id", ""),
        "updated_by": actor.get("login_id", ""),
    })
    with get_engine().begin() as conn:
        conn.execute(insert(handover_logs).values(**row))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "申し送り登録", "handover_logs", rid, after=row)
    return rid

def search_handovers(start_date=None, end_date=None, keyword="") -> pd.DataFrame:
    with get_engine().begin() as conn:
        stmt = select(handover_logs).where(handover_logs.c.facility_id == DEFAULT_FACILITY_ID)
        if start_date:
            stmt = stmt.where(handover_logs.c.record_date >= start_date)
        if end_date:
            stmt = stmt.where(handover_logs.c.record_date <= end_date)
        if keyword:
            like=f"%{keyword}%"
            stmt=stmt.where(or_(handover_logs.c.fact.ilike(like), handover_logs.c.notice.ilike(like), handover_logs.c.next_watch.ilike(like), handover_logs.c.writer.ilike(like)))
        stmt=stmt.order_by(handover_logs.c.record_date.desc(), handover_logs.c.created_at.desc()).limit(500)
        rows=conn.execute(stmt).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def get_handover(record_id: str) -> dict | None:
    with get_engine().begin() as conn:
        row=conn.execute(select(handover_logs).where(handover_logs.c.id == record_id)).mappings().first()
    return dict(row) if row else None

def update_handover(record_id: str, data: dict, actor: dict, expected_updated_at: str | None):
    before=get_handover(record_id)
    if not before:
        raise ValueError("対象記録が見つかりません。")
    if expected_updated_at and expected_updated_at != str(before.get("updated_at")):
        raise RuntimeError("他の端末で更新されています。画面を再読み込みしてから再度確認してください。")
    row=dict(data)
    row["updated_by"]=actor.get("login_id","")
    row["updated_at"]=now_jst_dt()
    with get_engine().begin() as conn:
        conn.execute(update(handover_logs).where(handover_logs.c.id == record_id).values(**row))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "申し送り更新", "handover_logs", record_id, before=before, after=row)

def delete_handover(record_id: str, actor: dict, expected_updated_at: str | None):
    before=get_handover(record_id)
    if not before:
        raise ValueError("対象記録が見つかりません。")
    if expected_updated_at and expected_updated_at != str(before.get("updated_at")):
        raise RuntimeError("他の端末で更新されています。画面を再読み込みしてから再度確認してください。")
    with get_engine().begin() as conn:
        conn.execute(delete(handover_logs).where(handover_logs.c.id == record_id))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "申し送り削除", "handover_logs", record_id, before=before)
