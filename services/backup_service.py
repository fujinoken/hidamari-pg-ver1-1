from __future__ import annotations

from io import BytesIO
import zipfile
import pandas as pd
from sqlalchemy import text
from db.connection import get_engine
from utils.time_utils import format_now_jst

CORE_TABLES = [
    "facilities",
    "staff_accounts",
    "users",
    "health_records",
    "excretion_records",
    "handover_logs",
    "audit_logs",
]


def create_export_zip() -> bytes:
    """PostgreSQL版のバックアップ方針：DBの論理CSVエクスポートZIPを作る。"""
    engine = get_engine()
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest = ["ひだまり PostgreSQL版 論理バックアップ", f"作成日時: {format_now_jst()}", ""]
        with engine.connect() as conn:
            for table in CORE_TABLES:
                df = pd.read_sql(text(f"SELECT * FROM {table}"), conn)
                csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
                zf.writestr(f"csv/{table}.csv", csv_bytes)
                manifest.append(f"{table}: {len(df)} rows")
        zf.writestr("manifest.txt", "\n".join(manifest))
    return buffer.getvalue()
