from __future__ import annotations
from sqlalchemy import text
from db.connection import get_engine
import uuid
from datetime import date

def _new_id() -> str:
    return uuid.uuid4().hex

def add_user(facility_id: str, user_name: str, user_code: str = "", room: str = ""):
    engine = get_engine()
    with engine.begin() as conn:
        user_id = _new_id()
        conn.execute(text("""
            INSERT INTO users (id, facility_id, user_code, user_name, room, is_active)
            VALUES (:id, :facility_id, :user_code, :user_name, :room, TRUE)
        """), {
            "id": user_id, "facility_id": facility_id, "user_code": user_code,
            "user_name": user_name, "room": room
        })
        return user_id

def list_users(facility_id: str, active_only: bool = True):
    engine = get_engine()
    where = "WHERE CAST(facility_id AS TEXT) = :facility_id"
    if active_only:
        where += " AND (is_active = TRUE OR is_active = 1)"
    with engine.begin() as conn:
        rows = conn.execute(text(f"""
            SELECT CAST(id AS TEXT) AS id, COALESCE(user_code, '') AS user_code,
                   COALESCE(user_name, '') AS user_name, COALESCE(room, '') AS room,
                   is_active
            FROM users
            {where}
            ORDER BY user_name
        """), {"facility_id": facility_id}).mappings().all()
        return [dict(r) for r in rows]

def deactivate_user(user_id: str):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("UPDATE users SET is_active = FALSE WHERE CAST(id AS TEXT) = :id"), {"id": str(user_id)})

def save_health_record(facility_id: str, user_id: str, record_date: str, **values):
    engine = get_engine()
    record_id = values.get("id") or _new_id()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO health_records (
                id, facility_id, user_id, record_date, temperature,
                blood_pressure_high, blood_pressure_low, pulse, spo2,
                weight, meal_rate, memo
            ) VALUES (
                :id, :facility_id, :user_id, :record_date, :temperature,
                :blood_pressure_high, :blood_pressure_low, :pulse, :spo2,
                :weight, :meal_rate, :memo
            )
        """), {
            "id": record_id, "facility_id": facility_id, "user_id": str(user_id),
            "record_date": str(record_date),
            "temperature": values.get("temperature"),
            "blood_pressure_high": values.get("blood_pressure_high"),
            "blood_pressure_low": values.get("blood_pressure_low"),
            "pulse": values.get("pulse"),
            "spo2": values.get("spo2"),
            "weight": values.get("weight"),
            "meal_rate": values.get("meal_rate"),
            "memo": values.get("memo", ""),
        })
        return record_id

def update_health_record(record_id: str, **values):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE health_records SET
                record_date = :record_date,
                user_id = :user_id,
                temperature = :temperature,
                blood_pressure_high = :blood_pressure_high,
                blood_pressure_low = :blood_pressure_low,
                pulse = :pulse,
                spo2 = :spo2,
                weight = :weight,
                meal_rate = :meal_rate,
                memo = :memo,
                updated_at = CURRENT_TIMESTAMP
            WHERE CAST(id AS TEXT) = :id
        """), {
            "id": str(record_id),
            "record_date": str(values.get("record_date")),
            "user_id": str(values.get("user_id")),
            "temperature": values.get("temperature"),
            "blood_pressure_high": values.get("blood_pressure_high"),
            "blood_pressure_low": values.get("blood_pressure_low"),
            "pulse": values.get("pulse"),
            "spo2": values.get("spo2"),
            "weight": values.get("weight"),
            "meal_rate": values.get("meal_rate"),
            "memo": values.get("memo", ""),
        })

def delete_health_record(record_id: str):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM health_records WHERE CAST(id AS TEXT) = :id"), {"id": str(record_id)})

def list_health_records(facility_id: str, start_date: str | None = None, end_date: str | None = None, user_id: str | None = None, keyword: str | None = None, limit: int = 200):
    engine = get_engine()
    sql = """
        SELECT
            CAST(h.id AS TEXT) AS id,
            CAST(h.user_id AS TEXT) AS user_id,
            h.record_date,
            COALESCE(u.user_name, '') AS user_name,
            COALESCE(u.room, '') AS room,
            h.temperature,
            h.blood_pressure_high,
            h.blood_pressure_low,
            h.pulse,
            h.spo2,
            h.weight,
            h.meal_rate,
            COALESCE(h.memo, '') AS memo
        FROM health_records h
        LEFT JOIN users u ON CAST(h.user_id AS TEXT) = CAST(u.id AS TEXT)
        WHERE CAST(h.facility_id AS TEXT) = :facility_id
    """
    params = {"facility_id": facility_id, "limit": limit}
    if start_date:
        sql += " AND CAST(h.record_date AS TEXT) >= :start_date"
        params["start_date"] = str(start_date)
    if end_date:
        sql += " AND CAST(h.record_date AS TEXT) <= :end_date"
        params["end_date"] = str(end_date)
    if user_id:
        sql += " AND CAST(h.user_id AS TEXT) = :user_id"
        params["user_id"] = str(user_id)
    if keyword:
        sql += " AND (COALESCE(u.user_name, '') LIKE :kw OR COALESCE(h.memo, '') LIKE :kw)"
        params["kw"] = f"%{keyword}%"
    sql += " ORDER BY CAST(h.record_date AS TEXT) DESC, user_name ASC LIMIT :limit"
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]

def get_health_record(record_id: str):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT CAST(id AS TEXT) AS id, CAST(user_id AS TEXT) AS user_id,
                   record_date, temperature, blood_pressure_high, blood_pressure_low,
                   pulse, spo2, weight, meal_rate, COALESCE(memo, '') AS memo
            FROM health_records
            WHERE CAST(id AS TEXT) = :id
        """), {"id": str(record_id)}).mappings().first()
        return dict(row) if row else None

def today_input_status(facility_id: str, target_date: str):
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT
                CAST(u.id AS TEXT) AS user_id,
                u.user_name,
                u.room,
                CASE WHEN h.id IS NULL THEN '未入力' ELSE '入力済み' END AS status
            FROM users u
            LEFT JOIN health_records h
              ON CAST(u.id AS TEXT) = CAST(h.user_id AS TEXT)
             AND CAST(h.record_date AS TEXT) = :target_date
             AND CAST(h.facility_id AS TEXT) = :facility_id
            WHERE CAST(u.facility_id AS TEXT) = :facility_id
              AND (u.is_active = TRUE OR u.is_active = 1)
            ORDER BY u.user_name
        """), {"facility_id": facility_id, "target_date": str(target_date)}).mappings().all()
        return [dict(r) for r in rows]
