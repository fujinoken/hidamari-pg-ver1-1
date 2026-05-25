
from __future__ import annotations
import uuid, json
from sqlalchemy import insert
from db.connection import get_engine
from db.schema import audit_logs
from config.settings import DEFAULT_FACILITY_ID

def add_audit_log(login_id: str = "", role: str = "", action: str = "", target_table: str = "", target_id: str = "", summary: str = "", before=None, after=None, facility_id: str = DEFAULT_FACILITY_ID):
    try:
        def dumps(v):
            if v is None:
                return ""
            try:
                return json.dumps(v, ensure_ascii=False, default=str)
            except Exception:
                return str(v)
        with get_engine().begin() as conn:
            conn.execute(insert(audit_logs).values(
                id=str(uuid.uuid4()),
                facility_id=facility_id,
                login_id=login_id or "",
                role=role or "",
                action=action or "",
                target_table=target_table or "",
                target_id=target_id or "",
                summary=summary or "",
                before_json=dumps(before),
                after_json=dumps(after),
            ))
    except Exception:
        pass
