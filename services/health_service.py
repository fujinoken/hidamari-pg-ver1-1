import pandas as pd
from sqlalchemy import text
from db.migrations import get_engine


def _rows(sql, params=None):
    with get_engine().begin() as conn:
        return [dict(r) for r in conn.execute(text(sql), params or {}).mappings().all()]


def add_health_record(data: dict):
    sql = """
    INSERT INTO health_records
    (facility_id, user_id, user_name, record_date, temperature, blood_pressure_high, blood_pressure_low,
     pulse, spo2, weight, meal_rate, memo, created_by)
    VALUES
    (:facility_id, :user_id, :user_name, :record_date, :temperature, :blood_pressure_high, :blood_pressure_low,
     :pulse, :spo2, :weight, :meal_rate, :memo, :created_by)
    """
    with get_engine().begin() as conn:
        conn.execute(text(sql), data)


def list_health_records(limit=50):
    return _rows("SELECT * FROM health_records ORDER BY record_date DESC, id DESC LIMIT :limit", {"limit": limit})


def add_excretion_record(data: dict):
    sql = """
    INSERT INTO excretion_records
    (facility_id, user_id, user_name, record_date, urination, defecation, memo, created_by)
    VALUES
    (:facility_id, :user_id, :user_name, :record_date, :urination, :defecation, :memo, :created_by)
    """
    with get_engine().begin() as conn:
        conn.execute(text(sql), data)


def list_excretion_records(limit=50):
    return _rows("SELECT * FROM excretion_records ORDER BY record_date DESC, id DESC LIMIT :limit", {"limit": limit})


def add_handover_record(data: dict):
    sql = """
    INSERT INTO handover_records
    (facility_id, record_date, shift, content, created_by)
    VALUES
    (:facility_id, :record_date, :shift, :content, :created_by)
    """
    with get_engine().begin() as conn:
        conn.execute(text(sql), data)


def list_handover_records(limit=50):
    return _rows("SELECT * FROM handover_records ORDER BY record_date DESC, id DESC LIMIT :limit", {"limit": limit})


def to_dataframe(records):
    return pd.DataFrame(records) if records else pd.DataFrame()
