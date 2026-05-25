
from __future__ import annotations
import uuid
import pandas as pd
from sqlalchemy import select, insert, update, delete, and_, or_
from db.connection import get_engine
from db.schema import health_records, users
from config.settings import DEFAULT_FACILITY_ID
from utils.time_utils import now_jst_dt
from services.audit_service import add_audit_log

def create_health_record(data: dict, actor: dict):
    rid = str(uuid.uuid4())
    row = dict(data)
    row.update({
        "id": rid,
        "facility_id": DEFAULT_FACILITY_ID,
        "created_by": actor.get("login_id", ""),
        "updated_by": actor.get("login_id", ""),
    })
    with get_engine().begin() as conn:
        conn.execute(insert(health_records).values(**row))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "健康記録登録", "health_records", rid, after=row)
    return rid

def search_health_records(start_date=None, end_date=None, user_id=None, keyword="") -> pd.DataFrame:
    with get_engine().begin() as conn:
        stmt = select(
            health_records,
            users.c.user_name.label("user_name"),
        ).join(users, users.c.id == health_records.c.user_id).where(
            health_records.c.facility_id == DEFAULT_FACILITY_ID
        )
        if start_date:
            stmt = stmt.where(health_records.c.record_date >= start_date)
        if end_date:
            stmt = stmt.where(health_records.c.record_date <= end_date)
        if user_id:
            stmt = stmt.where(health_records.c.user_id == user_id)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(health_records.c.family_note.ilike(like), health_records.c.change_note.ilike(like), users.c.user_name.ilike(like)))
        stmt = stmt.order_by(health_records.c.record_date.desc(), health_records.c.created_at.desc()).limit(500)
        rows = conn.execute(stmt).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def get_health_record(record_id: str) -> dict | None:
    with get_engine().begin() as conn:
        row = conn.execute(select(health_records).where(health_records.c.id == record_id)).mappings().first()
    return dict(row) if row else None

def update_health_record(record_id: str, data: dict, actor: dict, expected_updated_at: str | None):
    before = get_health_record(record_id)
    if not before:
        raise ValueError("対象記録が見つかりません。")
    current_token = str(before.get("updated_at"))
    if expected_updated_at and expected_updated_at != current_token:
        raise RuntimeError("他の端末で更新されています。画面を再読み込みしてから再度確認してください。")
    row = dict(data)
    row["updated_by"] = actor.get("login_id", "")
    row["updated_at"] = now_jst_dt()
    with get_engine().begin() as conn:
        conn.execute(update(health_records).where(health_records.c.id == record_id).values(**row))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "健康記録更新", "health_records", record_id, before=before, after=row)

def delete_health_record(record_id: str, actor: dict, expected_updated_at: str | None):
    before = get_health_record(record_id)
    if not before:
        raise ValueError("対象記録が見つかりません。")
    current_token = str(before.get("updated_at"))
    if expected_updated_at and expected_updated_at != current_token:
        raise RuntimeError("他の端末で更新されています。画面を再読み込みしてから再度確認してください。")
    with get_engine().begin() as conn:
        conn.execute(delete(health_records).where(health_records.c.id == record_id))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "健康記録削除", "health_records", record_id, before=before)

def latest_weight_days() -> pd.DataFrame:
    with get_engine().begin() as conn:
        df_users = pd.DataFrame([dict(r) for r in conn.execute(select(users).where(users.c.facility_id == DEFAULT_FACILITY_ID, users.c.display_flag == True)).mappings().all()])
        df_health = pd.DataFrame([dict(r) for r in conn.execute(select(health_records).where(health_records.c.facility_id == DEFAULT_FACILITY_ID, health_records.c.weight != None)).mappings().all()])
    if df_users.empty:
        return pd.DataFrame(columns=["利用者名","最新体重","最終測定日","経過日数"])
    rows=[]
    today = pd.Timestamp.today().normalize().date()
    for _,u in df_users.iterrows():
        h = df_health[df_health["user_id"]==u["id"]] if not df_health.empty else pd.DataFrame()
        if h.empty:
            rows.append({"利用者名":u["user_name"],"最新体重":"未測定","最終測定日":"","経過日数":"未測定"})
        else:
            h=h.sort_values("record_date", ascending=False)
            r=h.iloc[0]
            d=pd.to_datetime(r["record_date"]).date()
            rows.append({"利用者名":u["user_name"],"最新体重":r["weight"],"最終測定日":str(d),"経過日数":(today-d).days})
    return pd.DataFrame(rows)
