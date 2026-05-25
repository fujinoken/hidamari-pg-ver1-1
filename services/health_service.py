from __future__ import annotations
import uuid
import pandas as pd
from sqlalchemy import text
from db.connection import engine
from config.settings import DEFAULT_FACILITY_ID


def _fetch_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params or {}).mappings().all()
    return pd.DataFrame(rows)


def list_users(active_only: bool = True) -> pd.DataFrame:
    sql = "SELECT id, user_name, user_code, kana, is_active FROM users WHERE facility_id=:fid"
    if active_only:
        sql += " AND is_active = TRUE"
    sql += " ORDER BY user_name"
    return _fetch_df(sql, {"fid": DEFAULT_FACILITY_ID})


def create_user(user_name: str, user_code: str = "", kana: str = ""):
    user_name = (user_name or "").strip()
    if not user_name:
        raise ValueError("利用者名を入力してください。")
    user_id = str(uuid.uuid4())
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO users (id, facility_id, user_code, user_name, kana, is_active)
            VALUES (:id, :fid, :code, :name, :kana, TRUE)
        """), {"id": user_id, "fid": DEFAULT_FACILITY_ID, "code": user_code, "name": user_name, "kana": kana})
    return user_id


def save_health_record(data: dict):
    rec_id = data.get("id") or str(uuid.uuid4())
    params = {
        "id": rec_id,
        "fid": DEFAULT_FACILITY_ID,
        "user_id": data["user_id"],
        "record_date": data["record_date"],
        "temperature": data.get("temperature"),
        "bp_high": data.get("bp_high"),
        "bp_low": data.get("bp_low"),
        "pulse": data.get("pulse"),
        "spo2": data.get("spo2"),
        "weight": data.get("weight"),
        "meal_rate": data.get("meal_rate"),
        "memo": data.get("memo", ""),
    }
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO health_records
            (id, facility_id, user_id, record_date, temperature, bp_high, bp_low, pulse, spo2, weight, meal_rate, memo)
            VALUES (:id, :fid, :user_id, :record_date, :temperature, :bp_high, :bp_low, :pulse, :spo2, :weight, :meal_rate, :memo)
            ON CONFLICT (facility_id, user_id, record_date) DO UPDATE SET
                temperature=EXCLUDED.temperature,
                bp_high=EXCLUDED.bp_high,
                bp_low=EXCLUDED.bp_low,
                pulse=EXCLUDED.pulse,
                spo2=EXCLUDED.spo2,
                weight=EXCLUDED.weight,
                meal_rate=EXCLUDED.meal_rate,
                memo=EXCLUDED.memo,
                updated_at=CURRENT_TIMESTAMP
        """), params)
    return rec_id


def update_health_record(record_id: str, data: dict):
    params = {"id": record_id, **data}
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE health_records SET
                record_date=:record_date,
                user_id=:user_id,
                temperature=:temperature,
                bp_high=:bp_high,
                bp_low=:bp_low,
                pulse=:pulse,
                spo2=:spo2,
                weight=:weight,
                meal_rate=:meal_rate,
                memo=:memo,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=:id
        """), params)


def delete_health_record(record_id: str):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM health_records WHERE id=:id"), {"id": record_id})


def list_health_records(start_date: str | None = None, end_date: str | None = None, user_id: str | None = None) -> pd.DataFrame:
    sql = """
        SELECT h.id, h.record_date, h.user_id, u.user_name,
               h.temperature, h.bp_high, h.bp_low, h.pulse, h.spo2, h.weight, h.meal_rate, h.memo
        FROM health_records h
        LEFT JOIN users u ON CAST(h.user_id AS TEXT)=CAST(u.id AS TEXT)
        WHERE h.facility_id=:fid
    """
    params = {"fid": DEFAULT_FACILITY_ID}
    if start_date:
        sql += " AND h.record_date >= :start_date"
        params["start_date"] = start_date
    if end_date:
        sql += " AND h.record_date <= :end_date"
        params["end_date"] = end_date
    if user_id:
        sql += " AND CAST(h.user_id AS TEXT)=CAST(:user_id AS TEXT)"
        params["user_id"] = user_id
    sql += " ORDER BY h.record_date DESC, u.user_name"
    return _fetch_df(sql, params)


def today_input_status(target_date: str) -> pd.DataFrame:
    return _fetch_df("""
        SELECT u.id AS user_id, u.user_name,
               CASE WHEN h.id IS NULL THEN '未入力' ELSE '入力済み' END AS 入力状況,
               h.record_date AS 記録日
        FROM users u
        LEFT JOIN health_records h
          ON CAST(u.id AS TEXT)=CAST(h.user_id AS TEXT)
         AND h.record_date = :target_date
         AND h.facility_id = :fid
        WHERE u.facility_id=:fid AND u.is_active = TRUE
        ORDER BY u.user_name
    """, {"fid": DEFAULT_FACILITY_ID, "target_date": target_date})
