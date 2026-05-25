from __future__ import annotations

from db.connection import get_session
from db.schema import HandoverLog


def handover_to_dict(record: HandoverLog) -> dict:
    return {
        "ID": record.id,
        "日付": record.record_date,
        "勤務帯": record.shift,
        "記入者": record.writer,
        "事実": record.fact_text,
        "気づき": record.notice_text,
        "次に見ること": record.next_watch_text,
        "優先度": record.priority,
        "状態": record.status,
        "記録日時": record.created_at,
        "更新日時": record.updated_at,
    }


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
        return [handover_to_dict(r) for r in rows]
    finally:
        session.close()


def search_handovers(date_from=None, date_to=None, keyword: str = "", shift: str = "", limit: int = 500):
    session = get_session()
    try:
        q = session.query(HandoverLog)
        if date_from:
            q = q.filter(HandoverLog.record_date >= date_from)
        if date_to:
            q = q.filter(HandoverLog.record_date <= date_to)
        if shift:
            q = q.filter(HandoverLog.shift == shift)
        if keyword:
            like = f"%{keyword}%"
            q = q.filter(
                (HandoverLog.writer.ilike(like))
                | (HandoverLog.fact_text.ilike(like))
                | (HandoverLog.notice_text.ilike(like))
                | (HandoverLog.next_watch_text.ilike(like))
                | (HandoverLog.status.ilike(like))
                | (HandoverLog.priority.ilike(like))
            )
        rows = q.order_by(HandoverLog.record_date.desc(), HandoverLog.created_at.desc()).limit(limit).all()
        return [handover_to_dict(r) for r in rows]
    finally:
        session.close()


def get_handover(record_id: int) -> dict | None:
    session = get_session()
    try:
        record = session.query(HandoverLog).filter(HandoverLog.id == record_id).first()
        if not record:
            return None
        return handover_to_dict(record)
    finally:
        session.close()


def update_handover(record_id: int, data: dict) -> None:
    session = get_session()
    try:
        record = session.query(HandoverLog).filter(HandoverLog.id == record_id).first()
        if not record:
            raise ValueError("対象の申し送りが見つかりません。")
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_handover(record_id: int) -> None:
    session = get_session()
    try:
        record = session.query(HandoverLog).filter(HandoverLog.id == record_id).first()
        if not record:
            raise ValueError("対象の申し送りが見つかりません。")
        session.delete(record)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
