from __future__ import annotations

from db.connection import get_session
from db.schema import HandoverLog


def create_handover(data: dict) -> HandoverLog:
    session = get_session()
    try:
        row = HandoverLog(**data)
        session.add(row)
        session.commit()
        session.refresh(row)
        return row
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def list_handovers(limit: int = 200):
    session = get_session()
    try:
        rows = session.query(HandoverLog).order_by(HandoverLog.record_date.desc(), HandoverLog.created_at.desc()).limit(limit).all()
        return [
            {
                "日付": r.record_date,
                "勤務帯": r.shift,
                "記入者": r.writer,
                "事実": r.fact_text,
                "気づき": r.notice_text,
                "次に見ること": r.next_watch_text,
                "優先度": r.priority,
                "状態": r.status,
                "記録日時": r.created_at,
            }
            for r in rows
        ]
    finally:
        session.close()
