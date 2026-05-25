
from __future__ import annotations
from sqlalchemy import text, select
from db.connection import get_engine
from db.schema import backup_logs
from config.settings import DEFAULT_FACILITY_ID
from utils.time_utils import format_now_jst
from services.audit_service import add_audit_log
import uuid, json

def create_logical_backup_summary(actor: dict) -> dict:
    table_names = ["facilities","staff_accounts","users","health_records","excretion_records","handover_logs","audit_logs"]
    summary = {}
    with get_engine().begin() as conn:
        for t in table_names:
            try:
                cnt = conn.execute(text(f"SELECT COUNT(*) FROM {t} WHERE facility_id = :fid") if t not in ["facilities"] else text(f"SELECT COUNT(*) FROM {t}"), {"fid": DEFAULT_FACILITY_ID}).scalar()
            except Exception:
                cnt = 0
            summary[t] = int(cnt or 0)
        bid = str(uuid.uuid4())
        conn.execute(backup_logs.insert().values(
            id=bid,
            facility_id=DEFAULT_FACILITY_ID,
            backup_type="logical_summary",
            summary=json.dumps(summary, ensure_ascii=False),
            created_by=actor.get("login_id",""),
        ))
    add_audit_log(actor.get("login_id",""), actor.get("role",""), "論理バックアップ記録", "backup_logs", bid, after=summary)
    return {"backup_id": bid, "created_at": format_now_jst(), "summary": summary}
