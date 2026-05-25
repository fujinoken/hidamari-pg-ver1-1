from __future__ import annotations
from datetime import datetime, date
import pandas as pd
from sqlalchemy import select, insert, update, delete, and_, or_
from sqlalchemy.exc import IntegrityError
from db.migrations import get_engine
from db.schema import users, health_records, excretion_records, handovers

def _to_date(value):
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    return pd.to_datetime(value).date()

# 利用者
def list_users(active_only: bool = True, keyword: str = "") -> pd.DataFrame:
    stmt = select(users).order_by(users.c.user_code)
    conds = []
    if active_only:
        conds.append(users.c.is_active == True)
    if keyword:
        kw = f"%{keyword}%"
        conds.append(or_(users.c.user_name.like(kw), users.c.user_code.like(kw), users.c.room.like(kw)))
    if conds:
        stmt = stmt.where(and_(*conds))
    with get_engine().begin() as conn:
        rows = conn.execute(stmt).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def add_user(user_code: str, user_name: str, room: str = "", birth_date=None, gender: str = "", memo: str = ""):
    with get_engine().begin() as conn:
        conn.execute(insert(users).values(
            user_code=str(user_code).strip(), user_name=str(user_name).strip(), room=str(room).strip() or None,
            birth_date=_to_date(birth_date), gender=str(gender).strip() or None, memo=str(memo).strip() or None,
            is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        ))

def update_user(user_id: int, user_code: str, user_name: str, room: str = "", birth_date=None, gender: str = "", memo: str = "", is_active: bool = True):
    with get_engine().begin() as conn:
        conn.execute(update(users).where(users.c.id == int(user_id)).values(
            user_code=str(user_code).strip(), user_name=str(user_name).strip(), room=str(room).strip() or None,
            birth_date=_to_date(birth_date), gender=str(gender).strip() or None, memo=str(memo).strip() or None,
            is_active=bool(is_active), updated_at=datetime.utcnow()
        ))

def delete_user(user_id: int):
    # 履歴保護のため無効化
    with get_engine().begin() as conn:
        conn.execute(update(users).where(users.c.id == int(user_id)).values(is_active=False, updated_at=datetime.utcnow()))

# 健康チェック
def list_health_records(start_date=None, end_date=None, user_id=None, keyword: str = "") -> pd.DataFrame:
    stmt = (
        select(
            health_records.c.id, health_records.c.record_date, health_records.c.user_id,
            users.c.user_code, users.c.user_name, users.c.room,
            health_records.c.temperature, health_records.c.blood_pressure_high, health_records.c.blood_pressure_low,
            health_records.c.pulse, health_records.c.spo2, health_records.c.weight,
            health_records.c.meal_rate, health_records.c.water_amount,
            health_records.c.family_memo, health_records.c.staff_memo, health_records.c.staff_name,
            health_records.c.created_at, health_records.c.updated_at,
        ).select_from(health_records.join(users, health_records.c.user_id == users.c.id))
        .order_by(health_records.c.record_date.desc(), users.c.user_code)
    )
    conds = []
    if start_date:
        conds.append(health_records.c.record_date >= _to_date(start_date))
    if end_date:
        conds.append(health_records.c.record_date <= _to_date(end_date))
    if user_id:
        conds.append(health_records.c.user_id == int(user_id))
    if keyword:
        kw = f"%{keyword}%"
        conds.append(or_(users.c.user_name.like(kw), users.c.user_code.like(kw), users.c.room.like(kw)))
    if conds:
        stmt = stmt.where(and_(*conds))
    with get_engine().begin() as conn:
        rows = conn.execute(stmt).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def get_health_record(record_id: int):
    with get_engine().begin() as conn:
        row = conn.execute(select(health_records).where(health_records.c.id == int(record_id))).mappings().first()
    return dict(row) if row else None

def upsert_health_record(record_date, user_id: int, temperature=None, blood_pressure_high=None, blood_pressure_low=None, pulse=None, spo2=None, weight=None, meal_rate=None, water_amount=None, family_memo: str = "", staff_memo: str = "", staff_name: str = ""):
    record_date = _to_date(record_date)
    user_id = int(user_id)
    values = dict(
        record_date=record_date, user_id=user_id, temperature=temperature,
        blood_pressure_high=blood_pressure_high, blood_pressure_low=blood_pressure_low,
        pulse=pulse, spo2=spo2, weight=weight, meal_rate=meal_rate, water_amount=water_amount,
        family_memo=family_memo or None, staff_memo=staff_memo or None, staff_name=staff_name or None,
        updated_at=datetime.utcnow(),
    )
    with get_engine().begin() as conn:
        existing = conn.execute(select(health_records.c.id).where(health_records.c.record_date == record_date, health_records.c.user_id == user_id)).first()
        if existing:
            conn.execute(update(health_records).where(health_records.c.id == existing[0]).values(**values))
            return "updated"
        values["created_at"] = datetime.utcnow()
        conn.execute(insert(health_records).values(**values))
        return "created"

def update_health_record(record_id: int, **kwargs):
    allowed = {"record_date", "user_id", "temperature", "blood_pressure_high", "blood_pressure_low", "pulse", "spo2", "weight", "meal_rate", "water_amount", "family_memo", "staff_memo", "staff_name"}
    values = {k: v for k, v in kwargs.items() if k in allowed}
    if "record_date" in values:
        values["record_date"] = _to_date(values["record_date"])
    values["updated_at"] = datetime.utcnow()
    with get_engine().begin() as conn:
        conn.execute(update(health_records).where(health_records.c.id == int(record_id)).values(**values))

def delete_health_record(record_id: int):
    with get_engine().begin() as conn:
        conn.execute(delete(health_records).where(health_records.c.id == int(record_id)))

def today_input_status(target_date=None) -> pd.DataFrame:
    target_date = _to_date(target_date) or date.today()
    with get_engine().begin() as conn:
        urows = conn.execute(select(users.c.id, users.c.user_code, users.c.user_name, users.c.room).where(users.c.is_active == True).order_by(users.c.user_code)).mappings().all()
        rrows = conn.execute(select(health_records.c.user_id, health_records.c.id).where(health_records.c.record_date == target_date)).mappings().all()
    done = {r["user_id"]: r["id"] for r in rrows}
    data = []
    for u in urows:
        data.append({"利用者コード": u["user_code"], "利用者名": u["user_name"], "居室": u["room"] or "", "入力状況": "入力済み" if u["id"] in done else "未入力", "記録ID": done.get(u["id"], "")})
    return pd.DataFrame(data)

# ダッシュボード用
def list_excretion_records(limit: int = 20) -> pd.DataFrame:
    stmt = select(excretion_records).order_by(excretion_records.c.record_date.desc()).limit(limit)
    with get_engine().begin() as conn:
        rows = conn.execute(stmt).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def list_handovers(limit: int = 20) -> pd.DataFrame:
    stmt = select(handovers).order_by(handovers.c.record_date.desc(), handovers.c.id.desc()).limit(limit)
    with get_engine().begin() as conn:
        rows = conn.execute(stmt).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])
