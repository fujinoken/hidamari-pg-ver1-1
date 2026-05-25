from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert
from db.connection import get_session
from db.schema import ExcretionRecord, User


def excretion_record_to_dict(record: ExcretionRecord, user_name: str = "") -> dict:
    return {
        "ID": record.id,
        "記録日": record.record_date,
        "利用者名": user_name,
        "時間帯": record.slot,
        "尿量": record.urine_amount,
        "尿性状": record.urine_type,
        "便量": record.stool_amount,
        "便性状": record.stool_type,
        "メモ": record.memo,
        "入力者": record.input_by,
        "登録日時": record.created_at,
        "更新日時": record.updated_at,
    }


def upsert_excretion_record(data: dict) -> None:
    session = get_session()
    try:
        stmt = insert(ExcretionRecord).values(**data)
        update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in ExcretionRecord.__table__.columns
            if c.name not in ["id", "created_at"]
        }
        stmt = stmt.on_conflict_do_update(
            constraint="uq_excretion_date_user_slot",
            set_=update_cols,
        )
        session.execute(stmt)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def list_excretion_records(limit: int = 300):
    session = get_session()
    try:
        rows = (
            session.query(ExcretionRecord, User)
            .join(User, ExcretionRecord.user_id == User.id)
            .order_by(ExcretionRecord.record_date.desc(), User.display_name.asc(), ExcretionRecord.slot.asc())
            .limit(limit)
            .all()
        )
        return [excretion_record_to_dict(r, u.display_name) for r, u in rows]
    finally:
        session.close()


def search_excretion_records(user_id: int | None = None, date_from=None, date_to=None, keyword: str = "", limit: int = 500):
    session = get_session()
    try:
        q = session.query(ExcretionRecord, User).join(User, ExcretionRecord.user_id == User.id)
        if user_id:
            q = q.filter(ExcretionRecord.user_id == user_id)
        if date_from:
            q = q.filter(ExcretionRecord.record_date >= date_from)
        if date_to:
            q = q.filter(ExcretionRecord.record_date <= date_to)
        if keyword:
            like = f"%{keyword}%"
            q = q.filter((ExcretionRecord.memo.ilike(like)) | (ExcretionRecord.input_by.ilike(like)))
        rows = q.order_by(ExcretionRecord.record_date.desc(), User.display_name.asc(), ExcretionRecord.slot.asc()).limit(limit).all()
        return [excretion_record_to_dict(r, u.display_name) for r, u in rows]
    finally:
        session.close()


def get_excretion_record(record_id: int) -> dict | None:
    session = get_session()
    try:
        row = (
            session.query(ExcretionRecord, User)
            .join(User, ExcretionRecord.user_id == User.id)
            .filter(ExcretionRecord.id == record_id)
            .first()
        )
        if not row:
            return None
        r, u = row
        return excretion_record_to_dict(r, u.display_name)
    finally:
        session.close()


def update_excretion_record(record_id: int, data: dict) -> None:
    session = get_session()
    try:
        record = session.query(ExcretionRecord).filter(ExcretionRecord.id == record_id).first()
        if not record:
            raise ValueError("対象の排泄記録が見つかりません。")
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_excretion_record(record_id: int) -> None:
    session = get_session()
    try:
        record = session.query(ExcretionRecord).filter(ExcretionRecord.id == record_id).first()
        if not record:
            raise ValueError("対象の排泄記録が見つかりません。")
        session.delete(record)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
