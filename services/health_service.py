from __future__ import annotations
import uuid
from datetime import date
import pandas as pd
from sqlalchemy import text
from db.migrations import get_engine
from config.settings import DEFAULT_FACILITY_ID

def create_user(user_name: str, room: str = "", user_code: str | None = None):
    user_name = (user_name or "").strip()
    room = (room or "").strip()
    if not user_name:
        raise ValueError("利用者名を入力してください。")
    user_id = str(uuid.uuid4())
    if not user_code:
        user_code = user_id[:8]
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO users (id, facility_id, user_code, user_name, room, is_active)
            VALUES (:id, :facility_id, :user_code, :user_name, :room, TRUE)
        """), {
            "id": user_id,
            "facility_id": DEFAULT_FACILITY_ID,
            "user_code": user_code,
            "user_name": user_name,
            "room": room,
        })
    return user_id

def list_users(active_only=True):
    engine = get_engine()
    where = "WHERE COALESCE(is_active, TRUE) = TRUE" if active_only else ""
    with engine.begin() as conn:
        rows = conn.execute(text(f"""
            SELECT CAST(id AS TEXT) AS id,
                   COALESCE(user_code, CAST(id AS TEXT)) AS user_code,
                   COALESCE(user_name, '') AS user_name,
                   COALESCE(room, '') AS room,
                   COALESCE(is_active, TRUE) AS is_active
            FROM users
            {where}
            ORDER BY user_name
        """)).mappings().all()
    return [dict(r) for r in rows]

def get_user_options():
    users = list_users(True)
    return {f"{u['user_name']}（{u.get('room') or '居室未設定'}）": u["id"] for u in users}

def save_health_record(
    user_id: str,
    record_date: date,
    temperature=None,
    blood_pressure_high=None,
    blood_pressure_low=None,
    pulse=None,
    spo2=None,
    weight=None,
    meal_rate=None,
    memo: str = "",
):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO health_records
            (facility_id, user_id, record_date, temperature, blood_pressure_high,
             blood_pressure_low, pulse, spo2, weight, meal_rate, memo, updated_at)
            VALUES
            (:facility_id, :user_id, :record_date, :temperature, :blood_pressure_high,
             :blood_pressure_low, :pulse, :spo2, :weight, :meal_rate, :memo, CURRENT_TIMESTAMP)
        """), {
            "facility_id": DEFAULT_FACILITY_ID,
            "user_id": str(user_id),
            "record_date": record_date,
            "temperature": temperature,
            "blood_pressure_high": blood_pressure_high,
            "blood_pressure_low": blood_pressure_low,
            "pulse": pulse,
            "spo2": spo2,
            "weight": weight,
            "meal_rate": meal_rate,
            "memo": memo,
        })

def update_health_record(record_id: int, **kwargs):
    allowed = [
        "record_date", "temperature", "blood_pressure_high", "blood_pressure_low",
        "pulse", "spo2", "weight", "meal_rate", "memo"
    ]
    sets = []
    params = {"id": int(record_id)}
    for k in allowed:
        if k in kwargs:
            sets.append(f"{k} = :{k}")
            params[k] = kwargs[k]
    if not sets:
        return
    sets.append("updated_at = CURRENT_TIMESTAMP")
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"UPDATE health_records SET {', '.join(sets)} WHERE id = :id"), params)

def delete_health_record(record_id: int):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM health_records WHERE id = :id"), {"id": int(record_id)})

def list_health_records(keyword: str = "", start_date=None, end_date=None, limit: int = 200):
    engine = get_engine()
    conditions = []
    params = {"limit": int(limit)}
    if keyword:
        conditions.append("u.user_name ILIKE :kw")
        params["kw"] = f"%{keyword}%"
    if start_date:
        conditions.append("h.record_date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        conditions.append("h.record_date <= :end_date")
        params["end_date"] = end_date
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = f"""
        SELECT h.id,
               h.record_date,
               CAST(h.user_id AS TEXT) AS user_id,
               COALESCE(u.user_name, CAST(h.user_id AS TEXT)) AS user_name,
               COALESCE(u.room, '') AS room,
               h.temperature,
               h.blood_pressure_high,
               h.blood_pressure_low,
               h.pulse,
               h.spo2,
               h.weight,
               h.meal_rate,
               h.memo
        FROM health_records h
        LEFT JOIN users u ON CAST(u.id AS TEXT) = CAST(h.user_id AS TEXT)
        {where}
        ORDER BY h.record_date DESC, h.id DESC
        LIMIT :limit
    """
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def today_input_status(target_date: date):
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT CAST(u.id AS TEXT) AS user_id,
                   u.user_name,
                   COALESCE(u.room, '') AS room,
                   CASE WHEN h.id IS NULL THEN '未入力' ELSE '入力済み' END AS status
            FROM users u
            LEFT JOIN health_records h
              ON CAST(u.id AS TEXT) = CAST(h.user_id AS TEXT)
             AND h.record_date = :target_date
            WHERE COALESCE(u.is_active, TRUE) = TRUE
            ORDER BY u.user_name
        """), {"target_date": target_date}).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])
