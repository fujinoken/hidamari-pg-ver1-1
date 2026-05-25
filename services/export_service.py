
from __future__ import annotations
from io import StringIO
import pandas as pd
from sqlalchemy import select
from db.connection import get_engine
from db.schema import health_records, excretion_records, handover_logs, users, audit_logs
from config.settings import DEFAULT_FACILITY_ID
from utils.time_utils import format_now_jst

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

def export_table_df(table_name: str) -> pd.DataFrame:
    table_map = {
        "health_records": health_records,
        "excretion_records": excretion_records,
        "handover_logs": handover_logs,
        "users": users,
        "audit_logs": audit_logs,
    }
    table = table_map[table_name]
    with get_engine().begin() as conn:
        rows = conn.execute(select(table).where(table.c.facility_id == DEFAULT_FACILITY_ID).limit(10000)).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def csv_filename(table_name: str) -> str:
    return f"{table_name}_{format_now_jst('%Y%m%d_%H%M%S')}.csv"
