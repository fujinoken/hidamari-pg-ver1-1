from __future__ import annotations

from db.connection import get_session
from db.schema import AuditLog


def add_audit_log(login_id: str, role: str, action: str, target_table: str = "", target_id: str = "", summary: str = "", before_text: str = "", after_text: str = "") -> None:
    session = get_session()
    try:
        session.add(AuditLog(
            login_id=login_id or "",
            role=role or "",
            action=action,
            target_table=target_table,
            target_id=str(target_id or ""),
            summary=summary or "",
            before_text=before_text or "",
            after_text=after_text or "",
        ))
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


def list_audit_logs(limit: int = 300):
    session = get_session()
    try:
        rows = session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
        return [
            {
                "日時": r.created_at,
                "ログインID": r.login_id,
                "権限": r.role,
                "操作": r.action,
                "対象": r.target_table,
                "対象ID": r.target_id,
                "概要": r.summary,
            }
            for r in rows
        ]
    finally:
        session.close()
