from datetime import date
import pandas as pd
from sqlalchemy import text
from db.migrations import get_engine
from config.settings import DEFAULT_FACILITY_ID

def save_excretion_record(user_id, record_date: date, urination="", defecation="", memo=""):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO excretion_records
            (facility_id, user_id, record_date, urination, defecation, memo)
            VALUES (:facility_id, :user_id, :record_date, :urination, :defecation, :memo)
        """), {
            "facility_id": DEFAULT_FACILITY_ID,
            "user_id": str(user_id),
            "record_date": record_date,
            "urination": urination,
            "defecation": defecation,
            "memo": memo,
        })

def list_excretion_records(limit=100):
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT e.id, e.record_date, COALESCE(u.user_name, CAST(e.user_id AS TEXT)) AS user_name,
                   e.urination, e.defecation, e.memo
            FROM excretion_records e
            LEFT JOIN users u ON CAST(u.id AS TEXT) = CAST(e.user_id AS TEXT)
            ORDER BY e.record_date DESC, e.id DESC
            LIMIT :limit
        """), {"limit": int(limit)}).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])
