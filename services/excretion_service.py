from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert
from db.connection import get_session
from db.schema import ExcretionRecord, User


def upsert_excretion_record(data: dict) -> None:
    session = get_session()
    try:
        stmt = insert(ExcretionRecord).values(**data)
        update_cols = {c.name: getattr(stmt.excluded, c.name) for c in ExcretionRecord.__table__.columns if c.name not in ["id", "created_at"]}
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
        return [
            {
                "記録日": r.record_date,
                "利用者名": u.display_name,
                "時間帯": r.slot,
                "尿量": r.urine_amount,
                "尿性状": r.urine_type,
                "便量": r.stool_amount,
                "便性状": r.stool_type,
                "メモ": r.memo,
                "入力者": r.input_by,
                "登録日時": r.created_at,
            }
            for r, u in rows
        ]
    finally:
        session.close()
